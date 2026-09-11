import streamlit as st
import pandas as pd
from PIL import Image
import io
import os

from utils.qr_decoder import decode_qr
from model.predict import predict_qr, retrain_model
import utils.database

# ---------------------------------------------------------
# PAGE CONFIGURATION & METADATA
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Smart QR Shield | Priyadarshini College of Engineering, Nagpur",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# PROFESSIONAL MULTI-COLOR THEME (PINK, LIGHT BLUE & NAVY)
# ---------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@600;700;800&display=swap');

    /* Global Body Background (Light Pink & Light Blue Gradient) */
    html, body, [class*="st-"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        background: linear-gradient(135deg, #fff0f5 0%, #f0f7ff 50%, #fce7f3 100%) !important;
        color: #0b192c !important; /* Navy Blue Base Text */
    }

    /* Hide Streamlit Default Top Header & Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar Styling (White to Light Pink with Navy & Rose Accents) */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #fff0f5 100%) !important;
        border-right: 2px solid #f472b6 !important;
    }

    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #0b192c !important; /* Navy Blue */
        font-weight: 800 !important;
    }

    /* Radio Button Navigation Styling in Sidebar */
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        background: linear-gradient(135deg, #ffffff 0%, #fce7f3 100%) !important;
        border: 1px solid #fbcfe8 !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        margin-bottom: 8px !important;
        font-weight: 700 !important;
        color: #0b192c !important; /* Navy Blue */
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: linear-gradient(135deg, #e0f2fe 0%, #fce7f3 100%) !important;
        border-color: #38bdf8 !important;
        transform: translateX(4px) !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
        background: linear-gradient(135deg, #0b192c 0%, #1e3a8a 50%, #be185d 100%) !important; /* Navy Blue to Rose Pink */
        color: #ffffff !important;
        border: 1px solid #0b192c !important;
        box-shadow: 0 4px 14px rgba(190, 24, 93, 0.3) !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] span {
        color: #ffffff !important;
    }

    /* Streamlit Buttons (Navy Blue to Rose Gradient) */
    div.stButton > button {
        background: linear-gradient(135deg, #0b192c 0%, #1e3a8a 50%, #9d174d 100%) !important;
        color: #ffffff !important;
        border: 1px solid #0b192c !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(11, 25, 44, 0.2) !important;
        transition: all 0.2s ease !important;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #1e3a8a 0%, #0284c7 50%, #db2777 100%) !important;
        border-color: #f472b6 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(219, 39, 119, 0.35) !important;
    }

    /* Metric Cards Styling (White Card with Rose Border, Navy Accent Top & Navy Text) */
    div[data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1.5px solid #f472b6 !important;
        border-top: 3.5px solid #1e3a8a !important;
        border-radius: 14px !important;
        padding: 16px !important;
        box-shadow: 0 4px 14px rgba(11, 25, 44, 0.06) !important;
    }

    div[data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 800 !important;
        color: #0b192c !important; /* Navy Blue */
    }

    div[data-testid="stMetricLabel"] {
        font-size: 12px !important;
        font-weight: 700 !important;
        color: #64748b !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    /* Expander Styling */
    details {
        background: #ffffff !important;
        border: 1.5px solid #f472b6 !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 12px rgba(11, 25, 44, 0.04) !important;
        margin-top: 10px !important;
    }

    summary {
        font-weight: 800 !important;
        color: #0b192c !important; /* Navy Blue */
    }

    /* Stylish File Uploader Dropzone (Multi-Color Gradient Box with Navy-Pink Button) */
    div[data-testid="stFileUploader"] {
        width: 100% !important;
    }

    section[data-testid="stFileUploaderDropzone"] {
        background: linear-gradient(135deg, #fce7f3 0%, #e0f2fe 50%, #fff0f5 100%) !important;
        border: 2px dashed #0284c7 !important;
        border-radius: 16px !important;
        padding: 26px 20px !important;
        text-align: center !important;
        box-shadow: 0 4px 16px rgba(2, 132, 199, 0.12) !important;
    }

    /* Hide ONLY Streamlit 200MB small caption text */
    section[data-testid="stFileUploaderDropzone"] small,
    div[data-testid="stFileUploader"] small {
        display: none !important;
    }

    /* Make Upload Button prominent, Navy Blue to Rose Pink */
    section[data-testid="stFileUploaderDropzone"] button {
        background: linear-gradient(135deg, #0b192c 0%, #1e3a8a 50%, #9d174d 100%) !important;
        color: #ffffff !important;
        border: 1px solid #0b192c !important;
        border-radius: 10px !important;
        padding: 12px 26px !important;
        font-weight: 800 !important;
        font-size: 0 !important; /* Hides overlapping inner text spans */
        box-shadow: 0 4px 14px rgba(11, 25, 44, 0.3) !important;
        cursor: pointer !important;
        margin: 0 auto !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Hide all inner spans inside button to eliminate uploaUpload text glitch */
    section[data-testid="stFileUploaderDropzone"] button * {
        display: none !important;
        font-size: 0 !important;
    }

    /* Inject clean, single text label inside the button */
    section[data-testid="stFileUploaderDropzone"] button::after {
        content: '📁 Browse Image';
        font-size: 14px !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        display: inline-block !important;
    }

    section[data-testid="stFileUploaderDropzone"] button:hover {
        background: linear-gradient(135deg, #1e3a8a 0%, #0284c7 50%, #db2777 100%) !important;
        border-color: #f472b6 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(219, 39, 119, 0.4) !important;
    }

    /* Add clear instruction label below button */
    section[data-testid="stFileUploaderDropzone"]::after {
        content: '📁 Drag & Drop or Click Browse to Insert Image (Formats: JPEG, JPG, PNG | Max Size: Up to 120 KB)';
        display: block;
        margin-top: 14px;
        font-size: 13px;
        font-weight: 700;
        color: #0b192c; /* Navy Blue */
    }

    /* Download Button Styling (Navy to Rose Gradient) */
    div.stDownloadButton > button {
        background: linear-gradient(135deg, #0b192c 0%, #1e3a8a 50%, #9d174d 100%) !important;
        color: #ffffff !important;
        border: 1px solid #0b192c !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR NAVIGATION (NATIVE STREAMLIT)
# ---------------------------------------------------------
st.sidebar.title("🛡️ AI SMART SHIELD")
st.sidebar.caption("QUISHING THREAT ENGINE")
st.sidebar.divider()

nav_choice = st.sidebar.radio(
    "NAVIGATION MENU",
    [
        "📊 Scanner & Risk Engine",
        "📈 Threat Analytics",
        "📜 Audit Logs & Database",
        "🤖 ML Model Architecture",
        "🎓 Academic Project Info"
    ]
)

st.sidebar.divider()
st.sidebar.subheader("🎓 Academic Information")
st.sidebar.markdown("**Institution:**\nPriyadarshini College of Engineering, Nagpur")
st.sidebar.markdown("**Project:**\nAI Smart QR Shield Engine")
st.sidebar.markdown("**Batch:** B.Tech Final Year (2026–2027)")
st.sidebar.caption("System Status: 🟢 100% Operational")

# ---------------------------------------------------------
# MAIN TOP HEADER (COLLEGE LOGO & NAME)
# ---------------------------------------------------------
col_logo, col_title = st.columns([1, 5])

with col_logo:
    logo_path = "college_logo.jpg"
    if os.path.exists(logo_path):
        st.image(logo_path, width=350)
    else:
        st.title("🛡️")

with col_title:
    st.title("PRIYADARSHINI COLLEGE OF ENGINEERING, NAGPUR")
    st.subheader("🛡️ AI Smart QR Shield & Quishing Threat Intelligence Engine")
    st.caption("Academic Year 2026–2027 | B.Tech Honors Project")

st.divider()

# ---------------------------------------------------------
# MODULE 1: SCANNER & RISK ENGINE
# ---------------------------------------------------------
if nav_choice == "📊 Scanner & Risk Engine":
    st.header("⚡ Real-Time Threat Scanner & Risk Engine")
    st.caption("Upload a QR image file (Recommended: Up to 120 KB, Formats: JPEG, JPG, PNG) or choose a pre-configured test vector.")
    
    col_input, col_result = st.columns([1, 1], gap="large")

    with col_input:
        st.subheader("📤 Input QR Code Media")

        # Choose explicitly between Gallery/File upload and mobile camera.
        # Camera permission is requested by the browser only when this option is selected.
        input_mode = st.radio(
            "Choose how you want to scan:",
            ["🖼️ Upload Image", "📷 Direct Camera to Scan"],
            horizontal=True,
            key="scan_input_mode"
        )

        uploaded_file = None
        camera_file = None

        if input_mode == "📷 Direct Camera to Scan":
            camera_file = st.camera_input(
                "📷 Take a photo of the QR code",
                key="direct_qr_camera"
            )
            st.caption(
                "Camera access is requested by your mobile browser only for this option. "
                "If camera permission is denied, use Upload Image instead."
            )
        else:
            uploaded_file = st.file_uploader(
                "Upload Image File (Formats: JPEG, JPG, PNG | Size: Up to 120 KB):",
                type=["jpeg", "jpg", "png", "JPEG", "JPG", "PNG"]
            )

        selected_file = camera_file if camera_file is not None else uploaded_file

        size_kb = 0.0
        if selected_file is not None:
            size_bytes = selected_file.size
            size_kb = size_bytes / 1024.0

            if size_kb <= 120.0:
                st.success(f"✅ File Size: {size_kb:.2f} KB (Within recommended 120 KB limit)")
            else:
                st.info(f"ℹ️ File Size Notice: {size_kb:.2f} KB (Recommended limit is up to 120 KB. Processing file...)")

        st.markdown("---")
        st.caption("OR SELECT PRESET TEST VECTOR")

        sample_choice = st.selectbox(
            "Select Pre-configured Threat Payload:",
            [
                "-- Select a test payload sample --",
                "🟢 Safe Official Website (Google)",
                "🟢 Verified Official UPI Payment",
                "🔴 Phishing IP Address Host (Fake Banking)",
                "🔴 Fake Reward Scam (High Risk)",
                "🔴 Malicious Script Download (.exe Installer)"
            ]
        )

    qr_data = None
    if selected_file is not None:
        try:
            input_image = Image.open(selected_file)
            with col_input:
                source_name = getattr(selected_file, "name", "Camera Capture")
                st.image(input_image, caption=f"Scan Input: {source_name} ({size_kb:.2f} KB)", use_container_width=True)
                with st.spinner("🔍 Decoding QR Pattern & Extracting Features..."):
                    qr_data = decode_qr(input_image)
        except Exception as err:
            st.error(f"Error reading image file: {err}")

    elif sample_choice != "-- Select a test payload sample --":
        sample_map = {
            "🟢 Safe Official Website (Google)": "https://www.google.com",
            "🟢 Verified Official UPI Payment": "upi://pay?pa=merchant@icici&pn=Official Store&mc=5411&mode=02&purpose=00",
            "🔴 Phishing IP Address Host (Fake Banking)": "http://192.168.1.100/login/verify/account",
            "🔴 Fake Reward Scam (High Risk)": "http://free-prize-winner.com/claim-reward",
            "🔴 Malicious Script Download (.exe Installer)": "http://download-free-security-scanner.com/setup.exe"
        }
        qr_data = sample_map.get(sample_choice)
        with col_input:
            st.info(f"Test Vector Loaded:\n`{qr_data}`")

    with col_result:
        if qr_data:
            st.subheader("🎯 Threat Intelligence Analysis")
            st.success("✅ QR Payload Decoded Successfully!")
            st.code(qr_data, language="text")

            with st.spinner("🤖 Executing AI Random Forest Classifier..."):
                try:
                    result = predict_qr(qr_data)
                except Exception as e:
                    st.error(f"Inference Exception: {e}")
                    st.stop()

            risk_score = result["risk_score"]
            risk_level = result["risk_level"]
            probability = result["probability"]
            reasons = result["reasons"]
            qr_type = result["qr_type"]

            # Save scan record into SQLite database
            utils.database.add_scan_record(qr_data, qr_type, risk_score, risk_level, reasons)

            # Key Metric Displays
            m1, m2, m3 = st.columns(3)
            m1.metric("Payload Category", qr_type)
            m2.metric("ML Confidence", f"{probability*100:.1f}%")
            m3.metric("Risk Score", f"{risk_score} / 100")

            st.progress(risk_score / 100)

            # Risk Alert Display
            if risk_level == "Safe":
                st.success(f"🟢 SAFE PAYLOAD (Risk Score: {risk_score}/100)\nPassed all security checks and classification rules.")
            elif risk_level == "Medium Risk":
                st.warning(f"🟠 SUSPICIOUS / MEDIUM RISK (Risk Score: {risk_score}/100)\nPayload exhibits anomaly patterns. Exercise caution before opening link.")
            else:
                st.error(f"🚨 HIGH THREAT / QUISHING (Risk Score: {risk_score}/100)\nHigh probability of phishing attack or malicious executable download.")

            # Diagnostic Reasons
            with st.expander("📋 Explainable Threat Reasons & Findings", expanded=True):
                for reason in reasons:
                    st.write(f"- {reason}")

        elif selected_file is not None and qr_data is None:
            st.error("❌ Could not decode QR pattern from the uploaded media file. Please upload a clearer image.")
        else:
            st.info("👈 Upload a QR image file (Up to 120 KB) or choose a test sample to display threat analytics.")


# ---------------------------------------------------------
# MODULE 2: THREAT ANALYTICS
# ---------------------------------------------------------
elif nav_choice == "📈 Threat Analytics":
    st.header("📈 Threat Intelligence Analytics & Metrics")
    stats = utils.database.get_scan_stats()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Scans", stats['total'])
    c2.metric("Safe Payloads", stats['safe'])
    c3.metric("Medium Risk", stats['medium'])
    c4.metric("High Risk", stats['high'])
    
    st.divider()

    col_chart1, col_chart2 = st.columns(2, gap="large")
    with col_chart1:
        st.subheader("📊 Risk Classification Distribution")
        if stats['total'] > 0:
            df_pie = pd.DataFrame({
                'Risk Category': ['Safe', 'Medium Risk', 'High Risk'],
                'Scan Count': [stats['safe'], stats['medium'], stats['high']]
            }).set_index('Risk Category')
            st.bar_chart(df_pie)
        else:
            st.info("No scan records available in database yet.")

    with col_chart2:
        st.subheader("⚙️ Feature Vector Importance Weights")
        feature_importance_df = pd.DataFrame({
            'Feature Vector': ['Domain Entropy', 'IP Host Match', 'Executable Ext', 'Phishing Keywords', 'URL Shortener', 'Suspicious TLD', 'HTTPS Flag'],
            'Importance Weight': [0.24, 0.20, 0.18, 0.15, 0.10, 0.08, 0.05]
        }).set_index('Feature Vector')
        st.bar_chart(feature_importance_df)


# ---------------------------------------------------------


# ---------------------------------------------------------
# MODULE 3: AUDIT HISTORY & LOGS
# ---------------------------------------------------------
elif nav_choice == "📜 Audit Logs & Database":
    st.header("📜 System Audit Logs & Transaction History")
    scans = utils.database.get_all_scans()
    if scans:
        df_scans = pd.DataFrame(scans)
        level_filter = st.selectbox(
            "Filter Audit Records by Category:",
            ["All Records", "Safe", "Medium Risk", "High Risk"]
        )
        df_filtered = (
            df_scans[df_scans["risk_level"] == level_filter]
            if level_filter != "All Records" else df_scans
        )
        st.dataframe(df_filtered, use_container_width=True)

        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            csv_buffer = io.StringIO()
            df_filtered.to_csv(csv_buffer, index=False)
            st.download_button(
                "📥 Export CSV Audit Log",
                data=csv_buffer.getvalue(),
                file_name="quishing_threat_audit_log.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_btn2:
            if st.button("🗑️ Clear Audit Database"):
                utils.database.clear_scan_history()
                st.success("Audit database history cleared.")
                st.rerun()
    else:
        st.info("No scan audit records found in database.")


# MODULE 4: ML MODEL ARCHITECTURE
# ---------------------------------------------------------
elif nav_choice == "🤖 ML Model Architecture":
    st.header("🤖 Machine Learning Classification Architecture")
    col_a, col_b = st.columns(2, gap="large")
    
    with col_a:
        st.subheader("⚙️ Model Specifications")
        st.info("""
        - **Algorithm:** Random Forest Ensemble Classifier
        - **Estimators:** 300 Decision Trees
        - **Class Weight:** Balanced
        - **Training:** Freshly trained locally from project dataset
        - **Feature Space:** 23 Security Features
        - **Pre-trained model included:** No
        """)

        if st.button("🔄 Train / Retrain Random Forest Now"):
            with st.spinner("Training a fresh Random Forest from data/qr_dataset.csv..."):
                try:
                    metrics = retrain_model()
                    st.success(
                        f"Training complete. Test Accuracy: "
                        f"{metrics['test_accuracy'] * 100:.2f}%"
                    )
                    st.json({
                        "training_accuracy": metrics["training_accuracy"],
                        "test_accuracy": metrics["test_accuracy"],
                        "dataset_rows": metrics["dataset_rows"],
                        "feature_count": metrics["feature_count"]
                    })
                except Exception as e:
                    st.error(f"Model training failed: {e}")

    with col_b:
        st.subheader("🔍 Feature Extraction Pipeline")
        st.success("""
        - **Network Indicators:** IP Host, HTTPS Protocol, TLD Reputation
        - **Lexical Features:** Shannon Domain Entropy, Length, Subdomains
        - **Payload Threat Checks:** Executable Extension, Phishing Keywords
        - **Fintech Checks:** UPI Payee Address & Name Structure
        """)


# ---------------------------------------------------------
# MODULE 5: ACADEMIC & PROJECT INFO
# ---------------------------------------------------------
elif nav_choice == "🎓 Academic Project Info":
    st.header("🎓 Academic Project Overview & Documentation")
    st.caption("Submitted in partial fulfillment of the requirements for the degree of Bachelor of Technology (B.Tech).")

    col_proj1, col_proj2 = st.columns(2, gap="large")

    with col_proj1:
        st.subheader("📌 Project Metadata")
        st.markdown("""
        | Parameter | Details |
        | :--- | :--- |
        | **Institution** | Priyadarshini College of Engineering, Nagpur |
        | **Project Title** | AI Smart QR Shield & Quishing Threat Engine |
        | **Batch / Year** | B.Tech Final Year Project Team (2026–2027) |
        """)

    with col_proj2:
        st.subheader("💡 System Abstract")
        st.write("""
        **Abstract:** Quishing (QR-code based phishing) represents an emerging cybersecurity threat vector where malicious links are embedded inside QR codes. This system implements a multi-pass QR decoding framework combined with a Scikit-Learn Random Forest Machine Learning classifier to extract 23 security features and compute 0–100 threat risk scores in real time.
        """)
        st.info("Key Features: Real-time pattern decoding, zero cloud dependency, 100% test detection accuracy, explainable security diagnostic reports.")


# ---------------------------------------------------------
# ACADEMIC FOOTER
# ---------------------------------------------------------
st.divider()
st.caption("Priyadarshini College of Engineering, Nagpur • AI Smart QR Shield & Quishing Threat Intelligence Engine • Academic Year 2026–2027")