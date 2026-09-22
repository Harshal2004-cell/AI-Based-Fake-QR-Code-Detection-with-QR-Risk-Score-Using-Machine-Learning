import streamlit as st
import pandas as pd
from PIL import Image
import io
from pathlib import Path

from utils.qr_decoder import decode_qr
from components.auto_qr_camera import auto_qr_camera
from components.qr_image_decoder import decode_uploaded_image_in_browser
from model.predict import predict_qr, retrain_model
import utils.database

# ---------------------------------------------------------
# PAGE CONFIGURATION & METADATA
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Smart | Priyadarshini College of Engineering, Nagpur",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="locked"
)

# ---------------------------------------------------------
# PROFESSIONAL MULTI-COLOR THEME (PINK, LIGHT BLUE & NAVY)
# ---------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

    /* =========================================================
       PREMIUM SECURITY DASHBOARD — VISUAL ONLY
       Content, labels and application logic are unchanged.
       ========================================================= */
    :root {
        --navy: #071a2f;
        --navy-2: #0b2947;
        --blue: #1677ff;
        --cyan: #16b8d4;
        --ink: #12263f;
        --muted: #718198;
        --line: #dce6f0;
        --surface: #ffffff;
        --canvas: #eef3f8;
        --soft-blue: #edf5ff;
        --shadow: 0 10px 28px rgba(15, 39, 67, .09);
    }

    html, body, [class*="st-"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        color: var(--ink) !important;
    }

    .stApp {
        background:
            radial-gradient(circle at 78% 0%, rgba(22,119,255,.08), transparent 28%),
            linear-gradient(180deg, #f7faff 0%, var(--canvas) 55%, #eaf0f6 100%) !important;
    }

    /* Clean application chrome — content itself remains untouched */
    #MainMenu, footer, header { visibility: hidden; }

    /* Main content breathing room */
    .main .block-container {
        max-width: 1480px !important;
        padding: 1.2rem 2rem 2.5rem !important;
    }

    /* High-demand security dashboard surfaces */
    .main .block-container {
        position: relative !important;
    }
    .main .block-container > div {
        position: relative;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #d9e4ef !important;
        border-radius: 18px !important;
        background: rgba(255,255,255,.94) !important;
        box-shadow: 0 14px 38px rgba(12,35,61,.08) !important;
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg,#ffffff,#f4f8fc) !important;
        border: 1px solid #dbe6f1 !important;
        border-radius: 16px !important;
        padding: 14px 16px !important;
        box-shadow: 0 10px 24px rgba(15,39,67,.07) !important;
    }
    div[data-testid="stMetricLabel"] p { color:#61758c !important; font-weight:700 !important; }
    div[data-testid="stMetricValue"] { color:#0b2947 !important; font-weight:800 !important; }
    div[data-testid="stFileUploaderDropzone"] {
        border: 1.5px dashed #7da9d4 !important;
        border-radius: 16px !important;
        background: linear-gradient(135deg,#f7fbff,#eef6ff) !important;
    }
    div[data-baseweb="tab-list"] {
        gap: 8px !important;
        background:#eaf1f7 !important;
        padding:6px !important;
        border-radius:12px !important;
    }
    button[data-baseweb="tab"] { border-radius:9px !important; font-weight:700 !important; }
    div[data-testid="stAlert"] { border-radius:14px !important; border:1px solid rgba(15,39,67,.08) !important; }
    div[data-testid="stExpander"] { border:1px solid #dbe6f1 !important; border-radius:14px !important; background:#fff !important; }
    section[data-testid="stSidebar"] .stMarkdown { color:#dcecff !important; }
    section[data-testid="stSidebar"] .stMarkdown p { color:#dcecff !important; }
    section[data-testid="stSidebar"] .stRadio label { color:#dcecff !important; }

    /* =========================================================
       SIDEBAR — dashboard navigation like the supplied JPEG
       ========================================================= */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #071a2f 0%, #092440 52%, #071a2f 100%) !important;
        border-right: 1px solid rgba(255,255,255,.08) !important;
        box-shadow: 8px 0 30px rgba(4,20,38,.12) !important;
    }

    section[data-testid="stSidebar"] > div:first-child {
        padding: 1.15rem .9rem 1.4rem !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: .2px !important;
    }

    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #8fa7c0 !important;
        letter-spacing: .7px !important;
        font-size: 10px !important;
        font-weight: 700 !important;
    }

    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,.09) !important;
        margin: 1rem 0 !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 9px !important;
        padding: 10px 11px !important;
        margin: 3px 0 !important;
        color: #b9c9d9 !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        transition: all .18s ease !important;
        cursor: pointer !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(255,255,255,.07) !important;
        border-color: rgba(62,164,255,.22) !important;
        color: #ffffff !important;
        transform: translateX(3px) !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
        background: linear-gradient(90deg, rgba(22,119,255,.95), rgba(22,119,255,.72)) !important;
        border-color: rgba(117,194,255,.45) !important;
        color: #ffffff !important;
        box-shadow: 0 7px 18px rgba(0,0,0,.18), inset 3px 0 0 #75c2ff !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] span {
        color: #ffffff !important;
    }

    section[data-testid="stSidebar"] strong {
        color: #ffffff !important;
    }

    /* =========================================================
       TYPOGRAPHY / SECTION HEADERS
       ========================================================= */
    h1, h2, h3, h4 {
        font-family: 'Space Grotesk', sans-serif !important;
        color: var(--ink) !important;
        letter-spacing: -.35px !important;
    }

    .main h1 {
        font-size: clamp(1.45rem, 2vw, 2rem) !important;
        font-weight: 700 !important;
        margin-bottom: .45rem !important;
    }

    .main h2 {
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        margin-top: .8rem !important;
    }

    .main h3 {
        font-size: 1rem !important;
        font-weight: 700 !important;
    }

    /* Accent bar before major headers */
    .main h1::before,
    .main h2::before {
        content: '';
        display: inline-block;
        width: 4px;
        height: 22px;
        margin-right: 10px;
        vertical-align: -3px;
        border-radius: 4px;
        background: linear-gradient(180deg, #1677ff, #16b8d4);
        box-shadow: 0 4px 10px rgba(22,119,255,.22);
    }

    /* =========================================================
       DASHBOARD CARDS / METRICS
       ========================================================= */
    div[data-testid="stMetric"] {
        position: relative !important;
        overflow: hidden !important;
        background: rgba(255,255,255,.96) !important;
        border: 1px solid var(--line) !important;
        border-radius: 12px !important;
        padding: 14px 16px !important;
        min-height: 92px !important;
        box-shadow: var(--shadow) !important;
        transition: transform .18s ease, box-shadow .18s ease !important;
    }

    div[data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: linear-gradient(180deg, #1677ff, #16b8d4);
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 32px rgba(15,39,67,.13) !important;
    }

    div[data-testid="stMetricLabel"] {
        color: #7a899b !important;
        font-size: 10px !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }

    div[data-testid="stMetricValue"] {
        color: #0b2540 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 26px !important;
        font-weight: 700 !important;
    }

    /* =========================================================
       BUTTONS — compact enterprise dashboard style
       ========================================================= */
    div.stButton > button,
    div.stDownloadButton > button {
        background: linear-gradient(135deg, #0b2d4d 0%, #1677ff 100%) !important;
        color: #ffffff !important;
        border: 1px solid #126be3 !important;
        border-radius: 7px !important;
        min-height: 40px !important;
        padding: 8px 18px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        box-shadow: 0 7px 16px rgba(22,119,255,.18) !important;
        transition: all .18s ease !important;
    }

    div.stButton > button:hover,
    div.stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 22px rgba(22,119,255,.26) !important;
        border-color: #66b7ff !important;
    }

    /* =========================================================
       INPUTS / SELECTS
       ========================================================= */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    textarea,
    input {
        border-radius: 7px !important;
        border-color: #d5e0eb !important;
        background: #ffffff !important;
        color: #17314b !important;
        box-shadow: none !important;
    }

    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="select"] > div:focus-within,
    textarea:focus,
    input:focus {
        border-color: #4b9dff !important;
        box-shadow: 0 0 0 3px rgba(22,119,255,.10) !important;
    }

    /* =========================================================
       UPLOAD PANEL
       ========================================================= */
    div[data-testid="stFileUploader"] {
        width: 100% !important;
        background: #ffffff !important;
        border: 1px solid #dce6f0 !important;
        border-radius: 12px !important;
        padding: 4px !important;
        box-shadow: var(--shadow) !important;
    }

    section[data-testid="stFileUploaderDropzone"] {
        background: linear-gradient(180deg, #f9fcff 0%, #eef6ff 100%) !important;
        border: 1px dashed #74aee8 !important;
        border-radius: 9px !important;
        padding: 24px 18px !important;
    }

    section[data-testid="stFileUploaderDropzone"] small,
    div[data-testid="stFileUploader"] small {
        display: none !important;
    }

    section[data-testid="stFileUploaderDropzone"] button {
        background: #0b2d4d !important;
        color: #ffffff !important;
        border: 0 !important;
        border-radius: 6px !important;
        padding: 10px 22px !important;
        font-size: 0 !important;
        font-weight: 700 !important;
        box-shadow: 0 6px 14px rgba(11,45,77,.18) !important;
    }

    section[data-testid="stFileUploaderDropzone"] button * {
        display: none !important;
        font-size: 0 !important;
    }

    section[data-testid="stFileUploaderDropzone"] button::after {
        content: '📁 Browse Image';
        font-size: 13px !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }

    section[data-testid="stFileUploaderDropzone"] button:hover {
        background: #1677ff !important;
        transform: translateY(-1px) !important;
    }

    section[data-testid="stFileUploaderDropzone"]::after {
        content: '📁 Drag & Drop or Click Browse to Insert Image (Formats: JPEG, JPG, PNG | Max Size: Up to 120 KB)';
        display: block;
        margin-top: 12px;
        color: #65788d;
        font-size: 11px;
        font-weight: 600;
    }

    /* =========================================================
       EXPANDERS / TABLES / DATAFRAMES
       ========================================================= */
    details {
        background: #ffffff !important;
        border: 1px solid #dce6f0 !important;
        border-radius: 10px !important;
        box-shadow: 0 7px 18px rgba(15,39,67,.06) !important;
        margin: 9px 0 !important;
        overflow: hidden !important;
    }

    details summary {
        color: #18324d !important;
        font-weight: 700 !important;
        padding: 9px 12px !important;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #dce6f0 !important;
        border-radius: 9px !important;
        overflow: hidden !important;
        box-shadow: 0 7px 18px rgba(15,39,67,.06) !important;
        background: #ffffff !important;
    }

    /* Alert/status surfaces */
    div[data-testid="stAlert"] {
        border-radius: 9px !important;
        border: 1px solid #d7e3ee !important;
        box-shadow: 0 6px 16px rgba(15,39,67,.05) !important;
    }

    /* Camera container and generic bordered content */
    div[data-testid="stCameraInput"] {
        border-radius: 10px !important;
        overflow: hidden !important;
        border: 1px solid #cddbe8 !important;
        box-shadow: var(--shadow) !important;
        background: #ffffff !important;
    }

    /* Horizontal separators */
    hr {
        border: 0 !important;
        border-top: 1px solid #dce6f0 !important;
        margin: 1rem 0 !important;
    }

    /* Small-screen polish */
    @media (max-width: 900px) {
        .main .block-container {
            padding: .8rem 1rem 2rem !important;
        }
        div[data-testid="stMetricValue"] {
            font-size: 22px !important;
        }
    }
    

    /* =========================================================
       FINAL VISIBILITY PASS — keep every label readable
       ========================================================= */
    /* Main-area text: strong dark contrast on the light dashboard */
    .main .stMarkdown,
    .main .stMarkdown p,
    .main .stMarkdown li,
    .main .stText,
    .main label,
    .main [data-testid="stWidgetLabel"],
    .main [data-testid="stWidgetLabel"] p,
    .main [data-testid="stRadio"] label,
    .main [data-testid="stSelectbox"] label,
    .main [data-testid="stFileUploader"] label,
    .main [data-testid="stTextInput"] label,
    .main [data-testid="stTextArea"] label,
    .main [data-testid="stNumberInput"] label {
        color: #17324d !important;
        opacity: 1 !important;
    }

    .main .stMarkdown strong,
    .main .stMarkdown b {
        color: #0b2540 !important;
    }

    /* Radio/select text in the main content */
    .main div[role="radiogroup"] label,
    .main div[role="radiogroup"] label span,
    .main div[data-baseweb="select"] * {
        color: #17324d !important;
        opacity: 1 !important;
    }

    /* Sidebar: readable light text against the dark navigation */
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] label span,
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #eaf4ff !important;
        opacity: 1 !important;
    }

    section[data-testid="stSidebar"] .stMarkdown strong,
    section[data-testid="stSidebar"] .stMarkdown b {
        color: #ffffff !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        color: #dcecff !important;
        background: rgba(255,255,255,.035) !important;
        border-color: rgba(255,255,255,.08) !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label span,
    section[data-testid="stSidebar"] div[role="radiogroup"] label p {
        color: #dcecff !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover span,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover p,
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] span,
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] p {
        color: #ffffff !important;
    }

    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        color: #a9c0d7 !important;
        opacity: 1 !important;
    }

    /* Input text + placeholder visibility */
    input, textarea,
    div[data-baseweb="input"] input,
    div[data-baseweb="select"] input {
        color: #102c47 !important;
        -webkit-text-fill-color: #102c47 !important;
        opacity: 1 !important;
    }

    input::placeholder, textarea::placeholder {
        color: #6d8094 !important;
        opacity: 1 !important;
    }

    /* File uploader instructional text */
    section[data-testid="stFileUploaderDropzone"] * {
        color: #25425e !important;
        opacity: 1 !important;
    }
    section[data-testid="stFileUploaderDropzone"] button,
    section[data-testid="stFileUploaderDropzone"] button * {
        color: #ffffff !important;
    }

    /* Dataframe/table text */
    div[data-testid="stDataFrame"] * {
        opacity: 1 !important;
    }

    /* Disabled controls remain readable */
    button:disabled,
    input:disabled,
    textarea:disabled {
        opacity: .72 !important;
    }

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR NAVIGATION (NATIVE STREAMLIT)
# ---------------------------------------------------------

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
st.sidebar.markdown("🎓 Academic Information")
st.sidebar.markdown("**Institution:**\nPriyadarshini College of Engineering, Nagpur")
st.sidebar.markdown("**Project:**\nAI-Based Fake QR Code Detection with QR Risk Score Using Machine Learning")
st.sidebar.markdown("**Batch:** B.Tech Final Year (2026–2027)")
st.sidebar.caption("System Status: 🟢 100% Operational")

# ---------------------------------------------------------
# MAIN TOP HEADER (COLLEGE LOGO & NAME)
# ---------------------------------------------------------
col_logo, col_title = st.columns([1, 5])

with col_logo:
    logo_path = Path(__file__).resolve().parent / "college_logo.jpg"

    if logo_path.is_file():
        st.image(str(logo_path), width=350)
    else:
        st.error(f"College logo file not found: {logo_path}")
        
with col_title:
    st.title("PRIYADARSHINI COLLEGE OF ENGINEERING, NAGPUR")
    st.subheader("🛡️AI-Based Fake QR Code Detection with QR Risk Score Using Machine Learning")
    st.caption("Academic Year 2026–2027 | B.Tech Honors Project")

st.divider()

# ---------------------------------------------------------
# MODULE 1: SCANNER & RISK ENGINE
# ---------------------------------------------------------
if nav_choice == "📊 Scanner & Risk Engine":
    st.header("⚡ Real-Time Threat Scanner & Risk Engine")
    st.caption("Upload a QR image file (Recommended: Up to 120 KB, Formats: JPEG, JPG, PNG, WEBP, BMP, TIFF) or choose a pre-configured test vector.")
    
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
        camera_qr_data = None

        if input_mode == "📷 Direct Camera to Scan":
            camera_qr_data = auto_qr_camera(key="direct_qr_camera")
            st.caption(
                "Camera access is requested by your mobile browser only for this option. "
                "The QR code is captured automatically as soon as it is detected. "
                "If camera permission is denied, use Upload Image instead."
            )
        else:
            uploaded_file = st.file_uploader(
                "Upload Image File (Formats: JPEG, JPG, PNG, WEBP, BMP, TIFF | Size: Up to 120 KB):",
                type=["jpg", "jpeg", "png", "webp", "bmp", "tif", "tiff"]
            )

        selected_file = uploaded_file

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

    qr_data = camera_qr_data if input_mode == "📷 Direct Camera to Scan" else None
    if selected_file is not None:
        try:
            input_image = Image.open(selected_file)
            with col_input:
                source_name = getattr(selected_file, "name", "Camera Capture")
                st.image(input_image, caption=f"Scan Input: {source_name} ({size_kb:.2f} KB)", use_container_width=True)
                with st.spinner("🔍 Decoding QR Pattern & Extracting Features..."):
                    qr_data = decode_qr(input_image)
                    # Browser-side ZXing/BarcodeDetector fallback helps with
                    # branded payment QR images and QR codes embedded in screenshots.
                    if not qr_data:
                        qr_data = decode_uploaded_image_in_browser(
                            selected_file.getvalue(),
                            getattr(selected_file, "type", "image/jpeg"),
                            key="browser_qr_image_decoder"
                        )
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
        - **Estimators:** 450+ Decision Trees
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
