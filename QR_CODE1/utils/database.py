import sqlite3
import os
import csv
import json
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "scan_history.db")
SELF_TRAINING_FILE = os.path.join(PROJECT_ROOT, "data", "high_risk_samples.csv")
RETRAIN_STATE_FILE = os.path.join(PROJECT_ROOT, "data", "retraining_state.json")
RETRAIN_THRESHOLD = 10


def get_connection():
    """Get connection to SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize scan history table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            qr_data TEXT NOT NULL,
            qr_type TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            reasons TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def _ensure_self_training_file():
    os.makedirs(os.path.dirname(SELF_TRAINING_FILE), exist_ok=True)
    if not os.path.exists(SELF_TRAINING_FILE):
        with open(SELF_TRAINING_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["data", "label", "source", "timestamp"])


def _unique_high_risk_count():
    _ensure_self_training_file()
    with open(SELF_TRAINING_FILE, "r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return len({row["data"] for row in rows if row.get("data")})


def add_scan_record(qr_data, qr_type, risk_score, risk_level, reasons_list):
    """Save every scan automatically; high-risk payloads are also queued for self-training."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reasons_str = " | ".join(reasons_list) if isinstance(reasons_list, list) else str(reasons_list)

    cursor.execute("""
        INSERT INTO scan_logs (timestamp, qr_data, qr_type, risk_score, risk_level, reasons)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (timestamp, qr_data, qr_type, risk_score, risk_level, reasons_str))

    conn.commit()
    conn.close()

    # Automatically retain unique HIGH-RISK payloads for the next retraining cycle.
    if risk_level == "High Risk":
        _ensure_self_training_file()
        existing = set()
        with open(SELF_TRAINING_FILE, "r", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("data"):
                    existing.add(row["data"])

        if qr_data not in existing:
            with open(SELF_TRAINING_FILE, "a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([qr_data, 1, "auto_high_risk_prediction", timestamp])

    # Check AFTER saving the current scan so the threshold sample is included
    # in the model training. Training data is retained permanently until reset.
    if should_auto_retrain():
        try:
            from model.train_model import train_model
            train_model()
            mark_retraining_complete()
        except Exception:
            # A training failure must not prevent the scan from being stored.
            pass


def get_self_training_count():
    """Return the total number of unique high-risk samples retained since reset."""
    return _unique_high_risk_count()


def _get_last_retrained_count():
    if not os.path.exists(RETRAIN_STATE_FILE):
        return 0
    try:
        with open(RETRAIN_STATE_FILE, "r", encoding="utf-8") as f:
            return int(json.load(f).get("last_retrained_count", 0))
    except (ValueError, TypeError, json.JSONDecodeError, OSError):
        return 0


def should_auto_retrain():
    """Retrain after each additional block of 10 unique high-risk samples.

    Samples are NEVER deleted after retraining. The counter only records how
    many retained samples were already incorporated into the latest model.
    """
    current = get_self_training_count()
    last = _get_last_retrained_count()
    return current >= RETRAIN_THRESHOLD and (current - last) >= RETRAIN_THRESHOLD


def mark_retraining_complete():
    """Mark all currently retained samples as incorporated; do NOT delete them."""
    count = get_self_training_count()
    os.makedirs(os.path.dirname(RETRAIN_STATE_FILE), exist_ok=True)
    with open(RETRAIN_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_retrained_count": count}, f, indent=2)


def get_all_scans():
    """Fetch all scan logs ordered by latest first."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scan_logs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def clear_scan_history():
    """Reset scan history, retained self-training data, and retraining state."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scan_logs")
    conn.commit()
    conn.close()

    if os.path.exists(SELF_TRAINING_FILE):
        os.remove(SELF_TRAINING_FILE)
    if os.path.exists(RETRAIN_STATE_FILE):
        os.remove(RETRAIN_STATE_FILE)


def get_scan_stats():
    """Return aggregate counts used by the Threat Analytics dashboard."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN risk_level = 'Safe' THEN 1 ELSE 0 END) AS safe,
            SUM(CASE WHEN risk_level = 'Medium Risk' THEN 1 ELSE 0 END) AS medium,
            SUM(CASE WHEN risk_level = 'High Risk' THEN 1 ELSE 0 END) AS high
        FROM scan_logs
    """)
    row = cursor.fetchone()
    conn.close()
    return {
        "total": int(row["total"] or 0),
        "safe": int(row["safe"] or 0),
        "medium": int(row["medium"] or 0),
        "high": int(row["high"] or 0),
    }
