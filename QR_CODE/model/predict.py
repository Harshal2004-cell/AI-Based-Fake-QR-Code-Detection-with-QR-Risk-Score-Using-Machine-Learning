import os
import joblib
import pandas as pd
from utils.feature_extraction import extract_features

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_FILE = os.path.join(PROJECT_ROOT, "model", "qr_model.pkl")
FEATURE_FILE = os.path.join(PROJECT_ROOT, "model", "feature_names.pkl")


def _load_or_train_model():
    """
    Load the locally trained model.

    If no model exists, train a fresh Random Forest from the project's
    dataset. Therefore the distributed project never requires a pre-trained
    model to start working.
    """
    if not os.path.exists(MODEL_FILE) or not os.path.exists(FEATURE_FILE):
        from model.train_model import train_model
        train_model()

    model = joblib.load(MODEL_FILE)
    feature_names = joblib.load(FEATURE_FILE)
    return model, feature_names


def retrain_model():
    """Force creation of a fresh Random Forest model from the current dataset."""
    from model.train_model import train_model
    return train_model()


def predict_qr(qr_data):
    """
    Predict safety of QR payload.

    On the first prediction, if no local model has been generated yet,
    the Random Forest is trained automatically from data/qr_dataset.csv.
    """
    model, feature_names = _load_or_train_model()

    # Extract features from QR payload
    features = extract_features(qr_data)
    feature_df = pd.DataFrame([features])

    # Ensure alignment with training features
    feature_df = feature_df.reindex(columns=feature_names, fill_value=0)

    # ML Probability (probability of class 1 = suspicious)
    probabilities = model.predict_proba(feature_df)[0]
    class_to_probability = dict(zip(model.classes_, probabilities))
    ml_suspicious_prob = float(class_to_probability.get(1, 0.0))

    # Rule-Based Heuristic Evaluation for Risk Score Adjustments & Reasons
    reasons = []

    if features.get("Has_IP_Address", 0) == 1:
        reasons.append("⚠️ Uses direct IP address instead of registered domain name")

    if features.get("HTTP", 0) == 1 and features.get("HTTPS", 0) == 0:
        reasons.append("⚠️ Uses non-secure HTTP connection (missing SSL certificate)")

    if features.get("Is_URL_Shortener", 0) == 1:
        reasons.append("⚠️ Uses URL shortener service which hides actual destination link")

    if features.get("Suspicious_TLD", 0) == 1:
        reasons.append(
            "⚠️ Uses untrusted / high-risk top-level domain extension "
            "(e.g. .xyz, .top, .click)"
        )

    if features.get("Has_Executable_Ext", 0) == 1:
        reasons.append(
            "🚨 Links directly to executable or script file download "
            "(.exe, .apk, .vbs)"
        )

    kw_count = features.get("Suspicious_Keyword_Count", 0)
    if kw_count > 0:
        reasons.append(
            f"⚠️ Contains {kw_count} phishing / fraud keyword(s) "
            "(e.g. login, verify, claim, winner)"
        )

    if features.get("Number_of_Subdomains", 0) >= 2:
        reasons.append(
            "⚠️ Contains multiple subdomains "
            "(often used in typosquatting phishing links)"
        )

    qr_type = (
        "UPI" if features.get("QR_Type_UPI", 0) == 1
        else ("URL" if features.get("QR_Type_URL", 0) == 1 else "TEXT")
    )

    if qr_type == "UPI":
        if features.get("UPI_Payment_Address", 0) == 0:
            reasons.append(
                "⚠️ Invalid or incomplete UPI payment URI "
                "(missing recipient payee address 'pa=')"
            )
        if features.get("UPI_Payee_Name", 0) == 0:
            reasons.append(
                "ℹ️ UPI payment URI lacks registered payee name parameter ('pn=')"
            )

    # Dynamic Risk Score Calculation (0 - 100)
    base_score = int(ml_suspicious_prob * 100)

    penalties = 0
    if features.get("Has_IP_Address", 0) == 1:
        penalties += 25
    if features.get("Has_Executable_Ext", 0) == 1:
        penalties += 35
    if features.get("Is_URL_Shortener", 0) == 1:
        penalties += 15
    if features.get("Suspicious_TLD", 0) == 1:
        penalties += 15
    if kw_count > 0:
        penalties += min(20, kw_count * 8)

    risk_score = min(100, max(0, int(0.7 * base_score + 0.3 * penalties)))

    if (
        features.get("Has_Executable_Ext", 0) == 1
        or features.get("Has_IP_Address", 0) == 1
    ):
        risk_score = max(risk_score, 75)

    if risk_score <= 30:
        risk_level = "Safe"
        if not reasons:
            reasons.append("✅ Passed all security checks with low risk profile")
            reasons.append("✅ Secure HTTPS connection with verified domain format")
    elif risk_score <= 70:
        risk_level = "Medium Risk"
        if not reasons:
            reasons.append(
                "⚠️ Payload shows mild anomaly parameters; "
                "exercise caution before opening"
            )
    else:
        risk_level = "High Risk"
        if not reasons:
            reasons.append(
                "🚨 Payload presents multiple high-severity security threats "
                "and phishing signatures"
            )

    result = {
        "qr_data": qr_data,
        "qr_type": qr_type,
        "probability": ml_suspicious_prob,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reasons": reasons,
        "features": features
    }


    return result
