import sys
import io

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from model.predict import predict_qr

test_payloads = [
    "https://www.google.com",
    "upi://pay?pa=merchant@icici&pn=Official Store&mc=5411&mode=02&purpose=00",
    "http://192.168.1.100/login/verify/account",
    "http://download-free-security-scanner.com/setup.exe"
]

print("\n==============================================")
print("      AI QR SHIELD PREDICTION TEST")
print("==============================================")

for payload in test_payloads:
    res = predict_qr(payload)
    print(f"\nPayload    : {res['qr_data']}")
    print(f"Type       : {res['qr_type']}")
    print(f"Risk Score : {res['risk_score']} / 100")
    print(f"Risk Level : {res['risk_level']}")
    print(f"ML Conf.   : {res['probability']*100:.2f}%")
    print("Reasons    :")
    for reason in res["reasons"]:
        print(f"  - {reason}")
    print("-" * 46)

print("==============================================\n")