import base64
import streamlit as st

_HTML = r'''
<div class="qr-image-decoder">
  <img class="qr-image-preview" alt="QR upload preview">
  <div class="qr-image-status">Preparing browser QR decoder…</div>
</div>
'''

_CSS = r'''
.qr-image-decoder { width:100%; }
.qr-image-preview { width:100%; max-height:360px; object-fit:contain; border-radius:14px; background:#0a1320; display:block; }
.qr-image-status { padding:8px 0; color:#61758c; font-weight:600; font-size:13px; }
'''

_JS = r'''
export default function(component) {
  const { parentElement, data, setStateValue } = component;
  const img = parentElement.querySelector('.qr-image-preview');
  const status = parentElement.querySelector('.qr-image-status');
  let stopped = false;

  const payload = data && data.image_data ? data.image_data : '';
  const mime = (data && data.mime) || 'image/jpeg';
  if (!payload) {
    status.textContent = 'Waiting for image…';
    return () => { stopped = true; };
  }

  const src = `data:${mime};base64,${payload}`;
  img.src = src;

  const loadScript = (url) => new Promise((resolve) => {
    const existing = document.querySelector(`script[data-qr-lib="${url}"]`);
    if (existing) { existing.addEventListener('load', () => resolve(true)); setTimeout(() => resolve(!!window.ZXingBrowser), 1200); return; }
    const s = document.createElement('script');
    s.src = url; s.dataset.qrLib = url;
    s.onload = () => resolve(true); s.onerror = () => resolve(false);
    document.head.appendChild(s);
  });

  const finish = (text) => {
    if (stopped || !text) return;
    stopped = true;
    status.textContent = '✅ QR code decoded successfully.';
    setStateValue('qr_data', text);
  };

  const native = async () => {
    if (!('BarcodeDetector' in window)) return false;
    try {
      const detector = new BarcodeDetector({formats:['qr_code']});
      const codes = await detector.detect(img);
      if (codes && codes.length && codes[0].rawValue) { finish(codes[0].rawValue); return true; }
    } catch (e) {}
    return false;
  };

  const zxing = async () => {
    const ok = await loadScript('https://unpkg.com/@zxing/browser@0.2.1');
    if (!ok || !window.ZXingBrowser || stopped) return false;
    try {
      const reader = new ZXingBrowser.BrowserQRCodeReader();
      const result = await reader.decodeFromImageElement(img);
      const text = result && result.getText ? result.getText() : '';
      if (text) { finish(text); return true; }
    } catch (e) {}
    return false;
  };

  const jsqr = async () => {
    const ok = await loadScript('https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.js');
    if (!ok || !window.jsQR || stopped) return false;
    try {
      const canvas = document.createElement('canvas');
      const maxSide = 2200;
      const scale = Math.min(1, maxSide / Math.max(img.naturalWidth, img.naturalHeight));
      canvas.width = Math.max(1, Math.floor(img.naturalWidth * scale));
      canvas.height = Math.max(1, Math.floor(img.naturalHeight * scale));
      const ctx = canvas.getContext('2d', {willReadFrequently:true});
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      const image = ctx.getImageData(0,0,canvas.width,canvas.height);
      const code = window.jsQR(image.data, image.width, image.height, {inversionAttempts:'attemptBoth'});
      if (code && code.data) { finish(code.data); return true; }
    } catch (e) {}
    return false;
  };

  const run = async () => {
    try {
      await new Promise((resolve) => { if (img.complete) resolve(); else img.onload = resolve; });
      status.textContent = '🔍 Detecting QR code in the image…';
      if (await native()) return;
      if (await zxing()) return;
      if (await jsqr()) return;
      status.textContent = '❌ QR pattern could not be decoded from this image.';
    } catch (e) {
      status.textContent = '❌ QR decoder could not process this image.';
    }
  };

  run();
  return () => { stopped = true; };
}
'''

try:
    _component = st.components.v2.component(
        "qr_image_decoder_v2",
        html=_HTML,
        css=_CSS,
        js=_JS,
    )
except AttributeError:
    _component = None


def decode_uploaded_image_in_browser(image_bytes, mime_type="image/jpeg", key=None):
    if _component is None or not image_bytes:
        return None
    encoded = base64.b64encode(image_bytes).decode("ascii")
    result = _component(
        data={"image_data": encoded, "mime": mime_type},
        default={"qr_data": None},
        key=key,
        on_qr_data_change=lambda: None,
        height=410,
    )
    return getattr(result, "qr_data", None)
