# AI-Based Fake QR Code Detection & Threat Intelligence System

## 1. Project Title
**AI-Based Fake QR Code Detection & Threat Intelligence System with 0–100 QR Risk Score Using Machine Learning**

---

## 2. Abstract
Quick Response (QR) codes have become ubiquitous across digital payment ecosystems (UPI), contactless ordering, and web authentication. However, this growth has triggered a rapid rise in "Quishing" (QR Code Phishing) attacks, where cybercriminals replace legitimate QR codes with malicious targets to steal user credentials, initiate fraudulent payment transfers, or distribute malware. Standard mobile QR scanners decode and open payloads blindly without safety verification. 

This project presents an end-to-end **AI-Based Fake QR Code Detection & Threat Intelligence System**. The system incorporates a multi-pass image processing decoder (combining OpenCV binarization and ZXing-C++ engine) to reliably extract QR payloads. An advanced feature extraction engine computes 23 structural, lexical, domain entropy, protocol, and UPI payment parameter metrics. A **Random Forest Classifier (300 Decision Trees), trained locally from the project dataset** evaluates these features alongside security heuristics to generate an intuitive **0–100 QR Risk Score** and categorize payloads into a three-tier threat matrix: **Safe (0–30)**, **Medium Risk (31–70)**, and **High Risk (71–100)**. Transparent, human-readable threat explanations accompany every scan, and all transactions are audited in an SQLite database accessible via a modern Streamlit web dashboard.

---

## 3. Problem Definition
1. **Inherent Blindness of Standard Scanners**: Conventional QR code readers only decode raw strings and automatically prompt users to open links without inspecting security attributes or destination risks.
2. **Growth of Quishing Attacks**: Attackers leverage physical sticker overlays, spoofed banking domains, IP address hosts, and URL shorteners to bypass user suspicion.
3. **Financial Fraud in UPI Payments**: Fake payment QR codes often omit or alter payee addresses (`pa=`), merchant codes (`mc=`), or payee names (`pn=`), leading users to transfer money directly to scam accounts.
4. **Lack of Explainable Risk Scores**: Existing security tools provide binary flags without explaining *why* a link is dangerous, leaving users unaware of specific threat vectors.

---

## 4. System Workflow & Block Diagram

```
[ INPUT LAYER ] 
   └─ Upload QR Code Image (PNG / JPG / JPEG) or Select Test Payload
          │
          ▼
[ PREPROCESSING & DECODING LAYER ]
   ├─ Image Rescaling & Contrast Equalization
   ├─ Multi-Pass Binarization (Otsu & Adaptive Gaussian Thresholding)
   └─ Dual Decoding Engine (OpenCV QRCodeDetector + ZXing-C++ Fallback)
          │
          ▼
[ FEATURE EXTRACTION ENGINE ]
   ├─ Payload Classification (URL vs. UPI vs. Plain Text)
   ├─ Lexical Metrics (Length, Special Chars, Dots, Slashes, Hyphens, Subdomain Count)
   ├─ Protocol & Host Analysis (HTTPS Flag, HTTP Flag, IP Address Host Match)
   ├─ Domain Intelligence (Shannon Domain Entropy, High-Risk TLDs, URL Shortener Flag)
   ├─ Security Threat Checks (Executable Extensions: .exe, .apk, .vbs)
   ├─ Phishing Keyword Engine (Login, Verify, Claim, Reward, Bank, KYC)
   └─ UPI Query Parameter Validation (pa=, pn=, mc=)
          │
          ▼
[ AI / ML INFERENCE & RISK ENGINE ]
   ├─ Random Forest Classifier (300 Trees, Balanced Class Weighting)
   ├─ Malicious Probability Calculation
   ├─ Heuristic Penalty Integration -> 0–100 Risk Score
   ├─ 3-Tier Classification (Safe / Medium Risk / High Risk)
   └─ Explainable Security Reason Generator
          │
          ▼
[ OUTPUT & PERSISTENCE LAYER ]
   ├─ Interactive Streamlit Dashboard (Risk Score Meter & Threat Alert Cards)
   ├─ Explainable Security Bullet Points
   └─ SQLite Scan Log Persistence (scan_history.db)
```

---

## 5. Tools & Software Used
- **Integrated Development Environment (IDE)**: Visual Studio Code (VS Code)
- **Programming Language**: Python 3.12+
- **Database Engine**: SQLite3
- **Web Application Framework**: Streamlit
- **Operating System**: Windows 11
- **Command Shell & Execution Environment**: Windows PowerShell & Virtual Environment (`venv`)

---

## 6. Python Libraries & Modules Used

| Library / Module | Purpose & Role in System |
| :--- | :--- |
| **`opencv-python` (`cv2`)** | Image preprocessing, contrast enhancement, histogram equalization, Otsu thresholding, adaptive binarization, and QR code corner detection. |
| **`streamlit`** | Interactive high-tech web dashboard interface, risk score progress bars, alert banners, CSV log exports, and multi-page navigation. |
| **`scikit-learn`** | Machine learning framework used for Random Forest Classifier model training, hyperparameter tuning, train-test splitting, accuracy score, and confusion matrix evaluation. |
| **`pandas`** | Dataset handling, CSV loading, feature matrix construction, and audit log dataframes. |
| **`numpy`** | Array conversions and numeric image transformations. |
| **`joblib`** | Serializing and loading trained machine learning models (`qr_model.pkl`) and feature names (`feature_names.pkl`). |
| **`Pillow` (`PIL`)** | Opening, handling, and converting user-uploaded image files. |
| **`zxing-cpp`** | High-performance C++ barcode decoding fallback module for difficult or damaged QR codes. |
| **`sqlite3`** | Relational database operations for persisting scan history, timestamps, risk scores, and reasons. |
| **`re`** | Regular expressions for IP address detection, URI parameter parsing (`pa=`, `pn=`, `mc=`), and keyword matching. |
| **`urllib.parse`** | URL parsing for extracting domain netlocs and path components. |
| **`math`** | Mathematical calculations, including Shannon Entropy computation for domain randomness detection. |
