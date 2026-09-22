"""Robust QR decoding for camera frames and uploaded images.

The decoder treats JPG/JPEG/PNG/etc. as *image formats* and decodes the
payload stored inside the QR. Payloads may be UPI, HTTP(S), TEL, SMS,
MAILTO, WIFI, GEO, VCARD or arbitrary text.
"""
import cv2
import numpy as np
from PIL import Image, ImageOps, ImageFilter

try:
    import zxingcpp
except ImportError:
    zxingcpp = None

try:
    from pyzbar.pyzbar import decode as zbar_decode
except Exception:
    zbar_decode = None


def _as_bgr(image_input):
    if isinstance(image_input, Image.Image):
        # Correct EXIF camera orientation before decoding.
        image_input = ImageOps.exif_transpose(image_input).convert("RGB")
        arr = np.array(image_input)
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    if isinstance(image_input, np.ndarray):
        img = image_input.copy()
        if img.ndim == 2:
            return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        if img.ndim == 3 and img.shape[2] == 4:
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    return None


def _texts_from_opencv(detector, candidate):
    out = []
    try:
        data, points, _ = detector.detectAndDecode(candidate)
        if data and data.strip():
            out.append(data.strip())
    except Exception:
        pass

    try:
        ok, decoded_info, points, _ = detector.detectAndDecodeMulti(candidate)
        if ok and decoded_info:
            out.extend(t.strip() for t in decoded_info if t and t.strip())
    except Exception:
        pass
    return out


def _add_unique(candidates, candidate):
    if candidate is None or candidate.size == 0:
        return
    # Avoid generating thousands of duplicate arrays.
    candidates.append(candidate)


def _qr_region_candidates(img):
    """Find likely QR regions in screenshots/photos before decoding."""
    regions = []
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    for threshold in (80, 120, 160, 200):
        _, bw = cv2.threshold(blur, threshold, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(bw, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            area = w * h
            if area < img.shape[0] * img.shape[1] * 0.025:
                continue
            ratio = w / float(h or 1)
            if 0.65 <= ratio <= 1.5:
                pad = int(max(w, h) * 0.08)
                x1, y1 = max(0, x-pad), max(0, y-pad)
                x2, y2 = min(img.shape[1], x+w+pad), min(img.shape[0], y+h+pad)
                regions.append(img[y1:y2, x1:x2])
    return regions[:18]


def _candidates(img):
    candidates = []
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(gray)

    # Keep the first pass intentionally small so mobile/server scans stay fast.
    candidates.extend([img, gray, clahe])
    candidates.extend([
        cv2.threshold(clahe, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        cv2.adaptiveThreshold(clahe, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                              cv2.THRESH_BINARY, 31, 5),
    ])

    h, w = img.shape[:2]
    # Center crop catches QR codes embedded in posters/screenshots.
    for frac in (0.88, 0.70):
        cw, ch = int(w*frac), int(h*frac)
        x, y = (w-cw)//2, (h-ch)//2
        candidates.append(img[y:y+ch, x:x+cw])

    # Add the strongest square-ish contour regions only.
    candidates.extend(_qr_region_candidates(img)[:4])

    # 90/180 rotations are enough for common phone/gallery orientation cases.
    out = []
    for c in candidates:
        if c is None or c.size == 0:
            continue
        out.append(c)
        out.append(cv2.rotate(c, cv2.ROTATE_180))
    return out[:24]


def _logo_recovery_variants(candidate):
    """Try conservative center-logo recovery for branded payment QR images."""
    h, w = candidate.shape[:2]
    cx, cy = w//2, h//2
    variants = []
    for frac in (0.075, 0.10, 0.125):
        r = int(min(w, h) * frac)
        for mode in ("white", "inpaint"):
            x = candidate.copy()
            if mode == "white":
                cv2.circle(x, (cx, cy), r, (255, 255, 255), -1)
            else:
                mask = np.zeros((h, w), dtype=np.uint8)
                cv2.circle(mask, (cx, cy), r, 255, -1)
                x = cv2.inpaint(x, mask, 3, cv2.INPAINT_TELEA)
            variants.append(x)
    return variants


def _try_decode(candidate, detector):
    texts = _texts_from_opencv(detector, candidate)
    if texts:
        return texts[0]

    # Optional decoders: they are used when installed, but the app still works
    # with OpenCV alone.
    if zbar_decode is not None:
        try:
            for item in zbar_decode(candidate):
                text = item.data.decode("utf-8", errors="replace").strip()
                if text:
                    return text
        except Exception:
            pass

    if zxingcpp is not None:
        try:
            for item in zxingcpp.read_barcodes(candidate):
                text = getattr(item, "text", "") or ""
                if text.strip():
                    return text.strip()
        except Exception:
            pass

    return None


def decode_qr(image_input):
    """Decode QR payloads from camera/upload images with multiple fallbacks."""
    if image_input is None:
        return None

    img = _as_bgr(image_input)
    if img is None or img.size == 0:
        return None

    # Preserve detail for QR modules while bounding memory use.
    h, w = img.shape[:2]
    if max(h, w) > 3000:
        scale = 3000.0 / max(h, w)
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    detector = cv2.QRCodeDetector()
    try:
        detector.setUseAlignmentMarkers(True)
        detector.setEpsX(0.2)
        detector.setEpsY(0.2)
    except Exception:
        pass

    candidates = _candidates(img)

    logo_candidates = []
    for candidate in candidates:
        if candidate is None or candidate.size == 0:
            continue

        payload = _try_decode(candidate, detector)
        if payload:
            return payload

        ch, cw = candidate.shape[:2]
        ratio = cw / float(ch or 1)
        if 0.75 <= ratio <= 1.33:
            logo_candidates.append(candidate)

        # One enlargement pass catches small QR codes without making scanning slow.
        if max(ch, cw) < 1200:
            try:
                enlarged = cv2.resize(candidate, None, fx=2.0, fy=2.0,
                                      interpolation=cv2.INTER_CUBIC)
                payload = _try_decode(enlarged, detector)
                if payload:
                    return payload
            except Exception:
                pass

    # Branded/payment QR fallback. Limit this expensive stage to the best
    # square candidates so normal uploads remain fast.
    for candidate in logo_candidates[:4]:
        for recovered in _logo_recovery_variants(candidate):
            payload = _try_decode(recovered, detector)
            if payload:
                return payload

    return None
