# QR scanning support

The application treats JPG/JPEG/PNG/WEBP/BMP/TIFF as **image file formats**, not QR protocols.

Decoded QR payloads are then analyzed as UPI, HTTP/HTTPS URLs, common protocol payloads (TEL, SMS, MAILTO, GEO, WIFI, VCARD), or plain text.

The scanner uses multiple decoding layers:
- OpenCV QRCodeDetector with contrast, threshold, crop and orientation variants.
- Optional PyZbar / ZXing-C++ when available on the host.
- Browser-side ZXing Browser + BarcodeDetector + jsQR fallback for uploaded images.
- Browser-side ZXing Browser + BarcodeDetector + jsQR fallback for direct camera scanning.

A branded QR logo does not change the payload protocol. However, no decoder can guarantee recovery if a logo, blur, glare, cropping, or damage destroys too much of the QR's error-correction data.
