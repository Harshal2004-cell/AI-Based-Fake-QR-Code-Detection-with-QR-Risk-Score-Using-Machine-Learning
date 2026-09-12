import cv2
import numpy as np
import sys


# ============================================================
# QR DETECTION FUNCTION
# ============================================================

def try_decode(detector, image, method_name):

    try:
        data, points, _ = detector.detectAndDecode(image)

        if data:
            print("\n========================================")
            print("✅ QR CODE DETECTED!")
            print("========================================")
            print("Method :", method_name)
            print("QR DATA:")
            print(data)
            print("========================================\n")
            return data

    except Exception as e:
        print(f"⚠️ {method_name} failed: {e}")

    return None


# ============================================================
# MAIN PROGRAM
# ============================================================

print("========================================")
print("       AI SMART QR SHIELD")
print("       QR Detection Test")
print("========================================")


# ------------------------------------------------------------
# Select image
# ------------------------------------------------------------

image_path = input(
    "\nEnter QR image path "
    "(example: qr_test.png): "
).strip()


if not image_path:

    print("❌ No image path entered.")
    sys.exit()


# ------------------------------------------------------------
# Load image
# ------------------------------------------------------------

image = cv2.imread(image_path)


if image is None:

    print("\n❌ Could not open image.")
    print("Check the image path.")
    sys.exit()


print("\n✅ Image opened successfully!")

print("Image size:")
print("Width  :", image.shape[1])
print("Height :", image.shape[0])


# ------------------------------------------------------------
# Display image
# ------------------------------------------------------------

display_image = image.copy()

print("\nA window will open.")
print("Drag a rectangle around ONLY the QR code.")
print("Then press ENTER or SPACE.")
print("Press C to cancel.")


roi = cv2.selectROI(
    "Select ONLY QR Code",
    display_image,
    showCrosshair=True,
    fromCenter=False
)

cv2.destroyAllWindows()


x, y, w, h = roi


if w == 0 or h == 0:

    print("\n❌ No ROI selected.")
    sys.exit()


print("\n✅ QR region selected!")

print("X:", x)
print("Y:", y)
print("Width :", w)
print("Height:", h)


# ------------------------------------------------------------
# Crop QR
# ------------------------------------------------------------

qr = image[y:y+h, x:x+w]


# Save cropped QR for debugging
cv2.imwrite("cropped_qr.png", qr)

print("✅ Cropped QR saved as cropped_qr.png")


# ============================================================
# PREPROCESSING
# ============================================================

gray = cv2.cvtColor(qr, cv2.COLOR_BGR2GRAY)


# ------------------------------------------------------------
# Resize
# ------------------------------------------------------------

scale = 3

large_gray = cv2.resize(
    gray,
    None,
    fx=scale,
    fy=scale,
    interpolation=cv2.INTER_CUBIC
)


# ------------------------------------------------------------
# Histogram equalization
# ------------------------------------------------------------

equalized = cv2.equalizeHist(large_gray)


# ------------------------------------------------------------
# OTSU threshold
# ------------------------------------------------------------

_, otsu = cv2.threshold(
    equalized,
    0,
    255,
    cv2.THRESH_BINARY + cv2.THRESH_OTSU
)


# ------------------------------------------------------------
# Inverted OTSU
# ------------------------------------------------------------

inverted_otsu = cv2.bitwise_not(otsu)


# ------------------------------------------------------------
# Adaptive threshold
# ------------------------------------------------------------

adaptive = cv2.adaptiveThreshold(
    equalized,
    255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY,
    31,
    5
)


# ------------------------------------------------------------
# Inverted adaptive
# ------------------------------------------------------------

inverted_adaptive = cv2.bitwise_not(adaptive)


# ============================================================
# CREATE DETECTOR
# ============================================================

detector = cv2.QRCodeDetector()


# ============================================================
# TRY DIFFERENT IMAGES
# ============================================================

images_to_try = [

    ("Original QR", qr),

    ("Grayscale", gray),

    ("Resized Grayscale", large_gray),

    ("Equalized", equalized),

    ("OTSU", otsu),

    ("Inverted OTSU", inverted_otsu),

    ("Adaptive Threshold", adaptive),

    ("Inverted Adaptive", inverted_adaptive),

]


print("\n========================================")
print("Starting QR detection...")
print("========================================")


qr_data = None


for method_name, test_image in images_to_try:

    print("\nTrying:", method_name)

    qr_data = try_decode(
        detector,
        test_image,
        method_name
    )

    if qr_data:
        break


# ============================================================
# MULTIPLE SCALE TEST
# ============================================================

if qr_data is None:

    print("\n========================================")
    print("Trying additional scales...")
    print("========================================")

    for scale in [1.5, 2, 2.5, 4, 5]:

        resized = cv2.resize(
            gray,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC
        )

        qr_data = try_decode(
            detector,
            resized,
            f"Scale {scale}"
        )

        if qr_data:
            break


# ============================================================
# FINAL RESULT
# ============================================================

if qr_data:

    print("\n")
    print("****************************************")
    print("       🎉 SUCCESS!")
    print("****************************************")
    print("QR DATA:")
    print(qr_data)
    print("****************************************")

    print("\nNext step:")
    print("We will connect this QR data to predict_qr().")

else:

    print("\n")
    print("****************************************")
    print("       ❌ QR NOT DECODED")
    print("****************************************")

    print("\nThe image was successfully opened,")
    print("but OpenCV could not decode the QR.")

    print("\nThe cropped QR has been saved as:")
    print("cropped_qr.png")

    print("\nWe will use this cropped image for")
    print("the next debugging step.")


# ============================================================
# SHOW PROCESSED IMAGE
# ============================================================

cv2.imshow(
    "Cropped QR",
    qr
)

cv2.waitKey(0)
cv2.destroyAllWindows()