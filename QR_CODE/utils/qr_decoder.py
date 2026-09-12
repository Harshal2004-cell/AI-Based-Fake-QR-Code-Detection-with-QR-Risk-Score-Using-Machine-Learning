import cv2
import numpy as np
from PIL import Image

try:
    import zxingcpp
except ImportError:
    zxingcpp = None


def _as_bgr(image_input):
    if isinstance(image_input, Image.Image):
        arr = np.array(image_input.convert("RGB"))
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    if isinstance(image_input, np.ndarray):
        img = image_input.copy()
        if img.ndim == 2:
            return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        if img.ndim == 3 and img.shape[2] == 4:
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    return None


def _decode_opencv(detector, candidate):
    try:
        data, points, _ = detector.detectAndDecode(candidate)
        if data and data.strip():
            return data.strip()
    except Exception:
        pass

    try:
        ok, decoded_info, points, _ = detector.detectAndDecodeMulti(candidate)
        if ok and decoded_info:
            for text in decoded_info:
                if text and text.strip():
                    return text.strip()
    except Exception:
        pass

    return None


def _perspective_candidates(img):
    """
    Generate practical perspective/angle variants.

    OpenCV/ZXing decode normal 2D QR symbols. A QR printed/placed on a
    3D object can still be decoded when the visible QR remains sufficiently
    planar/readable; there is no generic '3D QR' standard decoder here.
    """
    candidates = [img]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Improve difficult lighting / mild blur.
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    candidates += [
        gray,
        enhanced,
        cv2.GaussianBlur(enhanced, (3, 3), 0),
        cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 31, 5
        ),
        cv2.threshold(
            enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )[1],
    ]

    h, w = img.shape[:2]

    # Full frame + overlapping crops for a QR that is small/far away.
    boxes = [
        (0, 0, w, h),
        (int(.05*w), int(.05*h), int(.95*w), int(.95*h)),
        (0, 0, int(.78*w), int(.78*h)),
        (int(.22*w), 0, w, int(.78*h)),
        (0, int(.22*h), int(.78*w), h),
        (int(.22*w), int(.22*h), w, h),
    ]

    for x1, y1, x2, y2 in boxes:
        crop = img[y1:y2, x1:x2]
        if crop.size:
            candidates.append(crop)

    # Rotations handle QR photos taken in different orientations.
    base = list(candidates)
    for candidate in base:
        if candidate is None or candidate.size == 0:
            continue
        candidates.append(cv2.rotate(candidate, cv2.ROTATE_90_CLOCKWISE))
        candidates.append(cv2.rotate(candidate, cv2.ROTATE_180))
        candidates.append(cv2.rotate(candidate, cv2.ROTATE_90_COUNTERCLOCKWISE))

    return candidates


def decode_qr(image_input):
    """
    Robust QR decoder for:
      - mobile camera captures
      - uploaded/gallery images
      - rotated QR photos
      - QR embedded in larger photos
      - difficult lighting and mild blur

    Uses OpenCV QRCodeDetector first and ZXing-C++ as fallback.
    """
    if image_input is None:
        return None

    img = _as_bgr(image_input)
    if img is None:
        return None

    # Keep enough detail but prevent huge mobile photos from exhausting memory.
    h, w = img.shape[:2]
    if max(h, w) > 2400:
        scale = 2400.0 / max(h, w)
        img = cv2.resize(
            img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA
        )

    detector = cv2.QRCodeDetector()
    candidates = _perspective_candidates(img)

    # Try each candidate directly, then enlarge small candidates.
    for candidate in candidates:
        if candidate is None or candidate.size == 0:
            continue

        payload = _decode_opencv(detector, candidate)
        if payload:
            return payload

        ch, cw = candidate.shape[:2]
        if max(ch, cw) < 1800:
            for scale in (1.5, 2.0):
                try:
                    enlarged = cv2.resize(
                        candidate, None, fx=scale, fy=scale,
                        interpolation=cv2.INTER_CUBIC
                    )
                    payload = _decode_opencv(detector, enlarged)
                    if payload:
                        return payload
                except Exception:
                    pass

    # ZXing-C++ fallback.
    if zxingcpp is not None:
        for candidate in candidates:
            if candidate is None or candidate.size == 0:
                continue
            try:
                results = zxingcpp.read_barcodes(candidate)
                for barcode in results:
                    text = getattr(barcode, "text", "") or ""
                    if text.strip():
                        return text.strip()
            except Exception:
                pass

    return None
