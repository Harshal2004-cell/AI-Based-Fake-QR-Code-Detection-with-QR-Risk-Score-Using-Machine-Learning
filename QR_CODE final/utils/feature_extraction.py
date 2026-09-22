import re
import math
from urllib.parse import urlparse


def calculate_entropy(text):
    """Calculate Shannon Entropy of a string."""
    if not text:
        return 0.0
    entropy = 0.0
    for x in set(text):
        p_x = float(text.count(x)) / len(text)
        entropy -= p_x * math.log2(p_x)
    return round(entropy, 4)


def extract_features(data):
    """
    Extract comprehensive lexical, URL, entropy, and UPI features from raw QR data.
    """
    data = str(data).strip()
    features = {}

    # Basic Payload Metrics
    features["Data_Length"] = len(data)

    # QR Payload Type
    data_lower = data.lower()
    if data_lower.startswith("upi://"):
        qr_type = "UPI"
    elif data_lower.startswith(("http://", "https://")):
        qr_type = "URL"
    elif data_lower.startswith(("tel:", "sms:", "mailto:", "geo:", "wifi:", "vcard:", "begin:vcard")):
        qr_type = "PROTOCOL"
    else:
        qr_type = "TEXT"

    features["QR_Type_UPI"] = 1 if qr_type == "UPI" else 0
    features["QR_Type_URL"] = 1 if qr_type == "URL" else 0
    features["QR_Type_TEXT"] = 1 if qr_type in ("TEXT", "PROTOCOL") else 0
    features["QR_Type_PROTOCOL"] = 1 if qr_type == "PROTOCOL" else 0

    # Protocol Verification
    features["HTTPS"] = 1 if data_lower.startswith("https://") else 0
    features["HTTP"] = 1 if data_lower.startswith("http://") else 0

    # IP Address Host Detection
    ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    features["Has_IP_Address"] = 1 if re.search(ip_pattern, data) else 0

    # Lexical Counts
    features["Number_of_Dots"] = data.count(".")
    features["Number_of_Slashes"] = data.count("/")
    features["Number_of_Hyphens"] = data.count("-")
    features["Number_of_Digits"] = sum(c.isdigit() for c in data)
    features["Number_of_Special_Characters"] = len(re.findall(r"[^a-zA-Z0-9]", data))

    # Domain Analysis
    domain = ""
    try:
        if qr_type == "URL":
            parsed = urlparse(data)
            domain = parsed.netloc
        elif "://" in data:
            domain = data.split("://")[1].split("/")[0]
        
        if "@" in domain:
            domain = domain.split("@")[-1]
            
    except Exception:
        domain = ""

    features["Domain_Length"] = len(domain)
    features["Domain_Entropy"] = calculate_entropy(domain)

    if domain:
        parts = domain.split(".")
        features["Number_of_Subdomains"] = max(0, len(parts) - 2)
    else:
        features["Number_of_Subdomains"] = 0

    # URL Shortener Detection
    shorteners = [
        "bit.ly", "tinyurl.com", "is.gd", "t.co", "cutt.ly",
        "ow.ly", "buff.ly", "rebrand.ly", "goo.gl", "tiny.cc"
    ]
    features["Is_URL_Shortener"] = 1 if any(s in domain for s in shorteners) else 0

    # Suspicious Top-Level Domains (TLDs)
    suspicious_tlds = [
        ".xyz", ".top", ".click", ".gq", ".tk", ".ml",
        ".site", ".website", ".online", ".info", ".work", ".ga", ".cf"
    ]
    features["Suspicious_TLD"] = 1 if any(domain.endswith(tld) for tld in suspicious_tlds) else 0

    # Executable / Malicious Extension Check
    exec_extensions = [".exe", ".apk", ".vbs", ".bat", ".scr", ".zip", ".rar"]
    features["Has_Executable_Ext"] = 1 if any(data_lower.endswith(ext) or (ext + "?") in data_lower for ext in exec_extensions) else 0

    # Phishing / Scam Keyword Detection
    suspicious_keywords = [
        "login", "verify", "verification", "account", "update", "secure",
        "security", "password", "confirm", "bank", "free", "winner",
        "prize", "urgent", "claim", "signin", "payment", "refund",
        "kyc", "lottery", "reward", "gold", "reactivate", "alert"
    ]

    keyword_count = sum(1 for kw in suspicious_keywords if kw in data_lower)
    features["Suspicious_Keyword_Count"] = keyword_count
    features["Has_Suspicious_Keyword"] = 1 if keyword_count > 0 else 0

    # UPI Query Parameter Extraction
    if qr_type == "UPI":
        features["UPI_Payment_Address"] = 1 if re.search(r"[?&]pa=([^&]+)", data, re.IGNORECASE) else 0
        features["UPI_Payee_Name"] = 1 if re.search(r"[?&]pn=([^&]+)", data, re.IGNORECASE) else 0
        features["UPI_Merchant_Code"] = 1 if re.search(r"[?&]mc=([^&]+)", data, re.IGNORECASE) else 0
    else:
        features["UPI_Payment_Address"] = 0
        features["UPI_Payee_Name"] = 0
        features["UPI_Merchant_Code"] = 0

    return features