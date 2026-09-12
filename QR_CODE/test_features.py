from utils.feature_extraction import extract_features


test_data = "upi://pay?pa=8468914836@ibl&pn=Kalyani%20Pradip%20Derkar&mc=0000&mode=02&purpose=00"

features = extract_features(test_data)

print("\n========== QR FEATURES ==========\n")

for key, value in features.items():
    print(f"{key}: {value}")

print("\n=================================\n")