import streamlit as st

# Streamlit Components v2 run directly in the page (no iframe), which allows
# browser camera APIs such as getUserMedia() to work reliably on mobile/desktop.
_CAMERA_HTML = r'''
<div class="qr-camera-wrap">
  <video class="qr-camera-video" autoplay playsinline muted></video>
  <canvas class="qr-camera-canvas"></canvas>
  <div class="qr-camera-status">Requesting camera permission…</div>
</div>
'''

_CAMERA_CSS = r'''
.qr-camera-wrap { width: 100%; max-width: 760px; margin: 0 auto; }
.qr-camera-video { width: 100%; max-height: 62vh; object-fit: cover; border-radius: 12px; display: block; background: #111; }
.qr-camera-canvas { display: none; }
.qr-camera-status { padding: 8px 0; font-size: 14px; }
'''

_CAMERA_JS = r'''
export default function(component) {
  const { parentElement, setStateValue } = component;
  const video = parentElement.querySelector('.qr-camera-video');
  const canvas = parentElement.querySelector('.qr-camera-canvas');
  const status = parentElement.querySelector('.qr-camera-status');

  let stream = null;
  let stopped = false;
  let busy = false;
  let timer = null;
  let barcodeDetector = null;
  let jsQR = null;

  const stop = () => {
    stopped = true;
    if (timer) clearTimeout(timer);
    if (stream) stream.getTracks().forEach(t => t.stop());
    stream = null;
  };

  const loadZXing = () => new Promise((resolve) => {
    if (window.ZXingBrowser) { resolve(window.ZXingBrowser); return; }
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/@zxing/browser@0.2.1';
    script.onload = () => resolve(window.ZXingBrowser || null);
    script.onerror = () => resolve(null);
    document.head.appendChild(script);
  });

  const zxingScan = async () => {
    const ZX = await loadZXing();
    if (!ZX || stopped) return false;
    try {
      const reader = new ZX.BrowserQRCodeReader();
      const result = await reader.decodeFromVideoElement(video);
      const text = result && result.getText ? result.getText() : '';
      if (text) { finish(text); return true; }
    } catch (e) {}
    return false;
  };

  const loadJsQR = () => new Promise((resolve) => {
    if (window.jsQR) { resolve(window.jsQR); return; }
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.js';
    script.onload = () => resolve(window.jsQR || null);
    script.onerror = () => resolve(null);
    document.head.appendChild(script);
  });

  const finish = (text) => {
    if (stopped || !text) return;
    stopped = true;
    if (timer) clearTimeout(timer);
    status.textContent = '✅ QR code detected and captured automatically.';
    if (stream) stream.getTracks().forEach(t => t.stop());
    stream = null;
    setStateValue('qr_data', text);
  };

  const jsQrScan = () => {
    if (stopped || busy || !jsQR || video.readyState < 2) {
      if (!stopped) timer = setTimeout(jsQrScan, 180);
      return;
    }
    busy = true;
    try {
      const w = video.videoWidth || 640;
      const h = video.videoHeight || 480;
      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext('2d', {willReadFrequently:true});
      ctx.drawImage(video, 0, 0, w, h);
      let image = ctx.getImageData(0, 0, w, h);
      let code = jsQR(image.data, image.width, image.height, {inversionAttempts:'attemptBoth'});

      // Also inspect a centered crop so QR images displayed on another screen,
      // paper, or inside a larger photo can be detected more easily.
      if (!code) {
        const cropW = Math.floor(w * 0.80);
        const cropH = Math.floor(h * 0.80);
        const sx = Math.floor((w - cropW) / 2);
        const sy = Math.floor((h - cropH) / 2);
        const scale = Math.min(2, 1400 / Math.max(cropW, cropH));
        const cw = Math.max(1, Math.floor(cropW * scale));
        const ch = Math.max(1, Math.floor(cropH * scale));
        const crop = document.createElement('canvas');
        crop.width = cw; crop.height = ch;
        const cctx = crop.getContext('2d', {willReadFrequently:true});
        cctx.imageSmoothingEnabled = false;
        cctx.drawImage(video, sx, sy, cropW, cropH, 0, 0, cw, ch);
        image = cctx.getImageData(0, 0, cw, ch);
        code = jsQR(image.data, image.width, image.height, {inversionAttempts:'attemptBoth'});
      }

      if (code && code.data) { finish(code.data); return; }
    } catch (e) {}
    busy = false;
    if (!stopped) timer = setTimeout(jsQrScan, 180);
  };

  const nativeScan = async () => {
    if (!('BarcodeDetector' in window)) return false;
    try {
      barcodeDetector = new BarcodeDetector({formats:['qr_code']});
    } catch (e) { return false; }

    const loop = async () => {
      if (stopped) return;
      if (!busy && video.readyState >= 2) {
        busy = true;
        try {
          const codes = await barcodeDetector.detect(video);
          if (codes && codes.length && codes[0].rawValue) {
            finish(codes[0].rawValue);
            return;
          }
        } catch (e) {}
        busy = false;
      }
      timer = setTimeout(loop, 120);
    };
    loop();
    return true;
  };

  const start = async () => {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Camera API unavailable');
      }

      // Ask only after the Direct Camera option has been selected.
      stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: {ideal:'environment'},
          width: {ideal:1280},
          height: {ideal:720}
        },
        audio: false
      });

      video.srcObject = stream;
      await video.play();
      status.textContent = '📷 Point the camera at the QR code — it will scan automatically.';

      // ZXing Browser first for stronger QR detection, then native BarcodeDetector, then jsQR.
      const zxing = await zxingScan();
      if (!zxing) {
        const native = await nativeScan();
        if (!native) {
          jsQR = await loadJsQR();
          if (jsQR) jsQrScan();
          else status.textContent = '❌ QR scanner could not load. Please refresh or use Upload Image.';
        }
      }
    } catch (e) {
      status.textContent = '❌ Camera permission was denied or unavailable. Use Upload Image instead.';
    }
  };

  start();

  return () => stop();
}
'''

try:
    _camera_component = st.components.v2.component(
        "auto_qr_camera_v2",
        html=_CAMERA_HTML,
        css=_CAMERA_CSS,
        js=_CAMERA_JS,
    )
except AttributeError:
    _camera_component = None


def auto_qr_camera(key=None):
    """Open the user's device camera and automatically scan QR codes."""
    if _camera_component is None:
        # The project requires a recent Streamlit version (also used by the
        # locked sidebar), so this should only be a defensive fallback.
        return None

    result = _camera_component(
        data={},
        default={"qr_data": None},
        key=key,
        on_qr_data_change=lambda: None,
        height=520,
    )
    return getattr(result, "qr_data", None)
