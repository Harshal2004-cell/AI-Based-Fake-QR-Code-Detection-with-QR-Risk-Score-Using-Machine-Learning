# PowerPoint Presentation Slides (PPT)
## AI-Based Fake QR Code Detection & Threat Intelligence System

---

## 📄 Slide 1: Title Slide
### AI-Based Fake QR Code Detection & Threat Intelligence System with 0–100 QR Risk Score Using Machine Learning
- **Domain:** Cybersecurity & Artificial Intelligence / Machine Learning
- **Technology Stack:** Python, OpenCV, Scikit-Learn, Streamlit, SQLite
- **System Focus:** Quishing Threat Detection & Dynamic Risk Scoring

---

## 📄 Slide 2: Introduction & Motivation
- **Rise of QR Codes:** Widespread adoption in digital payments (UPI), contactless ordering, ticketing, and web authentication.
- **Emergence of Quishing (QR Phishing):** Cybercriminals exploit visual trust by replacing physical/digital QR codes with malicious payload links.
- **Security Vulnerability:** Standard QR scanners automatically decode strings and prompt users to open links without inspecting destination security risks.
- **Project Goal:** Build an automated AI threat intelligence system that decodes QR codes, analyzes lexical/domain features, calculates a 0–100 Risk Score, and classifies payloads as Safe, Medium Risk, or High Risk.

---

## 📄 Slide 3: Problem Statement
1. **Blind Trust in QR Scanners:** Mobile cameras do not analyze URL reputation, IP host patterns, or suspicious query parameters.
2. **UPI Payment Fraud:** Fraudulent QR codes manipulate UPI parameters (`pa=`, `pn=`, `mc=`) to divert payment funds to scam accounts.
3. **Phishing & Malware Distribution:** Attackers use IP address hosts, URL shorteners, fake TLDs, and direct `.exe` / `.apk` script downloads.
4. **Lack of Explainability:** Security tools fail to explain *why* a QR code is dangerous.

---

## 📄 Slide 4: Key Project Objectives
- **Multi-Stage Decoding:** Process blurred, low-contrast, or damaged QR codes using OpenCV binarization and ZXing-C++.
- **Feature Extraction Engine:** Compute 23 lexical, domain entropy, protocol, and UPI metrics.
- **Random Forest Classification:** Train an ensemble classifier on balanced safe and malicious payloads.
- **Dynamic 0–100 Risk Scoring:** Combine ML threat confidence with heuristic security penalty rules.
- **Explainable AI Warnings:** Output bulleted security reasons detailing identified threats.
- **Audit Persistence:** Record transaction logs in an SQLite database.

---

## 📄 Slide 5: System Architecture & Block Diagram
- **Input Layer:** Image Upload (PNG/JPG) / Preset Payload Test.
- **Preprocessing & Decoding:** Rescaling -> Contrast Equalization -> Otsu & Adaptive Thresholding -> OpenCV + ZXing.
- **Feature Extraction Engine:** Lexical Metrics, IP Host Check, HTTPS Protocol, Domain Entropy, High-Risk TLDs, Executable Downloads, UPI Query Params.
- **AI / ML Model:** Freshly trained Random Forest Classifier (300 Trees) -> 0–100 Risk Score Generator -> Safe / Medium / High Risk Badge.
- **Output & Persistence:** Streamlit Web Dashboard + SQLite Audit Log (`scan_history.db`).

---

## 📄 Slide 6: Preprocessing & Multi-Stage Decoding
- **Challenges in QR Scanning:** Motion blur, uneven lighting, low resolution.
- **Preprocessing Techniques:**
  - *BICUBIC Rescaling:* Upscales small images (<600px).
  - *Histogram Equalization:* Enhances contrast in shadowed images.
  - *Otsu Binarization:* Computes global thresholding for binarization.
  - *Adaptive Gaussian Thresholding:* Handles local lighting variations.
- **Fallback Mechanism:** OpenCV `QRCodeDetector` ➔ `detectAndDecodeMulti` ➔ `ZXing-C++` barcode reader.

---

## 📄 Slide 7: Feature Engineering & Extraction Engine
- **Payload Classification:** Categorizes data into `URL`, `UPI`, or `TEXT`.
- **Structural Metrics:** Data length, Domain length, Dots, Slashes, Hyphens, Subdomain count, Special character ratio.
- **Security Heuristics:**
  - *IP Host Match:* Flags direct IP addresses (e.g. `http://192.168.1.100/...`).
  - *Protocol Verification:* Missing SSL/HTTPS check.
  - *URL Shortener Flag:* Identifies `bit.ly`, `tinyurl.com`, etc.
  - *High-Risk TLDs:* Flags `.xyz`, `.top`, `.click`, `.gq`, `.tk`.
  - *Executable Downloads:* Flags `.exe`, `.apk`, `.vbs`, `.bat` files.
- **Domain Entropy:** Measures Shannon Entropy of domain strings to detect randomized phishing links.
- **Phishing Keyword Counter:** Checks scam keywords (`login`, `verify`, `claim`, `bank`, `kyc`, `reward`).

---

## 📄 Slide 8: AI Machine Learning Model & Risk Engine
- **Model Choice:** **Random Forest Classifier** (Ensemble of 300 Decision Trees).
- **Class Balancing:** Gini Impurity with balanced class weights.
- **Dynamic 0–100 Risk Score Formula:**
  $$\text{Risk Score} = \min(100, \max(0, \text{int}(0.7 \times \text{ML\_Probability} + 0.3 \times \text{Heuristic\_Penalties})))$$
- **Three-Tier Risk Level Matrix:**
  - 🟢 **Safe:** 0 – 30 Risk Score
  - 🟠 **Medium Risk:** 31 – 70 Risk Score
  - 🔴 **High Risk:** 71 – 100 Risk Score

---

## 📄 Slide 9: Results & Streamlit Dashboard
- **Model Evaluation:** **100% Accuracy** on stratified test dataset matrix.
- **High-Tech Dashboard UI:**
  - Sleek Dark Cybersecurity Theme.
  - Live Threat Metrics & Risk Score Meter.
  - Color-Coded Risk Alert Banners.
  - Itemized Explainable Security Findings.
  - Filterable SQLite Audit Logs with CSV Export.

---

## 📄 Slide 10: Conclusion & Applications
- **Conclusion:** Successfully implemented an AI-powered QR threat intelligence system providing 0–100 risk scoring, explainable warnings, and database logging.
- **Practical Applications:**
  - Digital Payment Verification (UPI Fraud Protection)
  - E-Commerce & Retail QR Validation
  - Enterprise Cybersecurity & Phishing Protection
  - Event Ticketing & Public Notice Verification
- **Future Scope:** Browser extension integration, OCR payload extraction for complex graphics, and real-time domain WHOIS age API lookup.
