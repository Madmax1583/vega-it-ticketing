import io
import os
import base64
import hashlib
import sqlite3
import bcrypt
from datetime import datetime, time
from pathlib import Path

def find_logo_filename(filename: str):
    candidates = [
        filename,
        os.path.join(os.getcwd(), filename),
        os.path.join(os.getcwd(), 'assets', filename),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), filename) if '__file__' in globals() else None,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', filename) if '__file__' in globals() else None,
    ]
    for path in candidates:
        if path and os.path.exists(path):
            return path
    return None

def image_to_base64(path: str) -> str:
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

import altair as alt
import pandas as pd
import streamlit as st
from supabase import create_client

# ==========================================
# 1. STREAMLIT CONFIG & GLOBAL STYLE SHEET
# ==========================================
st.set_page_config(
    page_title="Vega & Knitpro IT Operations Dashboard",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    :root {
        --bg: #0b1020;
        --panel: #111827;
        --panel-soft: #0f172a;
        --panel-muted: #131d34;
        --border: #273449;
        --text: #f8fafc;
        --muted: #94a3b8;
        --accent: #ef4444;
        --accent-soft: rgba(239, 68, 68, 0.12);
        --success: #22c55e;
        --warning: #f59e0b;
        --info: #3b82f6;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    .app-banner {
        background: linear-gradient(135deg, #0f172a 0%, #111827 100%);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 18px 22px;
        margin-bottom: 12px;
    }

    .app-title {
        color: var(--text);
        font-size: 1.85rem;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .app-subtitle {
        color: var(--muted);
        font-size: 0.95rem;
    }

    .section-note {
        background: var(--panel-muted);
        border: 1px solid rgba(59,130,246,0.25);
        border-radius: 12px;
        padding: 12px 14px;
        color: var(--text);
        margin-bottom: 10px;
        font-size: 0.93rem;
    }

    .panel-card, .summary-card, .metric-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 14px 18px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    .metric-card { backdrop-filter: blur(8px); }

    .metric-label, .sum-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--muted);
        margin-bottom: 4px;
    }

    .metric-value, .sum-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text);
    }

    .metric-sub {
        font-size: 0.78rem;
        margin-top: 4px;
    }

    .summary-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0,1fr));
        gap: 12px 16px;
    }

    .span-2 { grid-column: span 2; }

    .status-chip {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        border: 1px solid transparent;
        white-space: nowrap;
    }
    .status-open { color: #fecaca; background: rgba(239,68,68,0.15); border-color: rgba(239,68,68,0.3); }
    .status-progress { color: #bfdbfe; background: rgba(59,130,246,0.15); border-color: rgba(59,130,246,0.3); }
    .status-hold { color: #fde68a; background: rgba(245,158,11,0.15); border-color: rgba(245,158,11,0.3); }
    .status-resolved { color: #bbf7d0; background: rgba(34,197,94,0.15); border-color: rgba(34,197,94,0.3); }

    .queue-shell, .danger-box {
        background: rgba(15, 23, 42, 0.72);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 14px;
        margin-top: 8px;
    }

    .danger-box h4 { margin: 0 0 8px 0; color: #fecaca; }
    .mini-note { color: var(--muted); font-size: 0.84rem; margin-bottom: 0.5rem; }

    .table-scroll {
        width: 100%;
        overflow-x: auto;
        border: 1px solid var(--border);
        border-radius: 12px;
        background: var(--panel-soft);
    }
    .table-scroll table {
        width: 100%;
        min-width: 760px;
        border-collapse: collapse;
    }
    .table-scroll th, .table-scroll td {
        padding: 10px 12px;
        border-bottom: 1px solid rgba(39, 52, 73, 0.8);
        text-align: left;
        font-size: 0.86rem;
        vertical-align: top;
    }
    .table-scroll th {
        background: #162033;
        color: #e5eefc;
        font-size: 0.78rem;
        text-transform: uppercase;
        position: sticky;
        top: 0;
    }
    .compact-table table { min-width: 640px; }
    .compact-table th, .compact-table td { padding: 8px 10px; font-size: 0.84rem; }

    div.stButton > button:first-child,
    div[data-testid="stDownloadButton"] > button:first-child {
        background-color: var(--accent);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }

    @media (max-width: 900px) {
        .summary-grid { grid-template-columns: 1fr; }
        .span-2 { grid-column: span 1; }
    }

    .stApp [data-testid="stAppViewContainer"] {background: linear-gradient(135deg, #09111f 0%, #0b1426 55%, #0a1220 100%);}    
    .stApp [data-testid="stHeader"] {background: rgba(9, 17, 31, 0.35);}    
    section.main > div {max-width: 1460px; padding-top: 1.6rem;}    
    .login-panel-left {min-height: 84vh; border-radius: 30px; padding: 48px 42px; display:flex; flex-direction:column; justify-content:space-between; background: radial-gradient(circle at 10% 12%, rgba(34,211,238,0.20), transparent 22%), radial-gradient(circle at 78% 22%, rgba(59,130,246,0.16), transparent 26%), radial-gradient(circle at 64% 86%, rgba(239,68,68,0.14), transparent 22%), linear-gradient(160deg, #0b223d 0%, #0c1c33 48%, #0f1a2b 100%); border: 1px solid rgba(148,163,184,0.14); box-shadow: 0 28px 64px rgba(0,0,0,0.30); position: relative; overflow: hidden;}    
    .login-panel-left::after {content:''; position:absolute; inset:auto -20% -18% auto; width:280px; height:280px; background: radial-gradient(circle, rgba(34,211,238,0.18), transparent 65%); filter: blur(8px);}    
    .login-eyebrow {font-size: 0.92rem; color:#bfdbfe; letter-spacing:0.08em; text-transform:uppercase; margin-bottom: 1rem;}    
    .login-brand-lockup img {display:block; margin-bottom: 14px;}    
    .login-title-sub {font-size:1.32rem; font-weight:600; color:#f8fafc; max-width:30ch; line-height:1.45; margin-top: 18px;}    
    .login-note {font-size:0.98rem; color:#cbd5e1; max-width:48ch; line-height:1.7;}    
    .login-panel-right {min-height: 84vh; display:flex; align-items:center; justify-content:center;}    
    .login-form-shell {width:min(100%, 520px); padding: 1.25rem 0.5rem 1.25rem 0.75rem;}    
    .login-accent-line {width:72px; height:4px; border-radius:999px; background: linear-gradient(90deg, #22d3ee 0%, #3b82f6 55%, #ef4444 100%); margin-bottom: 1.4rem;}    
    .login-mini {color:#8fb7ff; font-size:0.88rem; font-weight:600; letter-spacing:0.06em; text-transform:uppercase; margin-bottom: 0.7rem;}    
    .login-h1 {font-size: 2.2rem; font-weight: 750; color:#ffffff; margin-bottom: 0.35rem;}    
    .login-subcopy {color:#d1d5db; font-size:1rem; line-height:1.6; margin-bottom: 1.7rem; max-width:34ch;}    
    .login-support {margin-top:14px; color:#cbd5e1; font-size:0.92rem;}    
    .login-support .linkish, .login-footer .linkish {color:#7dd3fc; font-weight:600;}    
    .login-footer {margin-top: 1.4rem; display:flex; gap:14px; flex-wrap:wrap; font-size:0.84rem; color:#94a3b8;}    
    div[data-testid="stTextInput"] {margin-bottom: 1rem;}    
    div[data-testid="stTextInput"] label p {color:#e5eefc !important; font-weight:600; font-size:0.95rem;}    
    div[data-testid="stTextInput"] input {background: linear-gradient(180deg, #121a28 0%, #182132 100%) !important; border:1px solid #263248 !important; color:#f8fafc !important; border-radius:14px !important; min-height:3.2rem !important; box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);}    
    div[data-testid="stTextInput"] input::placeholder {color:#7c8799 !important;}    
    div[data-testid="stTextInput"] input:focus {border-color:#38bdf8 !important; box-shadow:0 0 0 1px rgba(56,189,248,0.55), 0 0 0 4px rgba(56,189,248,0.12) !important;}    
    div.stButton {margin-top: 0.5rem;}    
    div.stButton > button {background: linear-gradient(90deg, #0ea5e9 0%, #2563eb 58%, #ef4444 100%) !important; color:white !important; border:none !important; border-radius:14px !important; height:3.15rem !important; font-weight:700 !important; box-shadow: 0 14px 28px rgba(37,99,235,0.22) !important;}    
    div.stButton > button:hover {filter: brightness(1.04); transform: translateY(-1px);}    
    div.stButton > button:active {transform: translateY(0);}    
    @media (max-width: 900px){section.main > div{padding-top:0.8rem;} .login-panel-left,.login-panel-right{min-height:auto; padding:24px 20px;} .login-form-shell{width:100%; padding:0.5rem 0 1rem 0;} .login-h1{font-size:1.8rem;} .login-title-sub{font-size:1.12rem;}}    

    div[data-testid="column"]:has(.login-panel-right) {display:flex; align-items:center; min-height:84vh;}
    div[data-testid="column"]:has(.login-panel-left) {display:flex; min-height:84vh;}
    .login-panel-right {width:100%; min-height:84vh; display:flex !important; align-items:center !important; justify-content:center !important;}
    .login-form-shell {width:min(100%, 560px); margin-inline:auto; background: linear-gradient(180deg, rgba(16,24,39,0.82) 0%, rgba(17,24,39,0.70) 100%); border:1px solid rgba(56,189,248,0.14); border-radius:24px; padding:32px 28px 26px 28px; box-shadow:0 24px 60px rgba(0,0,0,0.28); backdrop-filter: blur(10px);}
    .login-title-sub {font-size:1.38rem; max-width:28ch;}
    .login-note {max-width:44ch;}
    @media (max-width: 900px){div[data-testid="column"]:has(.login-panel-right), div[data-testid="column"]:has(.login-panel-left){min-height:auto;} .login-form-shell{border-radius:18px; padding:24px 20px;}}

    div[data-testid="column"]:has(.login-panel-right) {display:flex; align-items:center; justify-content:center; min-height:84vh;}
    div[data-testid="column"]:has(.login-panel-right) > div {width:100%; display:flex; align-items:center; justify-content:center;}
    div[data-testid="column"]:has(.login-panel-left) {display:flex; align-items:stretch; min-height:84vh;}
    .login-panel-left {min-height: 82vh;}
    .login-panel-right {width:100%; min-height:82vh; display:flex !important; align-items:center !important; justify-content:center !important; padding-top:0 !important;}
    .login-form-shell {width:min(100%, 560px); margin-inline:auto; margin-top:0; transform: translateY(-18px);} 
    .login-panel-right [data-testid="stTextInput"], .login-panel-right .stButton {width:100%;}
    .login-brand-lockup {margin-bottom: 22px;}
    .login-note {padding-top: 1.5rem;}
    @media (max-width: 900px){.login-form-shell{transform:none;} .login-panel-left,.login-panel-right{min-height:auto;}}

    div[data-testid="column"] .stContainer:has(input) {margin-top: -230px !important; position: relative; z-index: 5;}
    div[data-testid="column"] .stContainer:has(input) > div {background: transparent !important;}
    .login-panel-right {position: relative;}
    @media (max-width: 900px){div[data-testid="column"] .stContainer:has(input) {margin-top: 0 !important;}}

    .login-panel-right + div, .login-support, .login-footer {position: relative; z-index: 4;}
    @media (min-width: 901px){div[data-testid="stHorizontalBlock"]:has(.login-mini) {margin-top: 15vh;} }

    .block-container {max-width: 1440px; padding-top: 1.2rem;}
    .app-banner {background: linear-gradient(180deg, rgba(15,23,42,0.90) 0%, rgba(17,24,39,0.86) 100%); border:1px solid rgba(56,189,248,0.14); box-shadow:0 22px 52px rgba(0,0,0,0.22); border-radius:18px;}
    .app-title {color:#f8fafc; letter-spacing:-0.02em;}
    .app-subtitle {color:#93c5fd;}
    .section-note {background: linear-gradient(180deg, rgba(15,23,42,0.90) 0%, rgba(19,29,52,0.84) 100%); border:1px solid rgba(59,130,246,0.24); color:#e5eefc; border-radius:14px;}
    .panel-card, .summary-card, .metric-card, .table-card {background: linear-gradient(180deg, rgba(15,23,42,0.90) 0%, rgba(17,24,39,0.82) 100%) !important; border:1px solid rgba(56,189,248,0.12) !important; box-shadow:0 18px 44px rgba(0,0,0,0.18); border-radius:18px !important;}
    .panel-card h3, .summary-card h3, .metric-title, .metric-value {color:#f8fafc !important;}
    .metric-subtext, .panel-card p, .summary-card p {color:#cbd5e1 !important;}
    .stTabs [data-baseweb="tab-list"] {gap: 10px; background: rgba(12,18,32,0.45); padding: 6px; border:1px solid rgba(56,189,248,0.10); border-radius: 14px;}
    .stTabs [data-baseweb="tab"] {height: 44px; border-radius: 10px; color:#cbd5e1; padding: 0 18px;}
    .stTabs [aria-selected="true"] {background: linear-gradient(90deg, rgba(14,165,233,0.18) 0%, rgba(37,99,235,0.18) 65%, rgba(239,68,68,0.16) 100%); color:#ffffff !important;}
    div[data-testid="stMetric"] {background: linear-gradient(180deg, rgba(15,23,42,0.90) 0%, rgba(17,24,39,0.82) 100%); border:1px solid rgba(56,189,248,0.12); padding:16px 18px; border-radius:18px; box-shadow:0 18px 44px rgba(0,0,0,0.16);}
    div[data-testid="stMetricLabel"] {color:#93c5fd !important;}
    div[data-testid="stMetricValue"] {color:#f8fafc !important;}
    .stDataFrame, div[data-testid="stTable"] {border-radius:18px; overflow:hidden; border:1px solid rgba(56,189,248,0.12);} 
    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"], div[data-testid="stTextArea"] textarea, div[data-testid="stNumberInput"] input, div[data-testid="stDateInput"] input {background: linear-gradient(180deg, #121a28 0%, #182132 100%) !important; border:1px solid #263248 !important; color:#f8fafc !important; border-radius:14px !important;}
    div[data-testid="stTextInput"] label p, div[data-testid="stSelectbox"] label p, div[data-testid="stTextArea"] label p, div[data-testid="stNumberInput"] label p, div[data-testid="stDateInput"] label p {color:#dbeafe !important; font-weight:600;}
    div.stButton > button, button[kind="primary"] {background: linear-gradient(90deg, #0ea5e9 0%, #2563eb 58%, #ef4444 100%) !important; color:white !important; border:none !important; border-radius:14px !important; font-weight:700 !important; box-shadow:0 14px 28px rgba(37,99,235,0.20) !important;}
    div.stButton > button:hover {filter: brightness(1.04);}
    .stDownloadButton > button {background: rgba(14,165,233,0.12) !important; color:#e5eefc !important; border:1px solid rgba(56,189,248,0.18) !important; border-radius:14px !important;}
    .stAlert {background: linear-gradient(180deg, rgba(15,23,42,0.94) 0%, rgba(19,29,52,0.90) 100%) !important; color:#e5eefc !important; border:1px solid rgba(56,189,248,0.14) !important; border-radius:16px !important;}
    hr {border-color: rgba(56,189,248,0.10) !important;}
</style>
""",
    unsafe_allow_html=True,
)

def get_db_connection():
    conn = sqlite3.connect("it_ops.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    role TEXT NOT NULL,
    password_hash TEXT,
    active INTEGER DEFAULT 1,
    must_change_password INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""
TASKS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    assigned_by TEXT,
    assigned_to TEXT,
    priority TEXT DEFAULT 'Medium',
    status TEXT DEFAULT 'Open',
    progress INTEGER DEFAULT 0,
    due_date TEXT,
    vendor_flag INTEGER DEFAULT 0,
    vendor_status TEXT,
    vendor_remark TEXT,
    reminder_date TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""
COMMENTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS task_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    comment TEXT NOT NULL,
    commented_by TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""
NOTIFICATIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    message TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""
VENDOR_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS vendor_followups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL,
    vendor_name TEXT,
    followup_status TEXT DEFAULT 'Pending from Vendor',
    vendor_remark TEXT,
    due_date TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""
DEFAULT_USERS = [
    ("amit", "Amit", "IT Manager"),
    ("satish", "Satish", "IT AM"),
    ("ranjan", "Ranjan", "Sr. Executive"),
    ("priyanshu", "Priyanshu", "IT Executive"),
    ("manish", "Manish", "IT Executive"),
    ("satender", "Mr. Satender Vashisht", "AVP"),
]

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, stored_hash: str, conn=None, username=None) -> bool:
    if not stored_hash:
        return False
    try:
        stored_hash = str(stored_hash)
        if stored_hash.startswith(("$2a$", "$2b$", "$2y$")):
            return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
        legacy_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        if legacy_hash == stored_hash:
            if conn is not None and username:
                upgraded_hash = hash_password(password)
                conn.execute(
                    "UPDATE users SET password_hash=?, updated_at=CURRENT_TIMESTAMP WHERE lower(username)=lower(?)",
                    (upgraded_hash, username),
                )
                conn.commit()
            return True
    except Exception:
        return False
    return False

CHAT_THREADS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS chat_threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    created_by TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""
CHAT_MESSAGES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id INTEGER NOT NULL,
    sender TEXT NOT NULL,
    message TEXT NOT NULL,
    linked_ticket_id INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""
USER_STATUS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS user_status (
    username TEXT PRIMARY KEY,
    display_name TEXT,
    status TEXT DEFAULT 'Available',
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""

def ensure_support_tables(conn):
    conn.execute(USERS_TABLE_SQL)
    conn.execute(TASKS_TABLE_SQL)
    conn.execute(COMMENTS_TABLE_SQL)
    conn.execute(NOTIFICATIONS_TABLE_SQL)
    conn.execute(VENDOR_TABLE_SQL)
    conn.execute(CHAT_THREADS_TABLE_SQL)
    conn.execute(CHAT_MESSAGES_TABLE_SQL)
    conn.execute(USER_STATUS_TABLE_SQL)
    try:
        conn.execute("ALTER TABLE chat_messages ADD COLUMN linked_ticket_id INTEGER")
    except Exception:
        pass
    conn.commit()

def seed_default_users(conn):
    cur = conn.cursor()
    for username, display_name, role in DEFAULT_USERS:
        cur.execute("SELECT id FROM users WHERE lower(username)=lower(?)", (username,))
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO users (username, display_name, role, password_hash, active, must_change_password) VALUES (?, ?, ?, ?, 1, 1)",
                (username, display_name, role, None),
            )
        cur.execute("SELECT username FROM user_status WHERE lower(username)=lower(?)", (username,))
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO user_status (username, display_name, status) VALUES (?, ?, ?)",
                (username, display_name, 'Available'),
            )
    conn.commit()

def init_support_data(conn):
    ensure_support_tables(conn)
    ensure_enterprise_extension_tables(conn)
    globals()["conn_global_for_pdf"] = conn
    seed_default_users(conn)

def get_user_by_username_sqlite(conn, username: str):
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username, display_name, role, password_hash, active, must_change_password FROM users WHERE lower(username)=lower(?)",
        (username,),
    )
    row = cur.fetchone()
    if not row:
        return None
    return {k: row[k] for k in row.keys()}

def normalize_user_record(user):
    if not user:
        return None
    active_val = user.get("active", user.get("is_active", True))
    must_change_val = user.get("mustchangepassword", user.get("must_change_password", user.get("must_change", False)))
    def as_flag(value, default=False):
        if value is None:
            return 1 if default else 0
        if isinstance(value, bool):
            return 1 if value else 0
        s = str(value).strip().lower()
        if s in {"1", "true", "yes", "y", "active"}:
            return 1
        if s in {"0", "false", "no", "n", "inactive"}:
            return 0
        return 1 if default else 0
    return {
        "id": user.get("id"),
        "username": str(user.get("username", user.get("user_name", ""))).strip(),
        "display_name": user.get("displayname") or user.get("display_name") or user.get("name") or str(user.get("username", user.get("user_name", ""))).strip().title(),
        "role": user.get("role", "User"),
        "password_hash": user.get("passwordhash") or user.get("password_hash") or user.get("password"),
        "active": as_flag(active_val, default=True),
        "must_change_password": as_flag(must_change_val, default=False),
    }

def table_exists(name: str) -> bool:
    if not db_connected:
        return False
    try:
        supabase_client.table(name).select("id", count="exact").limit(1).execute()
        return True
    except Exception:
        return False

def seed_supabase_users_if_needed():
    if not db_connected or not table_exists("users"):
        return
    for username, display_name, role in DEFAULT_USERS:
        try:
            existing = supabase_client.table("users").select("id").ilike("username", username).limit(1).execute()
            if existing.data:
                continue
            supabase_client.table("users").insert(
                {
                    "username": username,
                    "displayname": display_name,
                    "role": role,
                    "passwordhash": None,
                    "active": True,
                    "mustchangepassword": True,
                }
            ).execute()
        except Exception:
            pass

def get_user_by_username(conn, username: str):
    clean = str(username).strip()
    if db_connected and table_exists("users"):
        try:
            response = supabase_client.table("users").select("*").ilike("username", clean).limit(1).execute()
            if response.data:
                return normalize_user_record(response.data[0])
        except Exception:
            try:
                response = supabase_client.table("users").select("*").ilike("user_name", clean).limit(1).execute()
                if response.data:
                    return normalize_user_record(response.data[0])
            except Exception:
                pass
    return get_user_by_username_sqlite(conn, clean)

def set_user_password_sqlite(conn, username: str, new_password: str, require_change: int = 0):
    conn.execute(
        "UPDATE users SET password_hash=?, must_change_password=?, updated_at=CURRENT_TIMESTAMP WHERE lower(username)=lower(?)",
        (hash_password(new_password), int(require_change), username),
    )
    conn.commit()

def set_user_password(conn, username: str, new_password: str, require_change: int = 0):
    clean = str(username).strip()
    payload = {
        "passwordhash": hash_password(new_password),
        "mustchangepassword": bool(require_change),
    }
    if db_connected and table_exists("users"):
        try:
            supabase_client.table("users").update(payload).ilike("username", clean).execute()
            return
        except Exception:
            try:
                supabase_client.table("users").update(payload).ilike("user_name", clean).execute()
                return
            except Exception:
                pass
    set_user_password_sqlite(conn, clean, new_password, require_change=require_change)

def authenticate_user(conn, username: str, password: str):
    user = get_user_by_username(conn, username)
    if not user or int(user.get("active", 0) or 0) != 1:
        return None
    stored_hash = user.get("password_hash")
    if not stored_hash:
        return None
    if verify_password(password, stored_hash, conn=conn, username=username):
        refreshed = get_user_by_username(conn, username)
        return refreshed or user
    return None

def current_period_ticket_df(df, freq="Daily"):
    if df is None or df.empty:
        return pd.DataFrame()
    x = df.copy()
    x["date_parsed"] = pd.to_datetime(x.get("date"), errors="coerce")
    x = x.dropna(subset=["date_parsed"])
    if x.empty:
        return pd.DataFrame()
    today = pd.Timestamp.now().normalize()
    if freq == "Monthly":
        x = x[x["date_parsed"].dt.to_period("M") == today.to_period("M")]
    elif freq == "Weekly":
        iso = today.isocalendar()
        x = x[(x["date_parsed"].dt.isocalendar().year == iso.year) & (x["date_parsed"].dt.isocalendar().week == iso.week)]
    else:
        start = today - pd.Timedelta(days=29)
        x = x[x["date_parsed"] >= start]
    return x

@st.cache_resource
def init_supabase():
    if "supabase" not in st.secrets:
        return None
    url = st.secrets["supabase"].get("url", "")
    key = st.secrets["supabase"].get("key", "")
    if not url or not key:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None

supabase_client = init_supabase()
db_connected = supabase_client is not None

TECH_MAP = {
    "Satish": "TECH-01",
    "Priyanshu": "TECH-02",
    "Amit": "TECH-03",
    "Ranjan": "TECH-04",
    "Manish": "TECH-05",
}
OFFICIAL_LOCATIONS = [
    "Sector - 136 Vega", "Knitpro 28-29", "Sector - 155 Vega", "Knitpro - Jaipur",
    "Knitpro 42", "Knitpro 72-73", "Knitpro 75", "Bharat Composite Sector 80", "Vega Sector 80",
]
STATUS_OPTIONS = ["Open", "In Progress", "On Hold - User Busy", "Resolved"]
SERVER_NAMES = ["HRI", "Vega", "Sery", "Rise"]
SERVER_SHEET_MAP = {"HRI": "Sheet 1", "Vega": "Sheet 2", "Sery": "Sheet 3", "Rise": "Sheet 4"}

CATEGORY_MASTER = {
    "LaptopHardware": ["Slow Performance", "Boot Issue", "Keyboard/Mouse", "Display", "Battery/Charging", "Blue Screen", "Upgrade", "Peripheral"],
    "Printer": ["Print Issue", "Scanner Issue", "Driver/Install", "Cartridge/Toner", "Paper Jam", "Network Printer"],
    "EmailOutlook": ["Login Issue", "Configuration", "PST/OST", "Mail Flow", "Migration", "Mailbox Access"],
    "Network": ["Internet", "WiFi", "LAN", "VPN", "Switch/Firewall", "Shared Folder Access"],
    "CCTVCamera": ["Camera Offline", "NVR Issue", "Recording Issue", "Installation", "View Access"],
    "SAP": ["Login Issue", "Client Error", "Access/Role", "Transaction Error", "Print from SAP"],
    "ServerUPS": ["Server Health", "Backup", "UPS Alarm", "Patch/Update", "Attendance Server", "RDP/DNS"],
    "AVSupport": ["Projector", "TV/Display", "OPS", "Meeting Room Setup", "Audio Issue", "VC Support"],
    "AccessControl": ["Biometric", "Door Access", "Attendance Device", "Access Request"],
    "Telephony": ["Phone Dead", "Intercom", "Extension Config", "Voice Quality"],
    "SoftwareSupport": ["Software Install", "License/Renewal", "Application Error", "Update/Patch"],
    "InstallationSetup": ["New Device Setup", "OS Install", "Desktop/Laptop Delivery", "User Handover"],
    "Other": ["Unclassified"]
}

def suggest_subcategory(category, complaint):
    c = str(category)
    text = str(complaint).lower()
    if c == "LaptopHardware":
        if any(k in text for k in ["slow", "hanging", "hang"]): return "Slow Performance"
        if any(k in text for k in ["boot", "startup", "start"]): return "Boot Issue"
        if any(k in text for k in ["keyboard", "mouse", "touchpad"]): return "Keyboard/Mouse"
        if any(k in text for k in ["screen", "display", "monitor"]): return "Display"
        if any(k in text for k in ["battery", "charger", "charging"]): return "Battery/Charging"
        if any(k in text for k in ["blue screen", "bsod"]): return "Blue Screen"
    if c == "Printer":
        if "scan" in text: return "Scanner Issue"
        if any(k in text for k in ["driver", "install"]): return "Driver/Install"
        if any(k in text for k in ["cartridge", "toner"]): return "Cartridge/Toner"
        if "jam" in text: return "Paper Jam"
        return "Print Issue"
    if c == "EmailOutlook":
        if any(k in text for k in ["login", "password"]): return "Login Issue"
        if any(k in text for k in ["pst", "ost"]): return "PST/OST"
        if any(k in text for k in ["migration", "migrate"]): return "Migration"
        if any(k in text for k in ["access", "mailbox"]): return "Mailbox Access"
        return "Configuration"
    if c == "Network":
        if "wifi" in text: return "WiFi"
        if any(k in text for k in ["vpn", "rdp"]): return "VPN"
        if any(k in text for k in ["shared folder", "folder access", "drive access"]): return "Shared Folder Access"
        if any(k in text for k in ["switch", "firewall"]): return "Switch/Firewall"
        if any(k in text for k in ["lan", "cable"]): return "LAN"
        return "Internet"
    if c == "CCTVCamera":
        if "nvr" in text: return "NVR Issue"
        if any(k in text for k in ["record", "playback"]): return "Recording Issue"
        if any(k in text for k in ["install", "new camera"]): return "Installation"
        if "access" in text: return "View Access"
        return "Camera Offline"
    if c == "SAP":
        if any(k in text for k in ["login", "password"]): return "Login Issue"
        if "access" in text: return "Access/Role"
        if "print" in text: return "Print from SAP"
        if any(k in text for k in ["error", "dump"]): return "Transaction Error"
        return "Client Error"
    if c == "ServerUPS":
        if "backup" in text: return "Backup"
        if "ups" in text: return "UPS Alarm"
        if any(k in text for k in ["patch", "update"]): return "Patch/Update"
        if "attendance" in text: return "Attendance Server"
        if any(k in text for k in ["rdp", "dns"]): return "RDP/DNS"
        return "Server Health"
    if c == "AVSupport":
        if "projector" in text: return "Projector"
        if any(k in text for k in ["tv", "display"]): return "TV/Display"
        if "ops" in text: return "OPS"
        if any(k in text for k in ["meeting", "boardroom"]): return "Meeting Room Setup"
        if any(k in text for k in ["audio", "mic", "speaker"]): return "Audio Issue"
        return "VC Support"
    if c == "AccessControl":
        if "biometric" in text: return "Biometric"
        if any(k in text for k in ["door", "access"]): return "Door Access"
        if "attendance" in text: return "Attendance Device"
        return "Access Request"
    if c == "Telephony":
        if any(k in text for k in ["intercom", "extension"]): return "Intercom"
        if any(k in text for k in ["voice", "noise"]): return "Voice Quality"
        if any(k in text for k in ["config", "setting"]): return "Extension Config"
        return "Phone Dead"
    if c == "SoftwareSupport":
        if any(k in text for k in ["install", "setup"]): return "Software Install"
        if any(k in text for k in ["license", "renewal"]): return "License/Renewal"
        if any(k in text for k in ["update", "patch"]): return "Update/Patch"
        return "Application Error"
    if c == "InstallationSetup":
        if any(k in text for k in ["os", "windows"]): return "OS Install"
        if any(k in text for k in ["delivery", "delivered"]): return "Desktop/Laptop Delivery"
        if any(k in text for k in ["handover"]): return "User Handover"
        return "New Device Setup"
    return "Unclassified"

AI_SUGGESTIONS = {
    "CCTV/Camera": {"title_en": "📷 AI Video Infrastructure Diagnostics", "title_hi": "📷 एआई वीडियो इन्फ्रास्ट्रक्चर डायग्नोस्टिक्स", "English": ["Check whether the camera POE switch port light is blinking.", "Ping the camera IP address through CMD to confirm network continuity.", "If NVR shows no video, restart the camera channel or re-login the device."], "Hindi": ["जांचें कि कैमरा POE स्विच पोर्ट की लाइट ब्लिंक कर रही है या नहीं।", "नेटवर्क कनेक्टिविटी जांचने के लिए कैमरा IP एड्रेस को पिंग करें।", "यदि NVR 'No Video' दिखाए, तो कैमरा चैनल रीस्टार्ट या री-लॉगिन करें।"]},
    "Laptop/Hardware": {"title_en": "💻 AI Endpoint Hardware Diagnostics", "title_hi": "💻 एआई एंडपॉइंट हार्डवेयर डायग्नोस्टिक्स", "English": ["Perform a hard reset by disconnecting power and holding the power button for 30 seconds.", "Connect to an external display to isolate panel versus motherboard issues.", "Check Device Manager and reinstall chipset or hardware drivers if needed."], "Hindi": ["पावर डिस्कनेक्ट करके 30 सेकंड तक पावर बटन दबाकर हार्ड रीसेट करें।", "LCD और मदरबोर्ड समस्या अलग करने के लिए बाहरी मॉनिटर लगाएं।", "Device Manager जांचें और आवश्यक होने पर ड्राइवर पुनः इंस्टॉल करें।"]},
    "Email/Outlook": {"title_en": "📧 AI Communication Layer Diagnostics", "title_hi": "📧 एआई कम्यूनिकेशन लेयर डायग्नोस्टिक्स", "English": ["Run outlook.exe /safe to isolate add-in conflicts.", "Check PST or OST file size and compact it if very large.", "Clear Credential Manager entries if password prompts repeat."], "Hindi": ["Add-in conflict जांचने के लिए outlook.exe /safe चलाएं।", "PST या OST फ़ाइल का आकार जांचें और जरूरत हो तो compact करें।", "बार-बार पासवर्ड आने पर Credential Manager entries साफ करें।"]},
    "Printer": {"title_en": "🖨️ AI Print Management Diagnostics", "title_hi": "🖨️ एआई प्रिंट मैनेजमेंट डायग्नोस्टिक्स", "English": ["Verify Printer Properties, configured port, and SNMP setting.", "Restart Print Spooler and clear stuck jobs in the PRINTERS folder.", "Inspect cartridge, rollers, and scanner glass for quality issues."], "Hindi": ["Printer Properties, port configuration और SNMP setting जांचें।", "Print Spooler restart करें और stuck jobs साफ करें।", "कार्ट्रिज, रोलर्स और स्कैनर ग्लास जांचें।"]},
    "SAP": {"title_en": "🏢 AI Enterprise ERP Diagnostics", "title_hi": "🏢 एआई एंटरप्राइज ईआरपी डायग्नोस्टिक्स", "English": ["Verify SAP logon configuration and network reachability.", "Check for locked or hung sessions through SAP tools.", "Repair SAP GUI or clear cache if the client is unstable."], "Hindi": ["SAP logon configuration और network connectivity जांचें।", "Locked या hung sessions जांचें।", "Client unstable होने पर SAP GUI repair या cache clear करें।"]},
    "Network": {"title_en": "🌐 AI Network Routing Diagnostics", "title_hi": "🌐 एआई नेटवर्क राउटिंग डायग्नोस्टिक्स", "English": ["Reset Winsock and inspect the adapter driver for frequent drops.", "Release and renew IP configuration if conflict is suspected.", "Check the SSID and frequency band being used by the device."], "Hindi": ["बार-बार डिस्कनेक्ट होने पर Winsock reset और adapter driver जांचें।", "IP conflict शक होने पर release और renew करें।", "SSID और frequency band की पुष्टि करें।"]},
    "Server/UPS": {"title_en": "🖥️ Server & Power Infrastructure Diagnostics", "title_hi": "🖥️ सर्वर और पावर इन्फ्रास्ट्रक्चर डायग्नोस्टिक्स", "English": ["Check UPS load and input power if alarms are active.", "Verify rack airflow and server room temperature.", "Review DNS and authentication dependencies if logins fail."], "Hindi": ["अलार्म आने पर UPS load और input power जांचें।", "Rack airflow और server room temperature जांचें।", "Login fail होने पर DNS और authentication dependencies देखें।"]},
}

if "local_tickets" not in st.session_state:
    st.session_state.local_tickets = pd.DataFrame([
        {"id": 1, "date": "2026-07-01", "user_name": "Amit Sharma", "department": "Production", "complaint": "CCTV camera in main corridor is flickering", "location": "Sector - 136 Vega", "attended_by": "Satish", "status": "In Progress", "category": "CCTV/Camera", "start_time": "2026-07-01 10:15:00", "close_time": None, "resolution_time": 0, "remarks": "POE check in progress"},
        {"id": 2, "date": "2026-07-03", "user_name": "Sunita Rao", "department": "Finance", "complaint": "Desktop showing blue screen after update", "location": "Knitpro 28-29", "attended_by": "Priyanshu", "status": "Open", "category": "Laptop/Hardware", "start_time": None, "close_time": None, "resolution_time": 0, "remarks": ""},
        {"id": 3, "date": "2026-07-05", "user_name": "Rajesh Kumar", "department": "HR", "complaint": "Office printer offline and queue is stuck", "location": "Sector - 155 Vega", "attended_by": "Amit", "status": "Resolved", "category": "Printer", "start_time": "2026-07-05 10:00:00", "close_time": "2026-07-05 10:35:00", "resolution_time": 35, "remarks": "Spooler restarted and queue flushed"},
    ])

if "local_nas" not in st.session_state:
    st.session_state.local_nas = pd.DataFrame([
        {"id": 1, "date": "2026-07-11", "server_name": "HRI", "status": "Success", "storage_used": 43.3975, "remarks": "Daily backup completed."},
        {"id": 2, "date": "2026-07-12", "server_name": "HRI", "status": "Success", "storage_used": 43.3985, "remarks": "Daily backup completed."},
        {"id": 3, "date": "2026-07-13", "server_name": "HRI", "status": "Failed", "storage_used": 43.3985, "remarks": "Handshake timeout."},
        {"id": 4, "date": "2026-07-13", "server_name": "Vega", "status": "Success", "storage_used": 236.1529, "remarks": "Backup completed."},
        {"id": 5, "date": "2026-07-15", "server_name": "Sery", "status": "Success", "storage_used": 4.2406, "remarks": "Incremental snapshot success."},
        {"id": 6, "date": "2026-07-15", "server_name": "Rise", "status": "Success", "storage_used": 6.4914, "remarks": "Replication completed."},
    ])

def format_ticket_number(ticket_id, location_str):
    try:
        clean_id = int(float(ticket_id))
        loc = str(location_str).lower() if pd.notna(location_str) else ""
        prefix = "VEGA" if ("vega" in loc or "136" in loc or "155" in loc) else "KP" if ("knitpro" in loc or "jaipur" in loc) else "IT"
        return f"{prefix}-2026-{clean_id:04d}"
    except Exception:
        return f"IT-2026-{ticket_id}"

def normalize_category(value):
    s = str(value).strip().lower().replace("&", "/")
    mapping = {
        "cctv/camera": "CCTVCamera",
        "cctv camera": "CCTVCamera",
        "camera": "CCTVCamera",
        "cctvcamera": "CCTVCamera",
        "laptop/hardware": "LaptopHardware",
        "laptop hardware": "LaptopHardware",
        "laptophardware": "LaptopHardware",
        "desktop": "LaptopHardware",
        "email/outlook": "EmailOutlook",
        "email outlook": "EmailOutlook",
        "emailoutlook": "EmailOutlook",
        "printer": "Printer",
        "sap": "SAP",
        "network": "Network",
        "server/ups": "ServerUPS",
        "server ups": "ServerUPS",
        "serverups": "ServerUPS",
        "other": "Other",
    }
    return mapping.get(s, value if pd.notna(value) and str(value).strip() else "Other")

def auto_categorize(complaint):
    text = str(complaint).lower()
    if any(k in text for k in ["cctv", "camera", "nvr"]): return "CCTVCamera"
    if any(k in text for k in ["laptop", "desktop", "keyboard", "touchpad", "battery", "screen", "hardware", "monitor"]): return "LaptopHardware"
    if any(k in text for k in ["outlook", "email", "mail", "pst", "ost"]): return "EmailOutlook"
    if any(k in text for k in ["printer", "scanner", "cartridge", "print"]): return "Printer"
    if any(k in text for k in ["sap", "erp"]): return "SAP"
    if any(k in text for k in ["network", "wifi", "internet", "vpn", "ping", "ip", "router", "switch", "lan"]): return "Network"
    if any(k in text for k in ["server", "ups", "rack", "dns", "domain", "backup"]): return "ServerUPS"
    return "Other"

def normalize_nas_status(value):
    s = str(value).strip().lower()
    if s in {"success", "ok", "passed", "pass", "complete", "completed"}: return "Success"
    if s in {"failed", "fail", "error", "warning", "warn", "partial", "warning / partial"}: return "Failed"
    return "Failed"

def normalize_ticket_df(df):
    expected = ["id", "date", "user_name", "department", "complaint", "location", "attended_by", "status", "category", "start_time", "close_time", "resolution_time", "remarks"]
    if df is None or df.empty: return pd.DataFrame(columns=expected)
    out = df.copy()
    for col in expected:
        if col not in out.columns: out[col] = None
    out["id"] = pd.to_numeric(out["id"], errors="coerce").fillna(0).astype(int)
    out["resolution_time"] = pd.to_numeric(out["resolution_time"], errors="coerce").fillna(0).astype(int)
    out["remarks"] = out["remarks"].fillna("").astype(str)
    out["status"] = out["status"].fillna("").astype(str)
    out["category"] = out["category"].fillna("").astype(str).map(normalize_category)
    out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    return out[expected]

def normalize_nas_df(df):
    expected = ["id", "date", "server_name", "status", "storage_used", "remarks"]
    if df is None or df.empty: return pd.DataFrame(columns=expected)
    out = df.copy()
    for col in expected:
        if col not in out.columns: out[col] = None
    out["id"] = pd.to_numeric(out["id"], errors="coerce").fillna(0).astype(int)
    out["storage_used"] = pd.to_numeric(out["storage_used"], errors="coerce").fillna(0.0)
    out["remarks"] = out["remarks"].fillna("").astype(str)
    out["server_name"] = out["server_name"].fillna("").astype(str)
    out["status"] = out["status"].fillna("").astype(str).str.strip().map(normalize_nas_status)
    out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    return out[expected]

def get_next_ticket_id(df):
    if df.empty or "id" not in df.columns: return 1
    return int(pd.to_numeric(df["id"], errors="coerce").fillna(0).max()) + 1

def get_next_nas_id(df):
    if df.empty or "id" not in df.columns: return 1
    return int(pd.to_numeric(df["id"], errors="coerce").fillna(0).max()) + 1

def prepare_ticket_view(df):
    view = df.copy()
    if not view.empty:
        view["System Ticket ID"] = view.apply(lambda r: format_ticket_number(r["id"], r["location"]), axis=1)
        view["date_parsed"] = pd.to_datetime(view["date"], errors="coerce")
    return view

def filtered_tickets(df, site_filter, status_filter, tech_filter):
    out = df.copy()
    if out.empty: return out
    if site_filter != "All": out = out[out["location"] == site_filter]
    if status_filter != "All": out = out[out["status"] == status_filter]
    if tech_filter != "All": out = out[out["attended_by"] == tech_filter]
    return out

def filtered_nas(df, server_filter):
    out = df.copy()
    if out.empty: return out
    if server_filter != "All": out = out[out["server_name"] == server_filter]
    return out

def separate_nas_series(df):
    if df.empty: return df
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    return out.dropna(subset=["date"])

def compute_nas_changes(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=["id", "date", "server_name", "status", "storage_used", "delta_gb", "delta_pct", "change_label", "change_type", "remarks"])
    out = normalize_nas_df(df).copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out = out.dropna(subset=["date"]).sort_values(["server_name", "date"])
    out["delta_gb"] = out.groupby("server_name")["storage_used"].diff().fillna(0.0)
    prev = out.groupby("server_name")["storage_used"].shift(1)
    out["delta_pct"] = ((out["storage_used"] - prev) / prev.replace(0, pd.NA) * 100).fillna(0.0)
    out["change_label"] = out["delta_gb"].apply(lambda x: f"+{x:.4f} GB" if x > 0 else (f"{x:.4f} GB" if x < 0 else "0.0000 GB"))
    out["change_type"] = out["delta_gb"].apply(lambda x: "Increment" if x > 0 else ("Decrement" if x < 0 else "No Change"))
    return out

def build_nas_reports(df):
    d = compute_nas_changes(df)
    if d.empty:
        empty = pd.DataFrame()
        return empty, empty, empty
    d["month"] = d["date"].dt.strftime("%Y-%m")
    master = d[[c for c in ["id", "date", "server_name", "status", "storage_used", "delta_gb", "delta_pct", "change_type", "remarks"] if c in d.columns]].copy()
    monthly = d.groupby(["month", "server_name"], as_index=False).agg(logs=("server_name", "size"), avg_storage=("storage_used", "mean"), min_storage=("storage_used", "min"), max_storage=("storage_used", "max"), total_increment=("delta_gb", lambda s: s[s > 0].sum()), total_decrement=("delta_gb", lambda s: abs(s[s < 0].sum())), failures=("status", lambda s: (s == "Failed").sum()))
    serverwise = d.groupby("server_name", as_index=False).agg(logs=("server_name", "size"), latest_date=("date", "max"), latest_storage=("storage_used", "last"), total_increment=("delta_gb", lambda s: s[s > 0].sum()), total_decrement=("delta_gb", lambda s: abs(s[s < 0].sum())), failures=("status", lambda s: (s == "Failed").sum()))
    return master, monthly, serverwise

def build_excel_report(tickets_df, nas_df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        detailed = build_detailed_ticket_exports(tickets_df)
        grouped = build_grouped_detail_views(tickets_df)
        mttr_month = build_mttr_sla_summary(add_priority_and_sla(prepare_ticket_view(tickets_df)).assign(Month=pd.to_datetime(prepare_ticket_view(tickets_df).get("date"), errors="coerce").dt.strftime("%Y-%m")), "Month") if tickets_df is not None and not tickets_df.empty else pd.DataFrame()
        mttr_week = build_mttr_sla_summary(add_priority_and_sla(prepare_ticket_view(tickets_df)).assign(Week=pd.to_datetime(prepare_ticket_view(tickets_df).get("date"), errors="coerce").dt.strftime("%Y-W") + pd.to_datetime(prepare_ticket_view(tickets_df).get("date"), errors="coerce").dt.isocalendar().week.astype(str)), "Week") if tickets_df is not None and not tickets_df.empty else pd.DataFrame()
        mttr_tech = build_mttr_sla_summary(prepare_ticket_view(tickets_df), "attended_by")
        mttr_site = build_mttr_sla_summary(prepare_ticket_view(tickets_df), "location")
        for name, frame in {
            "Master Tickets": detailed.get("Master Tickets", pd.DataFrame()),
            "Resolved Tickets": detailed.get("Resolved Tickets", pd.DataFrame()),
            "Pending Tickets": detailed.get("Pending Tickets", pd.DataFrame()),
            "Ticket Monthly": detailed.get("Ticket Monthly", pd.DataFrame()),
            "Ticket Weekly": detailed.get("Ticket Weekly", pd.DataFrame()),
            "Ticket Technician": detailed.get("Ticket Technician", pd.DataFrame()),
            "Ticket Location": detailed.get("Ticket Location", pd.DataFrame()),
            "Ticket Department": detailed.get("Ticket Department", pd.DataFrame()),
            "Repeat Issues": detailed.get("Repeat Issues", pd.DataFrame()),
            "Monthly Detail": grouped.get("monthly_detail", pd.DataFrame()),
            "Weekly Detail": grouped.get("weekly_detail", pd.DataFrame()),
            "Technician Detail": grouped.get("technician_detail", pd.DataFrame()),
            "Site Detail": grouped.get("site_detail", pd.DataFrame()),
            "MTTR SLA Month": mttr_month,
            "MTTR SLA Week": mttr_week,
            "MTTR SLA Tech": mttr_tech,
            "MTTR SLA Site": mttr_site,
        }.items():
            if frame is not None and not frame.empty:
                frame.to_excel(writer, sheet_name=name[:31], index=False)
        nas_master, nas_monthly, nas_weekly, nas_serverwise = build_nas_reports_extended(nas_df)
        nas_delta = compute_nas_changes(nas_df)
        nas_forecast = build_storage_forecast(nas_df)
        for name, frame in {
            "NAS Raw Logs": normalize_nas_df(nas_df),
            "NAS Deltas": nas_delta,
            "NAS Monthly": nas_monthly,
            "NAS Weekly": nas_weekly,
            "NAS Server Summary": nas_serverwise,
            "NAS Forecast": nas_forecast,
        }.items():
            if frame is not None and not frame.empty:
                frame.to_excel(writer, sheet_name=name[:31], index=False)
        vendor_perf = build_vendor_performance(load_vendor_followups_df(conn_global_for_pdf) if 'conn_global_for_pdf' in globals() and conn_global_for_pdf is not None else pd.DataFrame())
        dept_health = build_department_health(tickets_df)
        tech_score = build_technician_scorecard(tickets_df)
        aging = build_ticket_aging_analysis(tickets_df)
        insights = build_management_insights(tickets_df, nas_df, load_vendor_followups_df(conn_global_for_pdf) if 'conn_global_for_pdf' in globals() and conn_global_for_pdf is not None else pd.DataFrame())
        capacity = build_capacity_planning_dashboard(nas_df)
        assets = build_asset_health(load_assets_df(conn_global_for_pdf) if 'conn_global_for_pdf' in globals() and conn_global_for_pdf is not None else pd.DataFrame(), tickets_df)
        extra_frames = {
            'Executive Summary': build_month_over_month_comparison(tickets_df),
            'Ticket Aging Report': aging.get('aging_table', pd.DataFrame()),
            'SLA Compliance Report': build_mttr_sla_summary(prepare_ticket_view(tickets_df), 'location'),
            'Vendor Performance Report': vendor_perf.get('table', pd.DataFrame()),
            'Technician Scorecard': tech_score,
            'Department Health': dept_health,
            'Capacity Planning': capacity,
            'Asset Health': assets.get('registry', pd.DataFrame()),
            'Management Insights': insights,
        }
        for name, frame in extra_frames.items():
            if frame is not None and not frame.empty:
                frame.to_excel(writer, sheet_name=name[:31], index=False)
    return output.getvalue()

def build_ticket_exec_metrics(df):
    if df is None or df.empty:
        return {"today_open": 0, "today_closed": 0, "pending": 0, "overdue": 0, "avg_resolution": 0, "resolution_rate": 0.0}
    x = df.copy()
    x["date_parsed"] = pd.to_datetime(x.get("date"), errors="coerce")
    today = pd.Timestamp.now().normalize()
    today_mask = x["date_parsed"].dt.normalize() == today
    pending_mask = x["status"].isin(["Open", "In Progress", "On Hold - User Busy"])
    resolved_mask = x["status"] == "Resolved"
    overdue_mask = pending_mask & x["date_parsed"].notna() & ((today - x["date_parsed"].dt.normalize()).dt.days >= 2)
    resolved_df = x[resolved_mask & (pd.to_numeric(x.get("resolution_time"), errors="coerce").fillna(0) > 0)]
    total = len(x)
    resolved = int(resolved_mask.sum())
    return {
        "today_open": int((today_mask & pending_mask).sum()),
        "today_closed": int((today_mask & resolved_mask).sum()),
        "pending": int(pending_mask.sum()),
        "overdue": int(overdue_mask.sum()),
        "avg_resolution": int(resolved_df["resolution_time"].mean()) if not resolved_df.empty else 0,
        "resolution_rate": round((resolved / total) * 100, 1) if total else 0.0,
    }

def build_ticket_trend(df, freq="Daily"):
    if df is None or df.empty:
        return pd.DataFrame()
    x = current_period_ticket_df(df, freq=freq)
    if x.empty:
        return pd.DataFrame()
    if freq == "Weekly":
        week_num = x["date_parsed"].dt.isocalendar().week.astype(int).astype(str).str.zfill(2)
        year_num = x["date_parsed"].dt.isocalendar().year.astype(str)
        x["bucket"] = year_num + "-W" + week_num
    elif freq == "Monthly":
        x["bucket"] = x["date_parsed"].dt.strftime("%Y-%m")
    else:
        x["bucket"] = x["date_parsed"].dt.strftime("%Y-%m-%d")
    out = x.groupby("bucket", as_index=False).agg(Tickets=("id", "size"), Resolved=("status", lambda s: (s == "Resolved").sum()))
    return out.sort_values("bucket")

def build_department_summary(df):
    if df is None or df.empty:
        return pd.DataFrame()
    x = df.copy()
    out = x.groupby("department", as_index=False).agg(Tickets=("id", "size"), Resolved=("status", lambda s: (s == "Resolved").sum()))
    out["Pending"] = out["Tickets"] - out["Resolved"]
    return out.sort_values(["Tickets", "Resolved"], ascending=[False, False])

def build_location_summary(df):
    if df is None or df.empty:
        return pd.DataFrame()
    x = df.copy()
    out = x.groupby("location", as_index=False).agg(Tickets=("id", "size"), Resolved=("status", lambda s: (s == "Resolved").sum()))
    out["Pending"] = out["Tickets"] - out["Resolved"]
    return out.sort_values(["Tickets", "Resolved"], ascending=[False, False])

def build_technician_performance(df):
    if df is None or df.empty:
        return pd.DataFrame()
    x = df.copy()
    x["resolution_time"] = pd.to_numeric(x.get("resolution_time"), errors="coerce").fillna(0)
    out = x.groupby("attended_by", as_index=False).agg(Assigned=("id", "size"), Resolved=("status", lambda s: (s == "Resolved").sum()), Avg_Resolution_Min=("resolution_time", lambda s: int(s[s > 0].mean()) if (s > 0).any() else 0))
    out["Pending"] = out["Assigned"] - out["Resolved"]
    out["Resolution_%"] = ((out["Resolved"] / out["Assigned"]) * 100).round(1)
    return out.sort_values(["Assigned", "Resolved"], ascending=[False, False])

def build_repeat_issue_summary(df):
    if df is None or df.empty:
        return pd.DataFrame()
    x = df.copy()
    x["complaint_norm"] = x["complaint"].fillna("").astype(str).str.strip().str.lower()
    x = x[x["complaint_norm"] != ""]
    if x.empty:
        return pd.DataFrame()
    out = x.groupby(["category", "complaint_norm"], as_index=False).agg(Tickets=("id", "size"), Last_Seen=("date", "max"))
    out = out[out["Tickets"] > 1].sort_values(["Tickets", "Last_Seen"], ascending=[False, False])
    return out.rename(columns={"complaint_norm": "Complaint Pattern"}).head(10)

def build_ticket_reports(df):
    if df is None or df.empty:
        empty = pd.DataFrame()
        return empty, empty, empty, empty
    x = df.copy()
    x["date_parsed"] = pd.to_datetime(x.get("date"), errors="coerce")
    x = x.dropna(subset=["date_parsed"])
    if x.empty:
        empty = pd.DataFrame()
        return empty, empty, empty, empty
    today = pd.Timestamp.now().normalize()
    current_month_df = x[x["date_parsed"].dt.to_period("M") == today.to_period("M")].copy()
    current_week_iso = today.isocalendar()
    current_week_df = x[(x["date_parsed"].dt.isocalendar().year == current_week_iso.year) & (x["date_parsed"].dt.isocalendar().week == current_week_iso.week)].copy()
    if current_month_df.empty:
        current_month_df = x.copy()
    if current_week_df.empty:
        current_week_df = x.copy()
    current_month_df["Month"] = current_month_df["date_parsed"].dt.strftime("%Y-%m")
    week_num = current_week_df["date_parsed"].dt.isocalendar().week.astype(int).astype(str).str.zfill(2)
    year_num = current_week_df["date_parsed"].dt.isocalendar().year.astype(str)
    current_week_df["Week"] = year_num + "-W" + week_num
    monthly = current_month_df.groupby("Month", as_index=False).agg(Tickets=("id", "size"), Resolved=("status", lambda s: (s == "Resolved").sum()), Open=("status", lambda s: (s == "Open").sum()), In_Progress=("status", lambda s: (s == "In Progress").sum()), On_Hold=("status", lambda s: (s == "On Hold - User Busy").sum()))
    weekly = current_week_df.groupby("Week", as_index=False).agg(Tickets=("id", "size"), Resolved=("status", lambda s: (s == "Resolved").sum()), Open=("status", lambda s: (s == "Open").sum()), In_Progress=("status", lambda s: (s == "In Progress").sum()), On_Hold=("status", lambda s: (s == "On Hold - User Busy").sum()))
    technician = x.groupby("attended_by", as_index=False).agg(Tickets=("id", "size"), Resolved=("status", lambda s: (s == "Resolved").sum()), Avg_Resolution_Min=("resolution_time", lambda s: int(pd.to_numeric(s, errors='coerce').fillna(0)[pd.to_numeric(s, errors='coerce').fillna(0) > 0].mean()) if (pd.to_numeric(s, errors='coerce').fillna(0) > 0).any() else 0))
    location = x.groupby("location", as_index=False).agg(Tickets=("id", "size"), Resolved=("status", lambda s: (s == "Resolved").sum()))
    return monthly, weekly, technician, location

def build_nas_reports_extended(df):
    master, monthly, serverwise = build_nas_reports(df)
    changes = compute_nas_changes(df)
    if changes.empty:
        return master, monthly, pd.DataFrame(), serverwise
    changes["Week"] = changes["date"].dt.strftime("%Y-W") + changes["date"].dt.isocalendar().week.astype(str)
    weekly = changes.groupby(["Week", "server_name"], as_index=False).agg(Logs=("server_name", "size"), Avg_Storage=("storage_used", "mean"), Total_Increment=("delta_gb", lambda s: s[s > 0].sum()), Total_Decrement=("delta_gb", lambda s: abs(s[s < 0].sum())), Failures=("status", lambda s: (s == "Failed").sum()))
    return master, monthly, weekly, serverwise

def load_tickets():
    if db_connected:
        try:
            response = supabase_client.table("tickets").select("*").execute()
            return normalize_ticket_df(pd.DataFrame(response.data) if response.data else pd.DataFrame())
        except Exception:
            pass
    return normalize_ticket_df(st.session_state.local_tickets)

def load_nas_data():
    if db_connected:
        try:
            if table_exists("nasbackups"):
                response = supabase_client.table("nasbackups").select("*").execute()
                return normalize_nas_df(pd.DataFrame(response.data) if response.data else pd.DataFrame())
            if table_exists("nas_backups"):
                response = supabase_client.table("nas_backups").select("*").execute()
                return normalize_nas_df(pd.DataFrame(response.data) if response.data else pd.DataFrame())
        except Exception:
            pass
    return normalize_nas_df(st.session_state.local_nas)

def save_ticket(new_row):
    if db_connected:
        response = supabase_client.table("tickets").insert(new_row).execute()
        if response.data and "id" in response.data[0]: return int(response.data[0]["id"])
        return None
    current = st.session_state.local_tickets.copy()
    row = dict(new_row)
    if "category" in row:
        row["category"] = normalize_category(row["category"])
    row["id"] = get_next_ticket_id(current)
    st.session_state.local_tickets = pd.concat([current, pd.DataFrame([row])], ignore_index=True)
    return int(row["id"])

def update_ticket(ticket_id, payload):
    if db_connected:
        supabase_client.table("tickets").update(payload).eq("id", int(ticket_id)).execute()
        return
    idx = st.session_state.local_tickets[st.session_state.local_tickets["id"] == int(ticket_id)].index
    for key, value in payload.items():
        st.session_state.local_tickets.loc[idx, key] = normalize_category(value) if key == "category" else value

def delete_ticket(ticket_id):
    if db_connected:
        supabase_client.table("tickets").delete().eq("id", int(ticket_id)).execute()
        return
    st.session_state.local_tickets = st.session_state.local_tickets[st.session_state.local_tickets["id"] != int(ticket_id)].reset_index(drop=True)

def save_nas_log(new_row):
    if db_connected:
        response = supabase_client.table("nas_backups").insert(new_row).execute()
        if response.data and "id" in response.data[0]: return int(response.data[0]["id"])
        return None
    current = st.session_state.local_nas.copy()
    row = dict(new_row)
    if "category" in row:
        row["category"] = normalize_category(row["category"])
    row["id"] = get_next_nas_id(current)
    st.session_state.local_nas = pd.concat([current, pd.DataFrame([row])], ignore_index=True)
    return int(row["id"])

def delete_nas_log(log_id):
    if db_connected:
        target = "nasbackups" if table_exists("nasbackups") else "nas_backups" if table_exists("nas_backups") else None
        if target:
            supabase_client.table(target).delete().eq("id", int(log_id)).execute()
            return
    st.session_state.local_nas = st.session_state.local_nas[st.session_state.local_nas["id"] != int(log_id)].reset_index(drop=True)

def add_notification(conn, username, message):
    conn.execute("INSERT INTO notifications (username, message, is_read) VALUES (?, ?, 0)", (username, message))
    conn.commit()

def mark_notification_read(conn, notif_id):
    conn.execute("UPDATE notifications SET is_read=1 WHERE id=?", (notif_id,))
    conn.commit()

def status_badge_html(status):
    s = str(status).strip().lower()
    if s == "resolved": return '<span class="status-chip status-resolved">Resolved</span>'
    if s == "in progress": return '<span class="status-chip status-progress">In Progress</span>'
    if s == "on hold - user busy": return '<span class="status-chip status-hold">On Hold</span>'
    return '<span class="status-chip status-open">Open</span>'

def render_nas_status(status):
    return '<span class="status-chip status-resolved">Success</span>' if str(status).strip() == "Success" else '<span class="status-chip status-open">Failed</span>'

def render_status_table(df, columns, compact=False, nas_mode=False):
    if df.empty:
        st.info("No records found.")
        return

    show_df = df.copy()
    if "status" in show_df.columns:
        show_df["status"] = show_df["status"].apply(render_nas_status if nas_mode else status_badge_html)

    safe_columns = [c for c in columns if c in show_df.columns]
    styled = show_df[safe_columns].to_html(escape=False, index=False)
    css_class = "table-scroll compact-table" if compact else "table-scroll"
    st.markdown(f'<div class="{css_class}">{styled}</div>', unsafe_allow_html=True)

def render_glass_card(title, value, subtext, color_var="--accent"):
    st.markdown(f"<div class='metric-card'><div class='metric-label'>{title}</div><div class='metric-value'>{value}</div><div class='metric-sub' style='color: var({color_var});'>{subtext}</div></div>", unsafe_allow_html=True)

def build_bar_chart(df, xcol, ycol, color="#ef4444"):
    return alt.Chart(df).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(x=alt.X(xcol, title=None), y=alt.Y(ycol, title=None), color=alt.value(color), tooltip=list(df.columns)).properties(height=280)

def build_line_chart(df, xcol, ycol, color="#3b82f6"):
    return alt.Chart(df).mark_line(point=True, strokeWidth=3).encode(x=alt.X(xcol, title=None), y=alt.Y(ycol, title=None), color=alt.value(color), tooltip=list(df.columns)).properties(height=280)

def login_page(conn):
    vega_logo = find_logo_filename("vega_logo.png")
    knitpro_logo = find_logo_filename("knitpro_logo.png")
    vega_html = f'<img src="data:image/png;base64,{image_to_base64(vega_logo)}" alt="Vega logo" style="max-width:220px; height:auto;">' if vega_logo else '<div style="font-size:2.8rem;font-weight:800;color:#22d3ee;">VEGA</div>'
    knitpro_html = f'<img src="data:image/png;base64,{image_to_base64(knitpro_logo)}" alt="KnitPro logo" style="max-width:168px; height:auto;">' if knitpro_logo else ''

    left_col, right_col = st.columns([1.38, 1.0], gap="large")
    with left_col:
        st.markdown(f"""
        <div class="login-panel-left">
            <div>
                <div class="login-eyebrow">IT Operations</div>
                <div class="login-brand-lockup">{vega_html}{knitpro_html}</div>
                <div class="login-title-sub">Unified IT ticketing, technician operations, analytics, and infrastructure visibility.</div>
            </div>
            <div class="login-note">Built for structured incident logging, role-based access, and cleaner operational reporting across Vega and KnitPro support environments.</div>
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        top_spacer, card_slot, form_slot, bottom_spacer = st.columns([0.06, 0.88, 0.88, 0.06])
        with card_slot:
            st.markdown('<div class="login-panel-right" style="min-height:auto; padding-bottom:0;"><div class="login-form-shell" style="transform:none; margin-bottom:20px;"><div class="login-accent-line"></div><div class="login-mini">Vega IT Access</div><div class="login-h1">Sign in</div><div class="login-subcopy">Use your assigned account to access the dashboard.</div></div></div>', unsafe_allow_html=True)
        with form_slot:
            username = st.text_input("Username", placeholder="Enter your username", key="login_username").strip().lower()
            
            # Show / Hide password feature added directly here
            show_pw = st.checkbox("Show Password", key="toggle_login_pw")
            pw_type = "text" if show_pw else "password"
            password = st.text_input("Password", type=pw_type, placeholder="Enter your password", key="login_password")
            
            login_clicked = st.button("Login", use_container_width=True, key="login_button")
            st.markdown('<div class="login-support">Need account support? <span class="linkish">Contact administrator</span></div><div class="login-footer"><span class="linkish">Terms</span><span class="linkish">Policy</span><span>© 2026 Vega Industries Pvt. Ltd.</span></div>', unsafe_allow_html=True)

    if login_clicked:
        pending_user = get_user_by_username(conn, username)
        if pending_user and int(pending_user.get("active", 0) or 0) == 1 and (pending_user.get("must_change_password") or not pending_user.get("password_hash")):
            st.session_state["current_user"] = pending_user
            st.session_state["must_set_password"] = True
            st.rerun()
        user = authenticate_user(conn, username, password)
        if not user:
            st.error("Invalid credentials or inactive account.")
            return None
        st.session_state["current_user"] = user
        if user["must_change_password"] or not user["password_hash"]:
            st.session_state["must_set_password"] = True
        st.success(f"Welcome {user['display_name']}")
        st.rerun()
    return None

def first_password_setup(conn):
    user = st.session_state.get("current_user")
    st.warning("First time login detected. Set a new password to continue.")
    
    show_pw = st.checkbox("Show Passwords", key="toggle_setup_pw")
    pw_type = "text" if show_pw else "password"
    
    p1 = st.text_input("New password", type=pw_type)
    p2 = st.text_input("Confirm password", type=pw_type)
    if st.button("Save Password"):
        if len(p1) < 6:
            st.error("Password must be at least 6 characters long.")
            return
        if p1 != p2:
            st.error("Passwords do not match.")
            return
        set_user_password(conn, user["username"], p1)
        st.session_state["current_user"] = get_user_by_username(conn, user["username"])
        st.session_state["must_set_password"] = False
        st.success("Password updated successfully!")
        st.rerun()

def bootstrap_auth_gate(conn):
    if "current_user" not in st.session_state: st.session_state["current_user"] = None
    if "must_set_password" not in st.session_state: st.session_state["must_set_password"] = False
    if st.session_state["current_user"] is None:
        login_page(conn)
        st.stop()
    if st.session_state.get("must_set_password"):
        first_password_setup(conn)
        st.stop()

def get_role_pages(role):
    if role == "IT Manager": return ["Home", "Executive Command Center", "Overview", "Ticket Operations", "NAS Monitoring", "Reports", "Task Center", "Admin Tools", "AVP Dashboard", "Team Chat", "Vendor Dashboard", "Department Health", "Asset Health"]
    if role == "IT AM": return ["Home", "Executive Command Center", "Overview", "Ticket Operations", "NAS Monitoring", "Reports", "Task Center", "Team Chat", "Vendor Dashboard", "Department Health", "Asset Health"]
    if role == "AVP": return ["Home", "Executive Command Center", "Overview", "AVP Dashboard", "Reports", "Task Center", "Team Chat", "Vendor Dashboard", "Department Health", "Asset Health"]
    return ["Home", "Overview", "Ticket Operations", "NAS Monitoring", "Task Center", "Team Chat"]

def create_task(conn, payload):
    conn.execute("INSERT INTO tasks (title, description, assigned_by, assigned_to, priority, status, progress, due_date, vendor_flag, vendor_status, vendor_remark, reminder_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (payload.get("title"), payload.get("description"), payload.get("assigned_by"), payload.get("assigned_to"), payload.get("priority", "Medium"), payload.get("status", "Open"), payload.get("progress", 0), payload.get("due_date"), payload.get("vendor_flag", 0), payload.get("vendor_status"), payload.get("vendor_remark"), payload.get("reminder_date")))
    conn.commit()

def update_task(conn, task_id, payload):
    fields = ", ".join([f"{k}=?" for k in payload.keys()])
    values = list(payload.values()) + [task_id]
    conn.execute(f"UPDATE tasks SET {fields}, updated_at=CURRENT_TIMESTAMP WHERE id=?", values)
    conn.commit()

def add_task_comment(conn, task_id, comment, commented_by):
    conn.execute("INSERT INTO task_comments (task_id, comment, commented_by) VALUES (?, ?, ?)", (task_id, comment, commented_by))
    conn.commit()

def add_vendor_followup(conn, ticket_id, vendor_name, followup_status, vendor_remark, due_date):
    conn.execute("INSERT INTO vendor_followups (ticket_id, vendor_name, followup_status, vendor_remark, due_date) VALUES (?, ?, ?, ?, ?)", (ticket_id, vendor_name, followup_status, vendor_remark, due_date))
    conn.commit()


def get_all_users(conn):
    if db_connected and table_exists("users"):
        try:
            rows = supabase_client.table("users").select("*").execute()
            data = rows.data or []
            return pd.DataFrame([normalize_user_record(r) for r in data if normalize_user_record(r)])
        except Exception:
            pass
    cur = conn.cursor()
    cur.execute("SELECT id, username, display_name, role, password_hash, active, must_change_password FROM users ORDER BY username")
    rows = cur.fetchall()
    return pd.DataFrame([{k: row[k] for k in row.keys()} for row in rows])

def load_tasks_df(conn):
    try:
        return pd.read_sql_query("SELECT id, title, description, assigned_by, assigned_to, priority, status, progress, due_date, vendor_flag, vendor_status, vendor_remark, reminder_date, created_at, updated_at FROM tasks ORDER BY id DESC", conn)
    except Exception:
        return pd.DataFrame(columns=["id", "title", "description", "assigned_by", "assigned_to", "priority", "status", "progress", "due_date", "vendor_flag", "vendor_status", "vendor_remark", "reminder_date", "created_at", "updated_at"])

def load_vendor_followups_df(conn):
    try:
        return pd.read_sql_query("SELECT id, ticket_id, vendor_name, followup_status, vendor_remark, due_date, created_at FROM vendor_followups ORDER BY id DESC", conn)
    except Exception:
        return pd.DataFrame(columns=["id", "ticket_id", "vendor_name", "followup_status", "vendor_remark", "due_date", "created_at"])


def load_task_comments_df(conn):
    try:
        return pd.read_sql_query("SELECT id, task_id, comment, commented_by, created_at FROM task_comments ORDER BY id DESC", conn)
    except Exception:
        return pd.DataFrame(columns=["id", "task_id", "comment", "commented_by", "created_at"])


def load_notifications_df(conn, username=None):
    try:
        if username:
            return pd.read_sql_query("SELECT id, username, message, is_read, created_at FROM notifications WHERE lower(username)=lower(?) ORDER BY id DESC", conn, params=(username,))
        return pd.read_sql_query("SELECT id, username, message, is_read, created_at FROM notifications ORDER BY id DESC", conn)
    except Exception:
        return pd.DataFrame(columns=["id", "username", "message", "is_read", "created_at"])

def load_user_status_df(conn):
    try:
        return pd.read_sql_query("SELECT username, display_name, status, updated_at FROM user_status ORDER BY display_name", conn)
    except Exception:
        return pd.DataFrame(columns=["username", "display_name", "status", "updated_at"])

def set_user_status(conn, username, display_name, status):
    conn.execute("INSERT INTO user_status (username, display_name, status, updated_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP) ON CONFLICT(username) DO UPDATE SET display_name=excluded.display_name, status=excluded.status, updated_at=CURRENT_TIMESTAMP", (username, display_name, status))
    conn.commit()


def load_chat_threads_df(conn):
    try:
        return pd.read_sql_query("SELECT id, title, created_by, created_at FROM chat_threads ORDER BY id DESC", conn)
    except Exception:
        return pd.DataFrame(columns=["id", "title", "created_by", "created_at"])

def load_chat_messages_df(conn, thread_id=None):
    try:
        if thread_id is None:
            return pd.read_sql_query("SELECT id, thread_id, sender, message, created_at FROM chat_messages ORDER BY id DESC", conn)
        return pd.read_sql_query("SELECT id, thread_id, sender, message, created_at FROM chat_messages WHERE thread_id=? ORDER BY id ASC", conn, params=(int(thread_id),))
    except Exception:
        return pd.DataFrame(columns=["id", "thread_id", "sender", "message", "created_at"])

def create_chat_thread(conn, title, created_by):
    cur = conn.cursor()
    cur.execute("INSERT INTO chat_threads (title, created_by) VALUES (?, ?)", (title, created_by))
    conn.commit()
    return cur.lastrowid

def post_chat_message(conn, thread_id, sender, message):
    conn.execute("INSERT INTO chat_messages (thread_id, sender, message) VALUES (?, ?, ?)", (int(thread_id), sender, message))
    conn.commit()
    users_df = get_all_users(conn)
    if not users_df.empty and 'username' in users_df.columns:
        for uname in users_df['username'].dropna().astype(str).tolist():
            if uname.lower() != str(sender).lower():
                add_notification(conn, uname, f"New team chat message from {sender}")

def add_priority_and_sla(df):
    out = df.copy()
    if out.empty:
        return out
    if "priority" not in out.columns:
        def infer_priority(x):
            t = str(x).lower()
            if any(k in t for k in ["server", "sap", "network down", "critical", "vpn down"]):
                return "Critical"
            if any(k in t for k in ["printer", "email", "outlook", "cctv", "camera"]):
                return "High"
            return "Medium"
        out["priority"] = out.get("complaint", "").apply(infer_priority)
    out["date_parsed"] = pd.to_datetime(out.get("date"), errors="coerce")
    out["resolution_time"] = pd.to_numeric(out.get("resolution_time"), errors="coerce").fillna(0)
    now = pd.Timestamp.now()
    open_mask = out.get("status", pd.Series(dtype=str)).astype(str).isin(["Open", "In Progress", "On Hold - User Busy", "On Hold"])
    age_hours = ((now - out["date_parsed"]).dt.total_seconds() / 3600).fillna(0)
    out["age_hours"] = age_hours.round(1)
    sla_hours = out["priority"].map({"Critical": 2, "High": 4, "Medium": 8, "Low": 12}).fillna(8)
    out["sla_hours"] = sla_hours
    out["sla_breach"] = open_mask & (out["age_hours"] > out["sla_hours"])
    out["sla_badge"] = out["sla_breach"].map({True: "BREACH", False: "OK"})
    out["frt_min"] = out["resolution_time"].apply(lambda v: max(round(float(v) * 0.25), 1) if pd.notna(v) and float(v) > 0 else None)
    return out

def build_location_issue_heatmap(df):
    x = add_priority_and_sla(df)
    if x.empty:
        return alt.Chart(pd.DataFrame({"location": [], "category": [], "count": []})).mark_rect()
    base = x.groupby(["location", "category"], as_index=False).agg(count=("id", "size"))
    return alt.Chart(base).mark_rect().encode(
        x=alt.X("location:N", title="Location", sort="-y"),
        y=alt.Y("category:N", title="Issue Category"),
        color=alt.Color("count:Q", title="Tickets"),
        tooltip=["location", "category", "count"]
    )

def build_sla_breach_view(df):
    x = add_priority_and_sla(df)
    if x.empty:
        return x
    cols = [c for c in ["System Ticket ID", "user_name", "location", "category", "priority", "status", "age_hours", "sla_hours", "sla_badge", "attended_by", "remarks"] if c in x.columns]
    return x[x["status"].astype(str).isin(["Open", "In Progress", "On Hold - User Busy", "On Hold"])][cols]

def build_grouped_detail_views(df):
    x = add_priority_and_sla(prepare_ticket_view(df))
    if x.empty:
        empty = pd.DataFrame()
        return {"monthly_detail": empty, "weekly_detail": empty, "technician_detail": empty, "site_detail": empty}
    x["Month"] = pd.to_datetime(x["date"], errors="coerce").dt.strftime("%Y-%m")
    x["Week"] = pd.to_datetime(x["date"], errors="coerce").dt.strftime("%Y-W") + pd.to_datetime(x["date"], errors="coerce").dt.isocalendar().week.astype(str)
    x["MTTR_Min"] = x["resolution_time"]
    x["FRT_Min"] = x["frt_min"]
    return {
        "monthly_detail": x.sort_values(["Month", "date"], ascending=[False, False]),
        "weekly_detail": x.sort_values(["Week", "date"], ascending=[False, False]),
        "technician_detail": x.sort_values(["attended_by", "date"], ascending=[True, False]),
        "site_detail": x.sort_values(["location", "date"], ascending=[True, False]),
    }

def build_mttr_sla_summary(df, group_col):
    x = add_priority_and_sla(df)
    if x.empty or group_col not in x.columns:
        return pd.DataFrame()
    x["resolution_time"] = pd.to_numeric(x.get("resolution_time"), errors="coerce").fillna(0)
    return x.groupby(group_col, as_index=False).agg(
        Tickets=("id", "size"),
        Resolved=("status", lambda s: (s.astype(str) == "Resolved").sum()),
        MTTR_Min=("resolution_time", lambda s: round(s[s > 0].mean(), 1) if (s > 0).any() else 0),
        FRT_Min=("frt_min", lambda s: round(pd.Series(s).dropna().mean(), 1) if pd.Series(s).dropna().shape[0] else 0),
        SLA_Breach_Rate=("sla_breach", lambda s: round(pd.Series(s).fillna(False).mean() * 100, 1)),
    )

def build_storage_forecast(df):
    x = normalize_nas_df(df).copy()
    if x.empty:
        return pd.DataFrame()
    x["date"] = pd.to_datetime(x["date"], errors="coerce")
    x = x.dropna(subset=["date"]).sort_values(["server_name", "date"])
    rows = []
    for server, g in x.groupby("server_name"):
        if len(g) < 2:
            continue
        day_index = (g["date"] - g["date"].min()).dt.days.astype(float)
        y = pd.to_numeric(g["storage_used"], errors="coerce").fillna(0).astype(float)
        try:
            slope, intercept = pd.Series(y).astype(float).pipe(lambda yy: __import__("numpy").polyfit(day_index, yy, 1))
            latest_storage = float(y.iloc[-1])
            capacity = 100.0
            days_to_full = None
            if slope > 0 and latest_storage < capacity:
                days_to_full = max(((capacity - intercept) / slope) - float(day_index.iloc[-1]), 0)
            rows.append({
                "server_name": server,
                "latest_storage": round(latest_storage, 4),
                "daily_growth_est": round(float(slope), 4),
                "projected_days_to_100": round(float(days_to_full), 1) if days_to_full is not None else None,
            })
        except Exception:
            pass
    return pd.DataFrame(rows)

def build_system_reliability_index(df):
    x = add_priority_and_sla(df)
    if x.empty:
        return 100.0
    resolved_rate = (x["status"].astype(str) == "Resolved").mean() * 100
    breach_penalty = x["sla_breach"].fillna(False).mean() * 30
    pending_penalty = x["status"].astype(str).isin(["Open", "In Progress", "On Hold - User Busy", "On Hold"]).mean() * 20
    return round(max(min(resolved_rate - breach_penalty - pending_penalty + 20, 100), 0), 1)

def build_department_load_distribution(df):
    x = add_priority_and_sla(df)
    if x.empty:
        return pd.DataFrame()
    out = x.groupby("department", as_index=False).agg(Tickets=("id", "size"), Avg_Resolution=("resolution_time", lambda s: round(pd.to_numeric(s, errors='coerce').fillna(0).replace(0, pd.NA).dropna().mean(), 1) if pd.to_numeric(s, errors='coerce').fillna(0).replace(0, pd.NA).dropna().shape[0] else 0))
    total = out["Tickets"].sum()
    out["Load_%"] = ((out["Tickets"] / total) * 100).round(1) if total else 0
    out["Estimated_Cost_Index"] = (out["Tickets"] * out["Avg_Resolution"].replace(0, 5)).round(1)
    return out.sort_values("Tickets", ascending=False)

def build_technician_efficiency_matrix(df):
    perf = build_technician_performance(df)
    if perf.empty:
        return alt.Chart(pd.DataFrame({"attended_by": [], "Resolved": [], "Avg_Resolution_Min": []})).mark_circle()
    return alt.Chart(perf).mark_circle(size=160).encode(
        x=alt.X("Resolved:Q", title="Tickets Resolved"),
        y=alt.Y("Avg_Resolution_Min:Q", title="Average Resolution Time (MTTR Min)"),
        color=alt.Color("attended_by:N", title="Technician"),
        tooltip=["attended_by", "Assigned", "Resolved", "Avg_Resolution_Min", "Resolution_%"]
    )

def build_top_recurring_failures(df):
    x = add_priority_and_sla(df)
    if x.empty:
        return pd.DataFrame()
    return x.groupby(["location", "category"], as_index=False).agg(Tickets=("id", "size")).sort_values("Tickets", ascending=False).head(5)

def render_clickable_metric_filters(default_value="All"):
    if "overview_metric_filter" not in st.session_state:
        st.session_state["overview_metric_filter"] = default_value
    cols = st.columns(4)
    labels = [
        ("All Queue", "All"),
        ("Open", "Open"),
        ("In Progress", "In Progress"),
        ("On Hold", "On Hold - User Busy"),
    ]
    for col, (label, value) in zip(cols, labels):
        with col:
            if st.button(label, use_container_width=True, key=f"metric_filter_{value}"):
                st.session_state["overview_metric_filter"] = value
    return st.session_state.get("overview_metric_filter", default_value)

def filter_queue_by_metric(df, metric_value):
    if df.empty or metric_value == "All":
        return df
    if metric_value == "On Hold - User Busy":
        return df[df["status"].astype(str).isin(["On Hold - User Busy", "On Hold"])]
    return df[df["status"].astype(str) == metric_value]

def load_chat_messages_df(conn, thread_id=None):
    try:
        if thread_id is None:
            return pd.read_sql_query("SELECT id, thread_id, sender, message, linked_ticket_id, created_at FROM chat_messages ORDER BY id DESC", conn)
        return pd.read_sql_query("SELECT id, thread_id, sender, message, linked_ticket_id, created_at FROM chat_messages WHERE thread_id=? ORDER BY id ASC", conn, params=(int(thread_id),))
    except Exception:
        return pd.DataFrame(columns=["id", "thread_id", "sender", "message", "linked_ticket_id", "created_at"])

def post_chat_message(conn, thread_id, sender, message, linked_ticket_id=None):
    conn.execute("INSERT INTO chat_messages (thread_id, sender, message, linked_ticket_id) VALUES (?, ?, ?, ?)", (int(thread_id), sender, message, int(linked_ticket_id) if linked_ticket_id not in [None, '', 'None'] else None))
    conn.commit()
    users_df = get_all_users(conn)
    mentions = {token[1:].strip(' ,.:;!') for token in str(message).split() if token.startswith('@') and len(token) > 1}
    if not users_df.empty and 'username' in users_df.columns:
        for uname in users_df['username'].dropna().astype(str).tolist():
            if uname.lower() == str(sender).lower():
                continue
            msg = f"New team chat message from {sender}"
            if uname in mentions:
                msg = f"Mention from {sender} in team chat"
            add_notification(conn, uname, msg)

def build_thread_unread_map(conn, username):
    msgs = load_chat_messages_df(conn)
    notifs = load_notifications_df(conn, username)
    out = {}
    if msgs.empty:
        return out
    unread = 0 if notifs.empty else int((notifs['is_read'] == 0).sum())
    for tid in msgs['thread_id'].dropna().astype(int).unique().tolist():
        out[tid] = unread
    return out

def build_detailed_ticket_exports(df):
    x = prepare_ticket_view(df)
    x = x.drop(columns=[c for c in ["date_parsed"] if c in x.columns])
    monthly, weekly, technician, location = build_ticket_reports(df)
    dept = build_department_summary(df)
    repeat = build_repeat_issue_summary(df)
    resolved = x[x["status"].astype(str) == "Resolved"].copy() if not x.empty and "status" in x.columns else pd.DataFrame()
    pending = x[x["status"].astype(str).isin(["Open", "In Progress", "On Hold - User Busy", "On Hold"])].copy() if not x.empty and "status" in x.columns else pd.DataFrame()
    return {
        "Master Tickets": x,
        "Ticket Monthly": monthly,
        "Ticket Weekly": weekly,
        "Ticket Technician": technician,
        "Ticket Location": location,
        "Ticket Department": dept,
        "Repeat Issues": repeat,
        "Resolved Tickets": resolved,
        "Pending Tickets": pending,
    }



# Added month/year helpers for detailed report selection
ASSET_REGISTRY_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS asset_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id TEXT,
    asset_type TEXT,
    location TEXT,
    vendor TEXT,
    purchase_date TEXT,
    warranty_end TEXT,
    status TEXT DEFAULT 'Active'
)
"""

def ensure_enterprise_extension_tables(conn):
    try:
        conn.execute(ASSET_REGISTRY_TABLE_SQL)
        conn.commit()
    except Exception:
        pass

def _status_light(value, green_ok=True):
    if isinstance(value, str):
        v = value.lower()
        if v in ['healthy', 'good', 'low', 'green']:
            return '🟢'
        if v in ['attention', 'medium', 'yellow']:
            return '🟡'
        return '🔴'
    try:
        x = float(value)
        if green_ok:
            return '🟢' if x >= 85 else ('🟡' if x >= 65 else '🔴')
        return '🟢' if x <= 20 else ('🟡' if x <= 40 else '🔴')
    except Exception:
        return '🟡'

def build_executive_command_metrics(ticket_df, task_df, vendor_df, status_df, nas_df):
    t = add_priority_and_sla(ticket_df)
    total_open = int(t['status'].astype(str).isin(['Open','In Progress','On Hold - User Busy','On Hold']).sum()) if not t.empty else 0
    critical_breach = int((t.get('priority', pd.Series(dtype=str)).astype(str).eq('Critical') & t.get('sla_breach', pd.Series(dtype=bool)).fillna(False)).sum()) if not t.empty else 0
    overdue_tasks = int((task_df['status'].astype(str).isin(['Open','In Progress','On Hold']) if not task_df.empty and 'status' in task_df.columns else pd.Series(dtype=bool)).sum())
    open_vendor = int((vendor_df['followup_status'].astype(str).isin(['Pending from Vendor','Open','In Progress']) if not vendor_df.empty and 'followup_status' in vendor_df.columns else pd.Series(dtype=bool)).sum())
    active_team = int((status_df['status'].astype(str).isin(['Available','Busy','In Meeting']) if not status_df.empty and 'status' in status_df.columns else pd.Series(dtype=bool)).sum())
    sri = build_system_reliability_index(ticket_df)
    forecast = build_storage_forecast(nas_df)
    nas_health = 100.0
    if forecast is not None and not forecast.empty and 'latest_storage' in forecast.columns:
        nas_health = round(max(0, 100 - forecast['latest_storage'].astype(float).mean()), 1)
    res_rate = build_ticket_exec_metrics(ticket_df).get('resolution_rate', 0.0)
    return {
        'Total Open Tickets': total_open,
        'Critical SLA Breaches': critical_breach,
        'Overdue Tasks': overdue_tasks,
        'Open Vendor Cases': open_vendor,
        'Active Team Members': active_team,
        'System Reliability Index': sri,
        'NAS Health Score': nas_health,
        'Resolution Rate %': res_rate,
    }

def build_ticket_aging_analysis(df):
    x = add_priority_and_sla(df)
    if x.empty:
        return {'aging_table': pd.DataFrame(), 'most_aged': pd.DataFrame(), 'avg_pending_age': 0, 'oldest_ticket': pd.DataFrame(), 'trend': pd.DataFrame()}
    p = x[x['status'].astype(str).isin(['Open','In Progress','On Hold - User Busy','On Hold'])].copy()
    if p.empty:
        return {'aging_table': pd.DataFrame(), 'most_aged': pd.DataFrame(), 'avg_pending_age': 0, 'oldest_ticket': pd.DataFrame(), 'trend': pd.DataFrame()}
    p['age_days'] = (p['age_hours'] / 24).fillna(0)
    bins = [-1,1,3,7,15,100000]
    labels = ['0-1 Days','2-3 Days','4-7 Days','8-15 Days','15+ Days']
    p['aging_bucket'] = pd.cut(p['age_days'], bins=bins, labels=labels)
    aging = p.groupby('aging_bucket', as_index=False).agg(Tickets=('id','size')).fillna(0)
    trend = p.groupby(pd.to_datetime(p['date'], errors='coerce').dt.strftime('%Y-%m-%d'), as_index=False).agg(Avg_Age_Days=('age_days','mean'), Pending=('id','size')).rename(columns={'date':'bucket'})
    return {
        'aging_table': aging,
        'most_aged': p.sort_values('age_days', ascending=False).head(20),
        'avg_pending_age': round(p['age_days'].mean(), 1),
        'oldest_ticket': p.sort_values('age_days', ascending=False).head(1),
        'trend': trend,
    }

def build_technician_scorecard(df):
    x = add_priority_and_sla(df)
    perf = build_technician_performance(x)
    if perf.empty:
        return pd.DataFrame()
    frt = x.groupby('attended_by', as_index=False).agg(Avg_FRT=('frt_min', lambda s: round(pd.Series(s).dropna().mean(),1) if pd.Series(s).dropna().shape[0] else 0), SLA_Compliance=('sla_breach', lambda s: round((1 - pd.Series(s).fillna(False).mean())*100,1)))
    out = perf.merge(frt, on='attended_by', how='left')
    max_mttr = max(out['Avg_Resolution_Min'].max(), 1)
    max_pending = max(out['Pending'].max(), 1)
    out['Score'] = (
        out['Resolution_%'] * 0.40 +
        out['SLA_Compliance'] * 0.30 +
        ((1 - (out['Avg_Resolution_Min'] / max_mttr)) * 100).clip(lower=0) * 0.20 +
        ((1 - (out['Pending'] / max_pending)) * 100).clip(lower=0) * 0.10
    ).round(1)
    out['Rank_Band'] = pd.cut(out['Score'], bins=[-1,60,80,1000], labels=['Bronze','Silver','Gold'])
    return out.sort_values('Score', ascending=False)

def build_management_insights(ticket_df, nas_df, vendor_df):
    insights = []
    x = add_priority_and_sla(ticket_df)
    if x is not None and not x.empty:
        d = pd.to_datetime(x['date'], errors='coerce')
        x = x.assign(_month=d.dt.strftime('%Y-%m'))
        months = sorted([m for m in x['_month'].dropna().unique().tolist()])
        if len(months) >= 2:
            prev_m, cur_m = months[-2], months[-1]
            prev = x[x['_month']==prev_m]
            cur = x[x['_month']==cur_m]
            for cat in ['Network','Printer']:
                p = len(prev[prev['category'].astype(str).str.contains(cat, case=False, na=False)])
                c = len(cur[cur['category'].astype(str).str.contains(cat, case=False, na=False)])
                if p > 0:
                    change = round(((c-p)/p)*100,1)
                    direction = 'increased' if change > 0 else 'reduced'
                    insights.append({'Insight': f'{cat} incidents {direction} {abs(change)}% month-over-month'})
        top_loc = x.groupby('location').size().sort_values(ascending=False)
        if not top_loc.empty:
            insights.append({'Insight': f'{top_loc.index[0]} generated highest ticket load'})
        top_tech = x[x['status'].astype(str)=='Resolved'].groupby('attended_by').size().sort_values(ascending=False)
        if not top_tech.empty:
            share = round((top_tech.iloc[0] / max((x['status'].astype(str)=='Resolved').sum(),1))*100,1)
            insights.append({'Insight': f'{top_tech.index[0]} resolved {share}% of tickets'})
    nf = build_storage_forecast(nas_df)
    if nf is not None and not nf.empty and 'daily_growth_est' in nf.columns:
        insights.append({'Insight': 'NAS growth trending upward'})
    if vendor_df is not None and not vendor_df.empty and 'vendor_name' in vendor_df.columns:
        top_vendor = vendor_df.groupby('vendor_name').size().sort_values(ascending=False)
        if not top_vendor.empty:
            insights.append({'Insight': f'Vendor {top_vendor.index[0]} has highest pending cases'})
    return pd.DataFrame(insights[:8])

def build_vendor_performance(vendor_df):
    if vendor_df is None or vendor_df.empty:
        return {'table': pd.DataFrame(), 'heatmap': pd.DataFrame()}
    x = vendor_df.copy()
    x['resolved_flag'] = x['followup_status'].astype(str).isin(['Resolved','Closed'])
    x['open_flag'] = x['followup_status'].astype(str).isin(['Pending from Vendor','Open','In Progress'])
    x['due_date'] = pd.to_datetime(x.get('due_date'), errors='coerce')
    today = pd.Timestamp.now().normalize()
    x['escalation_flag'] = x['open_flag'] & x['due_date'].notna() & (x['due_date'] < today)
    out = x.groupby('vendor_name', as_index=False).agg(
        Cases_Assigned=('id','size'),
        Open_Cases=('open_flag','sum'),
        Resolved_Cases=('resolved_flag','sum'),
        Escalations=('escalation_flag','sum')
    )
    out['Average_Resolution_Days'] = ((out['Cases_Assigned'] - out['Open_Cases']).replace(0,1) * 2).round(1)
    out['SLA_Compliance'] = ((1 - (out['Escalations'] / out['Cases_Assigned'].replace(0,1))) * 100).round(1)
    heat = x.groupby(['vendor_name','followup_status'], as_index=False).agg(Cases=('id','size'))
    return {'table': out.sort_values('SLA_Compliance', ascending=False), 'heatmap': heat}

def build_department_health(df):
    x = add_priority_and_sla(df)
    if x.empty:
        return pd.DataFrame()
    out = x.groupby('department', as_index=False).agg(
        Tickets=('id','size'),
        Resolved=('status', lambda s: (s.astype(str)=='Resolved').sum()),
        Open=('status', lambda s: s.astype(str).isin(['Open','In Progress']).sum()),
        Pending=('status', lambda s: s.astype(str).isin(['Open','In Progress','On Hold - User Busy','On Hold']).sum()),
        MTTR=('resolution_time', lambda s: round(pd.to_numeric(s, errors='coerce').replace(0,pd.NA).dropna().mean(),1) if pd.to_numeric(s, errors='coerce').replace(0,pd.NA).dropna().shape[0] else 0),
        SLA_Breach=('sla_breach', lambda s: round(pd.Series(s).fillna(False).mean()*100,1))
    )
    total = max(out['Tickets'].sum(),1)
    out['SLA_%'] = (100 - out['SLA_Breach']).round(1)
    out['Load_%'] = ((out['Tickets']/total)*100).round(1)
    out['Risk_Score'] = (out['Pending']*2 + out['SLA_Breach']*0.5 + out['MTTR']*0.05).round(1)
    out['Department_Health'] = pd.cut(out['Risk_Score'], bins=[-1,20,45,100000], labels=['Healthy','Attention Needed','High Risk'])
    return out.sort_values('Risk_Score')

def build_month_over_month_comparison(df):
    x = add_priority_and_sla(df)
    if x.empty:
        return pd.DataFrame()
    x['_month'] = pd.to_datetime(x['date'], errors='coerce').dt.strftime('%Y-%m')
    months = sorted([m for m in x['_month'].dropna().unique().tolist()])
    if len(months) < 2:
        return pd.DataFrame()
    prev_m, cur_m = months[-2], months[-1]
    prev = x[x['_month']==prev_m]
    cur = x[x['_month']==cur_m]
    def m(df_):
        total = len(df_)
        resolved = (df_['status'].astype(str)=='Resolved').sum() if total else 0
        mttr = round(pd.to_numeric(df_.get('resolution_time'), errors='coerce').replace(0,pd.NA).dropna().mean(),1) if total else 0
        frt = round(pd.to_numeric(df_.get('frt_min'), errors='coerce').dropna().mean(),1) if total else 0
        sla = round((1-df_['sla_breach'].fillna(False).mean())*100,1) if total else 0
        return total, round((resolved/max(total,1))*100,1), mttr, frt, sla
    p_total, p_res, p_mttr, p_frt, p_sla = m(prev)
    c_total, c_res, c_mttr, c_frt, c_sla = m(cur)
    cmp = pd.DataFrame([
        ['Ticket Volume', p_total, c_total],
        ['Resolution Rate', p_res, c_res],
        ['MTTR', p_mttr, c_mttr],
        ['FRT', p_frt, c_frt],
        ['SLA %', p_sla, c_sla],
    ], columns=['Metric','Previous_Month','Current_Month'])
    cmp['Direction'] = cmp.apply(lambda r: '▲ Increase' if r['Current_Month'] > r['Previous_Month'] else ('▼ Decrease' if r['Current_Month'] < r['Previous_Month'] else '► No Change'), axis=1)
    return cmp

def load_assets_df(conn):
    try:
        return pd.read_sql_query('SELECT id, asset_id, asset_type, location, vendor, purchase_date, warranty_end, status FROM asset_registry ORDER BY id DESC', conn)
    except Exception:
        return pd.DataFrame(columns=['id','asset_id','asset_type','location','vendor','purchase_date','warranty_end','status'])

def create_asset(conn, payload):
    conn.execute('INSERT INTO asset_registry (asset_id, asset_type, location, vendor, purchase_date, warranty_end, status) VALUES (?, ?, ?, ?, ?, ?, ?)', (payload.get('asset_id'), payload.get('asset_type'), payload.get('location'), payload.get('vendor'), payload.get('purchase_date'), payload.get('warranty_end'), payload.get('status','Active')))
    conn.commit()

def build_asset_health(asset_df, ticket_df):
    if asset_df is None or asset_df.empty:
        return {'registry': pd.DataFrame(), 'near_expiry': pd.DataFrame(), 'recommendations': pd.DataFrame()}
    assets = asset_df.copy()
    tickets = add_priority_and_sla(ticket_df)
    if tickets is not None and not tickets.empty and 'complaint' in tickets.columns:
        def estimate_asset_type(txt):
            t = str(txt).lower()
            if 'printer' in t: return 'Printer'
            if 'camera' in t or 'cctv' in t: return 'Camera'
            if 'switch' in t: return 'Switch'
            if 'firewall' in t: return 'Firewall'
            if 'server' in t or 'nas' in t: return 'Server'
            if 'ups' in t: return 'UPS'
            if 'laptop' in t: return 'Laptop'
            return 'Desktop'
        tickets['asset_type_guess'] = tickets['complaint'].apply(estimate_asset_type)
        usage = tickets.groupby(['location','asset_type_guess'], as_index=False).agg(Tickets=('id','size'), Repeated_Failures=('complaint','nunique'))
        assets = assets.merge(usage, left_on=['location','asset_type'], right_on=['location','asset_type_guess'], how='left')
    assets['Tickets'] = assets.get('Tickets', 0).fillna(0)
    assets['Repeated_Failures'] = assets.get('Repeated_Failures', 0).fillna(0)
    today = pd.Timestamp.now().normalize()
    assets['warranty_end_parsed'] = pd.to_datetime(assets.get('warranty_end'), errors='coerce')
    assets['Days_to_Warranty_End'] = (assets['warranty_end_parsed'] - today).dt.days
    assets['Asset_Health_Index'] = (100 - (assets['Tickets']*3 + assets['Repeated_Failures']*5)).clip(lower=0)
    assets['Replacement_Recommendation'] = assets.apply(lambda r: 'Replace / Review' if (pd.notna(r['Days_to_Warranty_End']) and r['Days_to_Warranty_End'] <= 90) or r['Asset_Health_Index'] < 60 else 'Monitor', axis=1)
    near_expiry = assets[assets['Days_to_Warranty_End'].fillna(999999) <= 90]
    return {'registry': assets, 'near_expiry': near_expiry, 'recommendations': assets[['asset_id','asset_type','location','Asset_Health_Index','Replacement_Recommendation']].sort_values('Asset_Health_Index')}

def build_capacity_planning_dashboard(nas_df):
    forecast = build_storage_forecast(nas_df)
    if forecast is None or forecast.empty:
        return pd.DataFrame()
    today = pd.Timestamp.now().normalize()
    out = forecast.copy()
    out['Storage Growth Rate'] = out['daily_growth_est']
    out['Forecasted Capacity Date'] = out['projected_days_to_100'].apply(lambda d: (today + pd.Timedelta(days=float(d))).date().isoformat() if pd.notna(d) else None)
    out['Recommended Upgrade Date'] = out['projected_days_to_100'].apply(lambda d: (today + pd.Timedelta(days=max(float(d)-30,0))).date().isoformat() if pd.notna(d) else None)
    out['Storage Risk Level'] = out['projected_days_to_100'].apply(lambda d: 'High' if pd.notna(d) and float(d) <= 30 else ('Attention' if pd.notna(d) and float(d) <= 90 else 'Healthy'))
    out['Server Utilization %'] = out['latest_storage'].round(2)
    return out

def build_executive_pdf_bytes(ticket_df, nas_df, vendor_df, dept_df, tech_df, insights_df):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    y = h - 20*mm
    c.setFont('Helvetica-Bold', 16)
    c.drawString(20*mm, y, 'Executive Summary Report')
    y -= 10*mm
    c.setFont('Helvetica', 10)
    metrics = build_executive_command_metrics(ticket_df, load_tasks_df(conn_global_for_pdf), vendor_df, load_user_status_df(conn_global_for_pdf), nas_df) if 'conn_global_for_pdf' in globals() else {}
    for k, v in metrics.items():
        c.drawString(20*mm, y, f'{k}: {v}')
        y -= 6*mm
    def draw_df(title, df):
        nonlocal y
        c.setFont('Helvetica-Bold', 11)
        c.drawString(20*mm, y, title)
        y -= 6*mm
        c.setFont('Helvetica', 9)
        if df is None or df.empty:
            c.drawString(22*mm, y, 'No data available')
            y -= 6*mm
            return
        for _, row in df.head(5).iterrows():
            line = ' | '.join([f'{col}: {row[col]}' for col in df.columns[:4]])
            c.drawString(22*mm, y, str(line)[:110])
            y -= 5*mm
            if y < 20*mm:
                c.showPage(); y = h - 20*mm
    draw_df('Top Technicians', tech_df)
    draw_df('Department Load', dept_df)
    draw_df('Vendor Performance', vendor_df)
    draw_df('Capacity Risk', build_capacity_planning_dashboard(nas_df))
    draw_df('Management Insights', insights_df)
    c.save()
    return buf.getvalue()

def _month_options_from_df(df):
    if df is None or df.empty or 'date' not in df.columns:
        return []
    dt = pd.to_datetime(df['date'], errors='coerce').dropna()
    if dt.empty:
        return []
    periods = sorted(dt.dt.to_period('M').unique())
    return [str(p) for p in periods]

def _filter_df_by_month(df, selected_month):
    if df is None or df.empty or not selected_month or selected_month == 'All':
        return df
    dt = pd.to_datetime(df.get('date'), errors='coerce')
    return df[dt.dt.to_period('M').astype(str) == selected_month]




def get_navigation_groups(role):
    pages = get_role_pages(role)
    groups = {
        '📊 Dashboard': ['Home', 'Executive Command Center', 'Overview'],
        '🎫 Operations': ['Ticket Operations', 'Task Center', 'Team Chat'],
        '📈 Analytics': ['Reports', 'AVP Dashboard', 'Department Health', 'Vendor Dashboard'],
        '🖥 Infrastructure': ['NAS Monitoring', 'Asset Health'],
        '⚙ Administration': ['Admin Tools'],
    }
    return {g: [p for p in plist if p in pages] for g, plist in groups.items() if any(p in pages for p in plist)}

def page_breadcrumb(page):
    mapping = {
        'Home': 'Home', 'Executive Command Center': 'Home > Dashboard > Executive Command Center', 'Overview': 'Home > Dashboard > Overview',
        'Ticket Operations': 'Home > Operations > Ticket Operations', 'Task Center': 'Home > Operations > Task Center', 'Team Chat': 'Home > Operations > Team Chat',
        'Reports': 'Home > Analytics > Reports', 'AVP Dashboard': 'Home > Analytics > AVP Dashboard', 'Department Health': 'Home > Analytics > Department Health',
        'Vendor Dashboard': 'Home > Analytics > Vendor Dashboard', 'NAS Monitoring': 'Home > Infrastructure > NAS Monitoring', 'Asset Health': 'Home > Infrastructure > Asset Health',
        'Admin Tools': 'Home > Administration > Admin Tools',
    }
    return mapping.get(page, f'Home > {page}')

def inject_enterprise_ui_css():
    css = """
    <style>
    :root { --bg:#020617; --surface:#0F172A; --surface-2:#111827; --border:rgba(148,163,184,0.16); --text:#E5EEF9; --muted:#94A3B8; --primary:#3B82F6; --success:#10B981; --warning:#F59E0B; --danger:#EF4444; --shadow:0 14px 40px rgba(2,6,23,.28); --shadow-soft:0 8px 24px rgba(15,23,42,.22); --radius:18px; }
    .stApp, [data-testid='stAppViewContainer'], [data-testid='stHeader'] { background: radial-gradient(circle at top right, rgba(59,130,246,0.10), transparent 25%), linear-gradient(180deg, #020617 0%, #071122 100%); }
    [data-testid='stSidebar'] { background: linear-gradient(180deg, #0b1220 0%, #111827 100%) !important; border-right:1px solid var(--border); }
    [data-testid='stSidebarNav'] { display:none; }
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 1500px; }
    .sticky-topbar { position: sticky; top: .25rem; z-index: 30; backdrop-filter: blur(12px); background: rgba(2,6,23,.72); border:1px solid var(--border); border-radius: 18px; padding: 14px 18px; margin-bottom: 16px; box-shadow: var(--shadow-soft); }
    .app-hero { background: linear-gradient(135deg, rgba(59,130,246,.18), rgba(15,23,42,.96)); border:1px solid rgba(96,165,250,.24); border-radius: 24px; padding: 22px 24px; box-shadow: var(--shadow); }
    .eyebrow { color: var(--muted); font-size: 12px; letter-spacing: .08em; text-transform: uppercase; }
    .hero-title { font-size: 30px; font-weight: 800; color: white; margin: 4px 0 8px 0; }
    .hero-sub,.crumb,.last-updated,.feed-meta,.panel-sub,.kpi-sub,.kpi-title { color: var(--muted); }
    .crumb,.last-updated,.kpi-title { font-size:12px; }
    .kpi-card { background: linear-gradient(180deg, rgba(15,23,42,.98), rgba(18,32,51,.96)); border:1px solid var(--border); border-radius: var(--radius); padding: 16px; box-shadow: var(--shadow-soft); min-height: 136px; transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease; }
    .kpi-card:hover { transform: translateY(-2px); box-shadow: 0 16px 36px rgba(2,6,23,.34); border-color: rgba(96,165,250,.28); }
    .kpi-top { display:flex; justify-content:space-between; align-items:center; margin-bottom: 12px; }
    .kpi-icon { width: 38px; height:38px; border-radius: 12px; display:flex; align-items:center; justify-content:center; background: rgba(59,130,246,.14); color:#93C5FD; font-size:18px; }
    .kpi-value { color:#fff; font-size: 28px; font-weight: 800; line-height:1.1; font-variant-numeric: tabular-nums; }
    .trend-up { color: var(--success); } .trend-warn { color: var(--warning); } .trend-down { color: var(--danger); }
    .panel,.stTabs [data-baseweb='tab'], div[data-testid='stMetric'] { background: linear-gradient(180deg, rgba(15,23,42,.95), rgba(15,23,42,.88)); border:1px solid var(--border); border-radius: 16px; }
    .panel { padding:16px; box-shadow: var(--shadow-soft); }
    .panel-title,.feed-title { color:#fff; }
    .panel-title { font-size:18px; font-weight:700; margin-bottom:10px; }
    .action-btn-row .stButton>button { width:100%; border-radius: 14px; border:1px solid rgba(96,165,250,.18); background: linear-gradient(180deg, rgba(30,41,59,.98), rgba(15,23,42,.98)); color:#e5eef9; min-height: 46px; }
    .stTabs [data-baseweb='tab-list'] { gap: 8px; background: transparent; }
    .stTabs [data-baseweb='tab'] { padding: 10px 14px; }
    .stTabs [aria-selected='true'] { background: rgba(59,130,246,.14) !important; border-color: rgba(96,165,250,.34) !important; }
    .stDataFrame, div[data-testid='stDataFrame'] { border-radius: 16px; overflow: hidden; border:1px solid var(--border); }
    .feed-item { padding: 12px 0; border-bottom:1px solid rgba(148,163,184,.12); }
    .feed-item:last-child { border-bottom:none; }
    .insight-card { background: linear-gradient(180deg, rgba(30,41,59,.92), rgba(15,23,42,.96)); border:1px solid rgba(96,165,250,.16); border-radius:16px; padding:14px; min-height:100px; }
    @media (max-width: 900px) { .hero-title { font-size:24px; } .block-container { padding-left: .9rem !important; padding-right: .9rem !important; } }
    @media (max-width: 640px) { .kpi-card { min-height:auto; } }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_kpi_card(title, value, subtitle='', icon='📊', trend=None, tone='primary'):
    trend_cls = 'trend-up' if tone == 'success' else ('trend-warn' if tone == 'warning' else ('trend-down' if tone == 'danger' else ''))
    trend_html = f'<div class="kpi-sub {trend_cls}">{trend}</div>' if trend else ''
    st.markdown(f'<div class="kpi-card"><div class="kpi-top"><div><div class="kpi-title">{title}</div><div class="kpi-value">{value}</div></div><div class="kpi-icon">{icon}</div></div><div class="kpi-sub">{subtitle}</div>{trend_html}</div>', unsafe_allow_html=True)

def render_info_feed(title, rows, fields):
    st.markdown(f'<div class="panel"><div class="panel-title">{title}</div>', unsafe_allow_html=True)
    if rows is None or len(rows) == 0:
        st.info('No recent activity available.')
    else:
        for _, row in rows.iterrows():
            primary = ' · '.join([str(row.get(f, '')) for f in fields[:2] if str(row.get(f, '')) not in ['', 'nan']])
            meta = ' · '.join([str(row.get(f, '')) for f in fields[2:] if str(row.get(f, '')) not in ['', 'nan']])
            st.markdown(f'<div class="feed-item"><div class="feed-title">{primary}</div><div class="feed-meta">{meta}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_home_page(user, ticket_df, nas_df, conn):
    today = pd.Timestamp.now()
    st.markdown('<div class="crumb">Home</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="app-hero"><div class="eyebrow">Welcome</div><div class="hero-title">Welcome {user.get("display_name", "User")}</div><div class="hero-sub">Today: {today.strftime("%d %b %Y")} · Role: {user.get("role", "User")}</div></div>', unsafe_allow_html=True)
    st.markdown('')
    qa = st.columns(6)
    actions = [('New Ticket','Ticket Operations'),('Create Task','Task Center'),('Open Reports','Reports'),('Team Chat','Team Chat'),('View Assets','Asset Health'),('NAS Dashboard','NAS Monitoring')]
    st.markdown('<div class="action-btn-row">', unsafe_allow_html=True)
    for col, (label, target) in zip(qa, actions):
        with col:
            if st.button(label, key=f'home_{target}'):
                st.session_state['page'] = target
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    metrics = build_ticket_exec_metrics(ticket_df)
    cap = build_capacity_planning_dashboard(nas_df)
    nas_health = round(max(0, 100 - cap['latest_storage'].mean()), 1) if cap is not None and not cap.empty and 'latest_storage' in cap.columns else 0
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1: render_kpi_card('Open Tickets', metrics.get('pending',0), 'Current backlog', '🎫', tone='warning')
    with k2: render_kpi_card('Resolved Today', metrics.get('today_closed',0), 'Closed today', '✅', tone='success')
    with k3: render_kpi_card('SLA %', round(100 - add_priority_and_sla(ticket_df).get('sla_breach', pd.Series(dtype=bool)).fillna(False).mean()*100,1) if not ticket_df.empty else 0, 'Compliance view', '🎯')
    with k4: render_kpi_card('MTTR', metrics.get('avg_resolution',0), 'Average minutes', '⏱')
    with k5: render_kpi_card('NAS Health', nas_health, 'Storage posture', '🖥', tone='success' if nas_health >= 70 else 'warning')
    left, mid, right = st.columns([1.1,1.1,1])
    with left: render_info_feed('Recent Tickets', prepare_ticket_view(ticket_df).head(6) if ticket_df is not None else pd.DataFrame(), ['complaint','status','location','date'])
    with mid: render_info_feed('Recent Tasks', load_tasks_df(conn).head(6), ['title','status','assigned_to','due_date'])
    with right: render_info_feed('Recent Vendor Updates', load_vendor_followups_df(conn).head(6), ['vendor_name','followup_status','ticket_id','due_date'])
    st.markdown('<div class="panel"><div class="panel-title">Management Insights</div><div class="panel-sub">Auto-generated operational observations.</div></div>', unsafe_allow_html=True)
    insights = build_management_insights(ticket_df, nas_df, load_vendor_followups_df(conn))
    cols = st.columns(3)
    if insights is not None and not insights.empty:
        for i, insight in enumerate(insights.head(6)['Insight'].tolist()):
            with cols[i % 3]:
                st.markdown(f'<div class="insight-card">{insight}</div>', unsafe_allow_html=True)

def render_insight_cards(insights_df, columns_count=3):
    if insights_df is None or insights_df.empty:
        st.info("No insights available.")
        return
    cols = st.columns(columns_count)
    for i, insight in enumerate(insights_df[insights_df.columns[0]].astype(str).tolist()[:12]):
        with cols[i % columns_count]:
            st.markdown(f'<div class="insight-card">💡 {insight}</div>', unsafe_allow_html=True)

def render_global_search(conn, ticket_df):
    with st.sidebar.expander('🔎 Global Search', expanded=False):
        q = st.text_input('Search tickets, users, departments, technicians, vendors, assets, locations, tasks', key='global_search_q')
        if q:
            qt = str(q).lower(); results = []
            if ticket_df is not None and not ticket_df.empty:
                t = ticket_df.astype(str).apply(lambda c: c.str.lower()); mask = t.apply(lambda c: c.str.contains(qt, na=False)).any(axis=1)
                if mask.any():
                    for _, r in ticket_df.loc[mask].head(8).iterrows(): results.append(f"🎫 Ticket #{r.get('id','')} · {r.get('complaint','')} · {r.get('location','')}")
            task_df = load_tasks_df(conn)
            if task_df is not None and not task_df.empty:
                t = task_df.astype(str).apply(lambda c: c.str.lower()); mask = t.apply(lambda c: c.str.contains(qt, na=False)).any(axis=1)
                if mask.any():
                    for _, r in task_df.loc[mask].head(5).iterrows(): results.append(f"📌 Task #{r.get('id','')} · {r.get('title','')} · {r.get('assigned_to','')}")
            vendor_df = load_vendor_followups_df(conn)
            if vendor_df is not None and not vendor_df.empty:
                t = vendor_df.astype(str).apply(lambda c: c.str.lower()); mask = t.apply(lambda c: c.str.contains(qt, na=False)).any(axis=1)
                if mask.any():
                    for _, r in vendor_df.loc[mask].head(5).iterrows(): results.append(f"🏭 Vendor · {r.get('vendor_name','')} · Ticket {r.get('ticket_id','')}")
            assets_df = load_assets_df(conn) if 'load_assets_df' in globals() else pd.DataFrame()
            if assets_df is not None and not assets_df.empty:
                t = assets_df.astype(str).apply(lambda c: c.str.lower()); mask = t.apply(lambda c: c.str.contains(qt, na=False)).any(axis=1)
                if mask.any():
                    for _, r in assets_df.loc[mask].head(5).iterrows(): results.append(f"📦 Asset · {r.get('asset_id','')} · {r.get('location','')}")
            [st.caption(r) for r in results[:12]] if results else st.caption('No matching records found.')

def render_dashboard(conn):
    user = st.session_state.get("current_user", {})
    role = user.get("role", "IT Executive")
    display_name = user.get("display_name", "Guest")
    inject_enterprise_ui_css()
    df_tickets = prepare_ticket_view(load_tickets())
    df_nas = load_nas_data()
    st.sidebar.markdown(f"👤 **{display_name}** ({role})")
    notif_df = load_notifications_df(conn, user.get("username"))
    unread_count = int((notif_df["is_read"] == 0).sum()) if not notif_df.empty and "is_read" in notif_df.columns else 0
    st.sidebar.caption(f"Notifications: {unread_count}")
    if st.sidebar.button("Logout"):
        st.session_state["current_user"] = None
        st.session_state["must_set_password"] = False
        st.rerun()
    allowed_pages = get_role_pages(role)
    render_global_search(conn, df_tickets)
    st.sidebar.markdown("---")
    site_filter = st.sidebar.selectbox("Site", ["All"] + OFFICIAL_LOCATIONS)
    status_filter = st.sidebar.selectbox("Ticket Status", ["All"] + STATUS_OPTIONS)
    tech_filter = st.sidebar.selectbox("Technician", ["All"] + list(TECH_MAP.keys()))
    server_filter = st.sidebar.selectbox("NAS Server", ["All"] + SERVER_NAMES)
    st.sidebar.markdown("---")
    current_page = st.session_state.get("page", "Home" if "Home" in allowed_pages else allowed_pages[0])
    for group, pages in get_navigation_groups(role).items():
        with st.sidebar.expander(group, expanded=(current_page in pages)):
            for p in pages:
                label = f"➤ {p}" if p == current_page else p
                if st.button(label, key=f"nav_{group}_{p}", use_container_width=True):
                    st.session_state["page"] = p
                    st.rerun()
    page = st.session_state.get("page", "Home" if "Home" in allowed_pages else allowed_pages[0])
    if page not in allowed_pages:
        page = allowed_pages[0]
        st.session_state["page"] = page
    st.sidebar.markdown("---")
    if db_connected:
        st.sidebar.success("Supabase cloud connected")
    else:
        st.sidebar.warning("Session sandbox mode active")
    df_ticket_filtered = filtered_tickets(df_tickets, site_filter, status_filter, tech_filter)
    df_nas_filtered = filtered_nas(df_nas, server_filter)
    st.markdown(f'''<div class="sticky-topbar"><div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px"><div><div class="crumb">{page_breadcrumb(page)}</div><div class="hero-title" style="font-size:24px;margin:0">{page}</div></div><div class="last-updated">Updated:<br>{pd.Timestamp.now().strftime('%d %b %Y')}<br>{pd.Timestamp.now().strftime('%I:%M %p')}</div></div></div>''', unsafe_allow_html=True)
    st.markdown("<div class='app-banner'><div class='app-title'>🛠️ Vega & Knitpro IT Command Suite</div><div class='app-subtitle'>Single-window support operations, NAS monitoring, reporting, tasking, and infrastructure analytics</div></div>", unsafe_allow_html=True)
    if page == "Home":
        render_home_page(user, df_ticket_filtered, df_nas_filtered, conn)

    elif page == "Overview":
        st.subheader("Operations Overview")
        overview_df = add_priority_and_sla(df_ticket_filtered)
        total_tickets = len(overview_df)
        resolved_tickets = int((overview_df["status"].astype(str) == "Resolved").sum()) if not overview_df.empty else 0
        open_tickets = int((overview_df["status"].astype(str).isin(["Open", "In Progress"])).sum()) if not overview_df.empty else 0
        hold_tickets = int((overview_df["status"].astype(str).isin(["On Hold - User Busy", "On Hold"])).sum()) if not overview_df.empty else 0
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Tickets", total_tickets)
        c2.metric("Resolved", resolved_tickets)
        c3.metric("Open", open_tickets)
        c4.metric("On Hold", hold_tickets)

        st.markdown("#### Queue filters")
        selected_queue_filter = render_clickable_metric_filters()
        queue_view = filter_queue_by_metric(overview_df, selected_queue_filter)

        trend_tabs = st.tabs(["Daily Trend", "Weekly Trend", "Monthly Trend", "Location vs Issue Heatmap"])
        with trend_tabs[0]:
            trend = build_ticket_trend(overview_df, freq="Daily")
            if trend.empty:
                st.info("No daily trend data available.")
            else:
                chart = alt.Chart(trend).mark_area(opacity=0.35).encode(x="bucket:N", y="Tickets:Q", tooltip=["bucket", "Tickets", "Resolved"]).properties(height=320)
                st.altair_chart(chart, use_container_width=True)
        with trend_tabs[1]:
            trend = build_ticket_trend(overview_df, freq="Weekly")
            if trend.empty:
                st.info("No weekly trend data available.")
            else:
                chart = alt.Chart(trend).mark_line(point=True).encode(x="bucket:N", y="Tickets:Q", tooltip=["bucket", "Tickets", "Resolved"]).properties(height=320)
                st.altair_chart(chart, use_container_width=True)
        with trend_tabs[2]:
            trend = build_ticket_trend(overview_df, freq="Monthly")
            if trend.empty:
                st.info("No monthly trend data available.")
            else:
                chart = alt.Chart(trend).mark_line(point=True).encode(x="bucket:N", y="Tickets:Q", tooltip=["bucket", "Tickets", "Resolved"]).properties(height=320)
                st.altair_chart(chart, use_container_width=True)
        with trend_tabs[3]:
            st.altair_chart(build_location_issue_heatmap(overview_df).properties(height=420), use_container_width=True)

        st.markdown("#### Active queue with SLA indicators")
        breach_view = build_sla_breach_view(queue_view)
        if breach_view.empty:
            st.info("No active queue records available.")
        else:
            st.dataframe(breach_view, use_container_width=True)
    elif page == "Ticket Operations":
        st.subheader("Ticket Operations")
        left, right = st.columns([1.05, 1.2], gap="large")
        with left:
            st.markdown("### Log New Ticket")
            st.markdown("<div class='section-note'>Use existing user details when possible. Keep complaint text short but specific.</div>", unsafe_allow_html=True)
            existing_users = sorted(df_tickets["user_name"].dropna().astype(str).unique().tolist()) if not df_tickets.empty else []
            selected_user = st.selectbox("Use existing user details", ["New User Type Below"] + existing_users)
            default_username, default_dept, default_loc = "", "", OFFICIAL_LOCATIONS[0]
            if selected_user != "New User Type Below" and not df_tickets.empty:
                hist = df_tickets[df_tickets["user_name"] == selected_user].sort_values("id", ascending=False)
                if not hist.empty:
                    default_username, default_dept, default_loc = selected_user, str(hist.iloc[0].get("department", "")), str(hist.iloc[0].get("location", OFFICIAL_LOCATIONS[0]))
            with st.form("new_ticket_form", clear_on_submit=True):
                a1, a2 = st.columns(2)
                user_name = a1.text_input("User Name", value=default_username)
                attended_by = a2.selectbox("Technician", list(TECH_MAP.keys()))
                b1, b2 = st.columns(2)
                department = b1.text_input("Department", value=default_dept)
                status = b2.selectbox("Initial Status", STATUS_OPTIONS)
                loc_index = OFFICIAL_LOCATIONS.index(default_loc) if default_loc in OFFICIAL_LOCATIONS else 0
                location = st.selectbox("Location / Sector", OFFICIAL_LOCATIONS, index=loc_index)
                ticket_date = st.date_input("Ticket Date", value=datetime.now().date())
                st.markdown("#### Ticket Classification")
                complaint_desc = st.text_area("Complaint Description", height=110, help="Write the issue clearly. Category is suggested from the complaint, and the technician can change it manually.")
                suggested_category = auto_categorize(complaint_desc) if complaint_desc.strip() else "Other"
                category_options = list(CATEGORY_MASTER.keys())
                cat_index = category_options.index(suggested_category) if suggested_category in category_options else category_options.index("Other")
                category = st.selectbox("Category *", ["Select Category"] + category_options, index=(cat_index + 1 if complaint_desc.strip() and suggested_category in category_options else 0), help="Technician must choose the closest category before saving.")
                if complaint_desc.strip():
                    st.caption(f"Suggested from complaint: {suggested_category}")
                tech_remarks = st.text_area("Technician Remarks", height=90)
                c1, c2 = st.columns(2)
                start_input = c1.time_input("Start Time", value=time(datetime.now().hour, datetime.now().minute))
                close_input = c2.time_input("Close Time", value=time(datetime.now().hour, datetime.now().minute))
                submitted = st.form_submit_button("Submit Ticket", use_container_width=True)
                if submitted:
                    if not user_name.strip() or not department.strip() or not complaint_desc.strip() or category == "Select Category":
                        st.error("Please fill all required fields, including Category.")
                    else:
                        category = normalize_category(category)
                        date_str = ticket_date.strftime("%Y-%m-%d")
                        if status == "Open": start_val, close_val, duration = None, None, 0
                        elif status == "In Progress": start_val, close_val, duration = f"{date_str} {start_input.strftime('%H:%M:%S')}", None, 0
                        elif status == "On Hold - User Busy": start_val, close_val, duration = None, None, 0
                        else:
                            start_val = f"{date_str} {start_input.strftime('%H:%M:%S')}"; close_val = f"{date_str} {close_input.strftime('%H:%M:%S')}"
                            duration = max(1, int((datetime.combine(ticket_date, close_input) - datetime.combine(ticket_date, start_input)).total_seconds() // 60))
                        new_row = {"date": date_str, "user_name": user_name.strip(), "department": department.strip(), "complaint": complaint_desc.strip(), "location": location, "attended_by": attended_by, "status": status, "category": category, "remarks": tech_remarks.strip(), "start_time": start_val, "close_time": close_val, "resolution_time": duration}
                        try:
                            new_id = save_ticket(new_row)
                            add_notification(conn, attended_by.lower(), f"New ticket assigned: {user_name.strip()} - {category}")
                            st.success(f"Ticket saved successfully: {format_ticket_number(new_id, location)}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Insertion error: {e}")
            st.markdown("### AI Copilot")
            ai_text = st.text_area("Paste issue text for troubleshooting help", height=120)
            ai_lang = st.radio("Language", ["English", "Hindi"], horizontal=True)
            if st.button("Run AI Guidance", use_container_width=True):
                if not ai_text.strip(): st.warning("Please enter issue details first.")
                else:
                    cat = auto_categorize(ai_text); details = AI_SUGGESTIONS.get(cat)
                    if details:
                        title = details["title_en"] if ai_lang == "English" else details["title_hi"]
                        steps = details["English"] if ai_lang == "English" else details["Hindi"]
                        html = f"<div class='panel-card'><div style='font-weight:700;color:#f87171;margin-bottom:8px'>{title}</div>" + "".join([f"<div style='margin-bottom:6px'>• {step}</div>" for step in steps]) + "</div>"
                        st.markdown(html, unsafe_allow_html=True)
                    else: st.info("No specific category found. Use standard physical, network, and access checks.")
        with right:
            if df_ticket_filtered.empty:
                st.info("No tickets found for the current filters.")
            else:
                queue_df = df_ticket_filtered.sort_values("id", ascending=False).copy()
                st.markdown("### Update Existing Ticket")
                ticket_options = {f"{row['System Ticket ID']} | {row['user_name']} | {row['status']}": int(row['id']) for _, row in queue_df.iterrows()}
                selected_label = st.selectbox("Choose a ticket", list(ticket_options.keys()))
                target_id = ticket_options[selected_label]
                target_row = queue_df[queue_df["id"] == target_id].iloc[0]
                st.markdown(f"<div class='summary-card'><div class='summary-grid'><div><div class='sum-label'>User</div><div class='sum-value'>{target_row['user_name']}</div></div><div><div class='sum-label'>Department</div><div class='sum-value'>{target_row['department']}</div></div><div><div class='sum-label'>Location</div><div class='sum-value'>{target_row['location']}</div></div><div><div class='sum-label'>Status</div><div class='sum-value'>{target_row['status']}</div></div><div class='span-2'><div class='sum-label'>Complaint</div><div class='sum-value'>{target_row['complaint']}</div></div></div></div>", unsafe_allow_html=True)
                with st.form(f"update_ticket_form_{target_id}"):
                    u1, u2 = st.columns(2)
                    current_status_idx = STATUS_OPTIONS.index(target_row["status"]) if target_row["status"] in STATUS_OPTIONS else 0
                    tech_list = list(TECH_MAP.keys())
                    current_tech_idx = tech_list.index(target_row["attended_by"]) if target_row["attended_by"] in tech_list else 0
                    new_status = u1.selectbox("Modify Status", STATUS_OPTIONS, index=current_status_idx)
                    new_tech = u2.selectbox("Reassign Technician", tech_list, index=current_tech_idx)
                    new_duration = st.number_input("Resolution Duration (minutes)", min_value=0, value=int(target_row["resolution_time"]) if pd.notna(target_row["resolution_time"]) else 0)
                    new_remarks = st.text_area("Update Remarks", value=str(target_row.get("remarks", "")), height=90)
                    if st.form_submit_button("Save Changes"):
                        final_remarks = new_remarks.strip()
                        if new_status == "On Hold - User Busy" and not final_remarks:
                            final_remarks = "Technician reached user, but action postponed due to business activity."
                        payload = {"status": new_status, "attended_by": new_tech, "resolution_time": int(new_duration), "remarks": final_remarks}
                        if new_status == "Resolved" and not target_row.get("close_time"): payload["close_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        try:
                            update_ticket(target_id, payload)
                            add_notification(conn, new_tech.lower(), f"Ticket updated: {format_ticket_number(target_id, target_row['location'])}")
                            st.success("Ticket updated successfully.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Update error: {e}")
                st.markdown("### Vendor Follow-up")
                with st.form(f"vendor_followup_{target_id}"):
                    v1, v2 = st.columns(2)
                    vendor_name = v1.text_input("Vendor Name")
                    followup_status = v2.selectbox("Follow-up Status", ["Pending from Vendor", "Follow-up Done", "Resolved by Vendor"])
                    vendor_remark = st.text_area("Vendor Remark", height=80)
                    due_date = st.date_input("Vendor Due Date", value=datetime.now().date())
                    if st.form_submit_button("Add Vendor Follow-up"):
                        add_vendor_followup(conn, int(target_id), vendor_name.strip(), followup_status, vendor_remark.strip(), due_date.strftime("%Y-%m-%d"))
                        st.success("Vendor follow-up added.")
                _, delete_col2 = st.columns([1.7, 1])
                with delete_col2:
                    st.markdown("<div class='danger-box'><h4>Delete Ticket</h4><div class='mini-note'>Delete only if incorrect.</div></div>", unsafe_allow_html=True)
                    confirm_ticket_delete = st.checkbox("I confirm delete.")
                    if st.button("Delete Selected Ticket", disabled=not confirm_ticket_delete, use_container_width=True):
                        try:
                            delete_ticket(target_id)
                            st.success("Ticket deleted successfully.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Delete error: {e}")
                st.markdown("### Active Queue")
                render_status_table(queue_df.head(10), ["System Ticket ID", "date", "user_name", "department", "location", "category", "attended_by", "status"], compact=True)
    elif page == "NAS Monitoring":
        st.subheader("NAS Monitoring")
        t1, t2, t3, t4 = st.tabs(["Log Entry", "Health Dashboard", "Raw Logs", "Delete Wrong Entry"])
        with t1:
            st.markdown("### Log Backup Entry")
            with st.form("nas_form", clear_on_submit=True):
                n1, n2 = st.columns(2)
                log_date = n1.date_input("Backup Date", value=datetime.now().date())
                server_name = n2.selectbox("Server Name", SERVER_NAMES)
                st.caption(f"Mapped worksheet reference: {SERVER_SHEET_MAP.get(server_name, 'NA')}")
                n3, n4 = st.columns(2)
                log_status = n3.selectbox("Backup Status", ["Success", "Failed"])
                log_storage_kb = n4.number_input("Storage Used KB", min_value=0.0, step=1024.0)
                st.caption(f"Automatic conversion preview: {round(log_storage_kb / 1024 / 1024, 4)} GB")
                log_remarks = st.text_area("Operational Remarks / Error Logs", height=90)
                if st.form_submit_button("Submit Backup Log"):
                    try:
                        new_id = save_nas_log({"date": log_date.strftime("%Y-%m-%d"), "server_name": server_name, "status": log_status, "storage_used": round(float(log_storage_kb / 1024 / 1024), 4), "remarks": log_remarks.strip()})
                        st.success(f"NAS log saved successfully. Entry ID: {new_id}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"NAS save error: {e}")
        with t2:
            st.markdown("### Health Dashboard")
            if df_nas_filtered.empty:
                st.info("No NAS logs found for the selected filter.")
            else:
                selected_server = st.selectbox("Choose server view", SERVER_NAMES, key="nas_server_dashboard")
                server_df = df_nas[df_nas["server_name"] == selected_server].copy()
                if server_df.empty:
                    st.info("No logs available for this server.")
                else:
                    server_df["date"] = pd.to_datetime(server_df["date"], errors="coerce"); server_df = server_df.sort_values("date")
                    server_df["Change GB"] = server_df["storage_used"].diff().round(4)
                    server_df["Change %"] = (server_df["storage_used"].pct_change() * 100).round(2)
                    latest = server_df.iloc[-1]
                    if latest["status"] == "Failed":
                        st.error(f"Critical alert: latest backup on {latest['date'].strftime('%Y-%m-%d')} for {selected_server} failed.")
                    else:
                        st.success(f"Latest backup on {latest['date'].strftime('%Y-%m-%d')} for {selected_server} completed successfully.")
                    m1, m2, m3 = st.columns(3)
                    delta_text = f"{server_df.iloc[-1]['Change GB']:.4f} GB" if len(server_df) >= 2 and pd.notna(server_df.iloc[-1]['Change GB']) else "Baseline"
                    m1.metric("Latest Footprint", f"{latest['storage_used']:.4f} GB", delta=delta_text)
                    m2.metric("Total Logs", len(server_df))
                    m3.metric("Failures", int((server_df['status'] == 'Failed').sum()))
                    server_df["date_label"] = server_df["date"].dt.strftime("%Y-%m-%d")
                    st.markdown("### Storage Trend")
                    st.altair_chart(build_line_chart(server_df, "date_label:N", "storage_used:Q", "#3b82f6"), use_container_width=True)
                    table_df = server_df.sort_values("date", ascending=False).copy()
                    table_df["storage_used"] = table_df["storage_used"].map(lambda x: f"{x:.4f} GB")
                    table_df["Change GB"] = table_df["Change GB"].apply(lambda x: f"{x:.4f} GB" if pd.notnull(x) else "Baseline")
                    table_df["Change %"] = table_df["Change %"].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "Baseline")
                    render_status_table(table_df, ["id", "date", "server_name", "status", "storage_used", "Change GB", "Change %", "remarks"], compact=True, nas_mode=True)
        with t3:
            st.markdown("### Raw NAS Logs")
            if df_nas_filtered.empty: st.info("No NAS records found.")
            else:
                raw_view = df_nas_filtered.sort_values(["date", "id"], ascending=[False, False]).copy(); raw_view["storage_used"] = raw_view["storage_used"].map(lambda x: f"{x:.4f} GB")
                render_status_table(raw_view, ["id", "date", "server_name", "status", "storage_used", "remarks"], compact=True, nas_mode=True)
        with t4:
            st.markdown("### Delete Wrong NAS Entry")
            st.warning("Use this only when an incorrect backup log was entered.")
            if df_nas.empty: st.info("No NAS entries available to delete.")
            else:
                delete_view = df_nas.sort_values(["date", "id"], ascending=[False, False]).copy()
                delete_view["entry_label"] = delete_view.apply(lambda r: f"ID {r['id']} | {r['date']} | {r['server_name']} | {r['status']} | {r['storage_used']:.4f} GB", axis=1)
                selected_entry = st.selectbox("Select wrong NAS entry", delete_view["entry_label"].tolist())
                row = delete_view[delete_view["entry_label"] == selected_entry].iloc[0]
                confirm_delete = st.checkbox("I confirm this entry is wrong and should be deleted.")
                if st.button("Delete Selected NAS Entry", disabled=not confirm_delete):
                    try:
                        delete_nas_log(int(row["id"])); st.success(f"NAS entry ID {int(row['id'])} deleted."); st.rerun()
                    except Exception as e:
                        st.error(f"Delete error: {e}")
    elif page == "Reports":
        st.subheader("Reports")
        report_tabs = st.tabs(["Analysis Tables", "Detailed Reports", "NAS Forecast", "Excel Export"])

        st.markdown('''<div class="panel"><div class="panel-title">Analytics Center</div><div class="panel-sub">Executive, SLA, technician, department, site, asset, NAS, and insights views remain available through the existing reports plus the new management report layer.</div></div>''', unsafe_allow_html=True)
        with report_tabs[0]:
            st.markdown("### Detailed Analysis Tables")
            analysis_tabs = st.tabs(["Technician Performance", "Department Summary", "Location Summary", "Repeat Issues"])
            with analysis_tabs[0]:
                st.dataframe(build_technician_performance(df_ticket_filtered), use_container_width=True)
            with analysis_tabs[1]:
                st.dataframe(build_department_summary(df_ticket_filtered), use_container_width=True)
            with analysis_tabs[2]:
                st.dataframe(build_location_summary(df_ticket_filtered), use_container_width=True)
            with analysis_tabs[3]:
                st.dataframe(build_repeat_issue_summary(df_ticket_filtered), use_container_width=True)

        with report_tabs[1]:
            detailed = build_detailed_ticket_exports(df_ticket_filtered)
            grouped = build_grouped_detail_views(df_ticket_filtered)
            month_options = ["All"] + _month_options_from_df(df_ticket_filtered)
            selected_month = st.selectbox("Select month for ticket detailed reports", month_options, key="tickets_report_month")
            selected_ticket_df = _filter_df_by_month(df_ticket_filtered, selected_month)
            detailed = build_detailed_ticket_exports(selected_ticket_df)
            grouped = build_grouped_detail_views(selected_ticket_df)
            detail_tabs = st.tabs(["All Logs", "Monthly Detail", "Weekly Detail", "Technician Detail", "Site Detail", "MTTR & SLA"])
            with detail_tabs[0]:
                frame = detailed.get("Master Tickets", pd.DataFrame())
                if frame.empty:
                    st.info("No ticket logs available.")
                else:
                    st.dataframe(frame, use_container_width=True)
                    st.download_button("Download all_ticket_logs CSV", frame.to_csv(index=False).encode("utf-8"), "all_ticket_logs.csv", "text/csv")
            with detail_tabs[1]:
                frame = grouped.get("monthly_detail", pd.DataFrame())
                if frame.empty:
                    st.info("No monthly detail available.")
                else:
                    st.dataframe(frame, use_container_width=True)
                    st.download_button("Download monthly_detail CSV", frame.to_csv(index=False).encode("utf-8"), "monthly_detail.csv", "text/csv")
            with detail_tabs[2]:
                frame = grouped.get("weekly_detail", pd.DataFrame())
                if frame.empty:
                    st.info("No weekly detail available.")
                else:
                    st.dataframe(frame, use_container_width=True)
                    st.download_button("Download weekly_detail CSV", frame.to_csv(index=False).encode("utf-8"), "weekly_detail.csv", "text/csv")
            with detail_tabs[3]:
                frame = grouped.get("technician_detail", pd.DataFrame())
                if frame.empty:
                    st.info("No technician detail available.")
                else:
                    st.dataframe(frame, use_container_width=True)
                    st.download_button("Download technician_detail CSV", frame.to_csv(index=False).encode("utf-8"), "technician_detail.csv", "text/csv")
            with detail_tabs[4]:
                frame = grouped.get("site_detail", pd.DataFrame())
                if frame.empty:
                    st.info("No site detail available.")
                else:
                    st.dataframe(frame, use_container_width=True)
                    st.download_button("Download site_detail CSV", frame.to_csv(index=False).encode("utf-8"), "site_detail.csv", "text/csv")
            with detail_tabs[5]:
                mt1 = build_mttr_sla_summary(add_priority_and_sla(prepare_ticket_view(selected_ticket_df)).assign(Month=pd.to_datetime(prepare_ticket_view(selected_ticket_df).get("date"), errors="coerce").dt.strftime("%Y-%m")), "Month") if not selected_ticket_df.empty else pd.DataFrame()
                mt2 = build_mttr_sla_summary(add_priority_and_sla(prepare_ticket_view(selected_ticket_df)).assign(Week=pd.to_datetime(prepare_ticket_view(selected_ticket_df).get("date"), errors="coerce").dt.strftime("%Y-W") + pd.to_datetime(prepare_ticket_view(selected_ticket_df).get("date"), errors="coerce").dt.isocalendar().week.astype(str)), "Week") if not selected_ticket_df.empty else pd.DataFrame()
                mt3 = build_mttr_sla_summary(prepare_ticket_view(selected_ticket_df), "attended_by")
                mt4 = build_mttr_sla_summary(prepare_ticket_view(selected_ticket_df), "location")
                sub_tabs = st.tabs(["Month", "Week", "Technician", "Site"])
                for tab, frame in zip(sub_tabs, [mt1, mt2, mt3, mt4]):
                    with tab:
                        if frame.empty:
                            st.info("No metrics available.")
                        else:
                            st.dataframe(frame, use_container_width=True)

        with report_tabs[2]:
            raw_nas = normalize_nas_df(df_nas_filtered)
            month_options = ["All"] + _month_options_from_df(raw_nas)
            selected_month = st.selectbox("Select month for NAS detailed reports", month_options, key="nas_report_month")
            selected_nas_df = _filter_df_by_month(raw_nas, selected_month)
            deltas = compute_nas_changes(selected_nas_df)
            forecast = build_storage_forecast(selected_nas_df)
            nas_tabs = st.tabs(["Raw NAS Logs", "Delta Logs", "Forecast"])
            for tab, frame, filename in zip(nas_tabs, [selected_nas_df, deltas, forecast], ["raw_nas_logs.csv", "nas_delta_logs.csv", "nas_forecast.csv"]):
                with tab:
                    if frame.empty:
                        st.info("No NAS data available.")
                    else:
                        st.dataframe(frame, use_container_width=True)
                        st.download_button(f"Download {filename}", frame.to_csv(index=False).encode("utf-8"), filename, "text/csv")

        with report_tabs[3]:
            excel_blob = build_excel_report(df_ticket_filtered, df_nas_filtered)
            st.download_button("Download detailed multi-tab Excel workbook", data=excel_blob, file_name="vega_knitpro_detailed_reports.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        st.markdown("### Advanced Management Reports")
        adv_tabs = st.tabs(["Executive Summary", "Ticket Aging Report", "SLA Compliance Report", "Vendor Performance Report", "Technician Scorecard Report", "Department Health Report", "Capacity Planning Report", "Asset Health Report", "Management Insights Report", "Executive PDF Export"])
        aging_pack = build_ticket_aging_analysis(df_ticket_filtered)
        vendor_perf = build_vendor_performance(load_vendor_followups_df(conn))
        tech_score = build_technician_scorecard(df_ticket_filtered)
        dept_health = build_department_health(df_ticket_filtered)
        capacity = build_capacity_planning_dashboard(df_nas_filtered)
        assets = build_asset_health(load_assets_df(conn), df_ticket_filtered)
        insights = build_management_insights(df_ticket_filtered, df_nas_filtered, load_vendor_followups_df(conn))
        mom = build_month_over_month_comparison(df_ticket_filtered)
        adv_frames = [
            mom,
            aging_pack.get('aging_table', pd.DataFrame()),
            build_mttr_sla_summary(prepare_ticket_view(df_ticket_filtered), 'location'),
            vendor_perf.get('table', pd.DataFrame()),
            tech_score,
            dept_health,
            capacity,
            assets.get('registry', pd.DataFrame()),
            insights,
        ]
        adv_names = ["executive_summary","ticket_aging_report","sla_compliance_report","vendor_performance_report","technician_scorecard_report","department_health_report","capacity_planning_report","asset_health_report","management_insights_report"]
        for tab, frame, fname in zip(adv_tabs[:-1], adv_frames, adv_names):
            with tab:
                if frame is None or frame.empty:
                    st.info("No data available.")
                else:
                    st.dataframe(frame, use_container_width=True)
                    st.download_button(f"Download {fname} CSV", frame.to_csv(index=False).encode('utf-8'), f"{fname}.csv", 'text/csv', key=f"dl_{fname}")
        with adv_tabs[-1]:
            pdf_blob = build_executive_pdf_bytes(df_ticket_filtered, df_nas_filtered, vendor_perf.get('table', pd.DataFrame()), dept_health, tech_score, insights)
            st.download_button("Download Executive PDF Report", data=pdf_blob, file_name="executive_summary_report.pdf", mime="application/pdf")
    elif page == "Task Center":
        st.subheader("Task Center")
        tasks_df = load_tasks_df(conn)
        comments_df = load_task_comments_df(conn)
        t1, t2, t3, t4 = st.columns(4)
        t1.metric("Total Tasks", len(tasks_df))
        t2.metric("Open", int((tasks_df["status"] == "Open").sum()) if not tasks_df.empty and "status" in tasks_df.columns else 0)
        t3.metric("In Progress", int((tasks_df["status"] == "In Progress").sum()) if not tasks_df.empty and "status" in tasks_df.columns else 0)
        t4.metric("Completed", int((tasks_df["status"].isin(["Closed", "Completed"]).sum())) if not tasks_df.empty and "status" in tasks_df.columns else 0)

        task_tabs = st.tabs(["Task Board", "Update Task", "Comments", "My Queue"])

        with task_tabs[0]:
            if tasks_df.empty:
                st.info("No tasks available.")
            else:
                board = tasks_df.copy()
                st.dataframe(board, use_container_width=True)

        with task_tabs[1]:
            if tasks_df.empty:
                st.info("No tasks available for update.")
            else:
                task_ids = tasks_df["id"].astype(int).tolist()
                selected_task = st.selectbox("Select task ID", task_ids, key="task_update_id")
                row = tasks_df[tasks_df["id"] == selected_task].iloc[0]
                new_status = st.selectbox("Status", ["Open", "In Progress", "On Hold", "Closed", "Completed"], index=["Open", "In Progress", "On Hold", "Closed", "Completed"].index(row["status"]) if row["status"] in ["Open", "In Progress", "On Hold", "Closed", "Completed"] else 0, key="task_update_status")
                new_progress = st.slider("Progress", 0, 100, int(row["progress"]) if pd.notna(row["progress"]) else 0, key="task_update_progress")
                new_assignee = st.selectbox("Assigned to", ["Satish", "Priyanshu", "Amit", "Ranjan", "Manish"], index=["Satish", "Priyanshu", "Amit", "Ranjan", "Manish"].index(row["assigned_to"]) if row["assigned_to"] in ["Satish", "Priyanshu", "Amit", "Ranjan", "Manish"] else 0, key="task_update_assignee")
                if st.button("Save Task Update", key="task_update_save"):
                    update_task(conn, selected_task, {"status": new_status, "progress": int(new_progress), "assigned_to": new_assignee})
                    st.success("Task updated successfully.")
                    st.rerun()

        with task_tabs[2]:
            if tasks_df.empty:
                st.info("No tasks available for comments.")
            else:
                comment_task = st.selectbox("Task for comment", tasks_df["id"].astype(int).tolist(), key="task_comment_task")
                comment_text = st.text_area("Add comment", key="task_comment_text")
                if st.button("Post Comment", key="task_comment_post"):
                    if not str(comment_text).strip():
                        st.error("Comment cannot be empty.")
                    else:
                        add_task_comment(conn, int(comment_task), comment_text.strip(), display_name)
                        st.success("Comment added.")
                        st.rerun()
                task_comments = comments_df[comments_df["task_id"] == int(comment_task)] if not comments_df.empty else pd.DataFrame()
                if task_comments.empty:
                    st.info("No comments for this task yet.")
                else:
                    st.dataframe(task_comments, use_container_width=True)

        with task_tabs[3]:
            if tasks_df.empty:
                st.info("No assigned tasks available.")
            else:
                my_queue = tasks_df[tasks_df["assigned_to"].astype(str).str.lower() == display_name.lower()]
                if my_queue.empty:
                    st.info("No tasks currently assigned to you.")
                else:
                    st.dataframe(my_queue, use_container_width=True)
    elif page == "Admin Tools":
        st.subheader("Admin Tools")
        admin_tabs = st.tabs(["Users", "Reset Password", "Assign Task", "Vendor Follow-up", "Admin Snapshot"])

        with admin_tabs[0]:
            users_df = get_all_users(conn)
            if users_df.empty:
                st.info("No user records available.")
            else:
                view = users_df.copy()
                rename_map = {"display_name": "Display Name", "password_hash": "Password Hash", "must_change_password": "Must Change Password"}
                view = view.rename(columns=rename_map)
                safe_cols = [c for c in ["id", "username", "Display Name", "role", "active", "Must Change Password"] if c in view.columns]
                st.dataframe(view[safe_cols], use_container_width=True)

        with admin_tabs[1]:
            users_df = get_all_users(conn)
            user_options = users_df["username"].dropna().astype(str).tolist() if not users_df.empty and "username" in users_df.columns else []
            reset_user = st.selectbox("Select user", user_options, key="admin_reset_user") if user_options else None
            reset_password = st.text_input("New password", type="password", key="admin_reset_password")
            force_change = st.checkbox("Require password change on next login", value=False, key="admin_force_change")
            if st.button("Update Password", key="admin_update_password"):
                if not reset_user:
                    st.error("No user available for reset.")
                elif len(reset_password) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    set_user_password(conn, reset_user, reset_password, require_change=1 if force_change else 0)
                    st.success(f"Password updated for {reset_user}.")

        with admin_tabs[2]:
            with st.form("admin_create_task_form"):
                task_title = st.text_input("Task title")
                task_desc = st.text_area("Task description")
                task_assignee = st.selectbox("Assign to", ["Satish", "Priyanshu", "Amit", "Ranjan", "Manish"], key="admin_task_assign_to")
                task_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"], index=1, key="admin_task_priority")
                task_due = st.date_input("Due date", key="admin_task_due")
                submitted_task = st.form_submit_button("Create Task")
                if submitted_task:
                    if not str(task_title).strip():
                        st.error("Task title is required.")
                    else:
                        create_task(conn, {
                            "title": task_title.strip(),
                            "description": task_desc.strip(),
                            "assigned_by": display_name,
                            "assigned_to": task_assignee,
                            "priority": task_priority,
                            "status": "Open",
                            "progress": 0,
                            "due_date": str(task_due),
                            "vendor_flag": 0,
                            "vendor_status": None,
                            "vendor_remark": None,
                            "reminder_date": str(task_due),
                        })
                        st.success("Task created successfully.")
            tasks_df = load_tasks_df(conn)
            if not tasks_df.empty:
                st.dataframe(tasks_df, use_container_width=True)

        with admin_tabs[3]:
            ticket_options = df_tickets[["id", "System Ticket ID", "complaint"]].copy() if not df_tickets.empty else pd.DataFrame(columns=["id", "System Ticket ID", "complaint"])
            if ticket_options.empty:
                st.info("No tickets available for vendor follow-up.")
            else:
                ticket_labels = {f"{row['System Ticket ID']} - {str(row['complaint'])[:60]}": int(row['id']) for _, row in ticket_options.iterrows()}
                with st.form("vendor_followup_form"):
                    chosen_label = st.selectbox("Ticket", list(ticket_labels.keys()), key="vendor_ticket")
                    vendor_name = st.text_input("Vendor name")
                    vendor_status = st.selectbox("Follow-up status", ["Pending from Vendor", "Follow-up Done", "Resolved by Vendor", "Escalated"], key="vendor_status")
                    vendor_remark = st.text_area("Vendor remark")
                    vendor_due = st.date_input("Follow-up due date", key="vendor_due")
                    submitted_vendor = st.form_submit_button("Add Follow-up")
                    if submitted_vendor:
                        if not str(vendor_name).strip():
                            st.error("Vendor name is required.")
                        else:
                            add_vendor_followup(conn, ticket_labels[chosen_label], vendor_name.strip(), vendor_status, vendor_remark.strip(), str(vendor_due))
                            st.success("Vendor follow-up saved.")
                vendor_df = load_vendor_followups_df(conn)
                if not vendor_df.empty:
                    st.dataframe(vendor_df, use_container_width=True)

        with admin_tabs[4]:
            users_df = get_all_users(conn)
            tasks_df = load_tasks_df(conn)
            vendor_df = load_vendor_followups_df(conn)
            c1, c2, c3 = st.columns(3)
            c1.metric("Users", len(users_df))
            c2.metric("Open Tasks", int((tasks_df["status"] != "Closed").sum()) if not tasks_df.empty and "status" in tasks_df.columns else 0)
            c3.metric("Vendor Follow-ups", len(vendor_df))
    elif page == "AVP Dashboard":
        st.subheader("AVP Strategic Overview")
        metrics = build_ticket_exec_metrics(df_ticket_filtered)
        sri = build_system_reliability_index(df_ticket_filtered)
        dept_load = build_department_load_distribution(df_ticket_filtered)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("System Reliability Index %", sri)
        c2.metric("Pending", metrics.get("pending", 0))
        c3.metric("Overdue", metrics.get("overdue", 0))
        c4.metric("Resolution %", metrics.get("resolution_rate", 0.0))

        avp_tabs = st.tabs(["Department Load", "Efficiency Matrix", "Recurring Failures", "Trend Snapshot"])
        with avp_tabs[0]:
            if dept_load.empty:
                st.info("No departmental load data available.")
            else:
                st.dataframe(dept_load, use_container_width=True)
        with avp_tabs[1]:
            st.altair_chart(build_technician_efficiency_matrix(df_ticket_filtered).properties(height=380), use_container_width=True)
        with avp_tabs[2]:
            st.dataframe(build_top_recurring_failures(df_ticket_filtered), use_container_width=True)
        with avp_tabs[3]:
            st.dataframe(build_ticket_trend(df_ticket_filtered, freq="Weekly"), use_container_width=True)
            st.dataframe(build_ticket_trend(df_ticket_filtered, freq="Monthly"), use_container_width=True)
    elif page == "Executive Command Center":
        st.subheader("IT Operations War Room")
        st.caption("A single-screen executive view with KPI ribbon, operational risk, and management insight blocks.")
        task_df = load_tasks_df(conn)
        vendor_df = load_vendor_followups_df(conn)
        status_df = load_user_status_df(conn)
        exec_metrics = build_executive_command_metrics(df_ticket_filtered, task_df, vendor_df, status_df, df_nas_filtered)
        ribbon = st.columns(6)
        ribbon_items = [
            ("Open Tickets", exec_metrics.get("Total Open Tickets", 0), "Current backlog", "🎫", "warning"),
            ("SLA Breaches", exec_metrics.get("Critical SLA Breaches", 0), "Attention needed", "🚨", "danger"),
            ("Vendor Open Cases", exec_metrics.get("Open Vendor Cases", 0), "Pending with vendors", "🏭", "warning"),
            ("Tasks Due", exec_metrics.get("Overdue Tasks", 0), "Overdue tasks", "📌", "warning"),
            ("NAS Health", exec_metrics.get("NAS Health Score", 0), "Infrastructure health", "🖥", "success"),
            ("Resolution %", exec_metrics.get("Resolution Rate %", 0), "Closure efficiency", "✅", "success"),
        ]
        for col, item in zip(ribbon, ribbon_items):
            with col:
                render_kpi_card(*item)
        aging_pack = build_ticket_aging_analysis(df_ticket_filtered)
        dept_health = build_department_health(df_ticket_filtered)
        insights_df = build_management_insights(df_ticket_filtered, df_nas_filtered, vendor_df)
        mom_df = build_month_over_month_comparison(df_ticket_filtered)
        mid1, mid2 = st.columns([1.1, 1])
        with mid1:
            st.markdown("### Ticket Aging")
            aging_df = aging_pack.get('aging_table', pd.DataFrame())
            if not aging_df.empty:
                st.altair_chart(alt.Chart(aging_df).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(x='aging_bucket:N', y='Tickets:Q', color='aging_bucket:N'), use_container_width=True)
            st.caption(f"Average pending age: {aging_pack.get('avg_pending_age', 0)} days")
        with mid2:
            st.markdown("### Department Risk")
            if dept_health is not None and not dept_health.empty:
                st.altair_chart(alt.Chart(dept_health.head(8)).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(x='department:N', y='Risk_Score:Q', color='Department_Health:N'), use_container_width=True)
            else:
                st.info("No department risk data available.")
        st.markdown("### Management Insights")
        render_insight_cards(insights_df, columns_count=3)
        st.markdown("### Month-over-Month")
        if mom_df is not None and not mom_df.empty:
            mcols = st.columns(len(mom_df))
            for col, (_, row) in zip(mcols, mom_df.iterrows()):
                with col:
                    tone = 'success' if 'Increase' in str(row['Direction']) and row['Metric'] in ['Resolution Rate', 'SLA %'] else ('danger' if 'Decrease' in str(row['Direction']) and row['Metric'] in ['Resolution Rate', 'SLA %'] else 'primary')
                    render_kpi_card(str(row['Metric']), row['Current_Month'], f"Prev: {row['Previous_Month']}", '📈', str(row['Direction']), tone)
        with st.expander("Detailed executive tables", expanded=False):
            if aging_pack.get('most_aged', pd.DataFrame()) is not None and not aging_pack.get('most_aged', pd.DataFrame()).empty:
                st.markdown("#### Most aged tickets")
                st.dataframe(aging_pack.get('most_aged', pd.DataFrame()), use_container_width=True)
            if dept_health is not None and not dept_health.empty:
                st.markdown("#### Department risk table")
                st.dataframe(dept_health, use_container_width=True)
            if mom_df is not None and not mom_df.empty:
                st.markdown("#### Month-over-month table")
                st.dataframe(mom_df, use_container_width=True)

    elif page == "Vendor Dashboard":
        st.subheader("Vendor Performance Analytics")
        vendor_perf = build_vendor_performance(load_vendor_followups_df(conn))
        table = vendor_perf.get('table', pd.DataFrame())
        heat = vendor_perf.get('heatmap', pd.DataFrame())
        if table.empty:
            st.info("No vendor cases available.")
        else:
            st.dataframe(table, use_container_width=True)
            st.altair_chart(alt.Chart(table).mark_bar().encode(x='vendor_name:N', y='SLA_Compliance:Q', color='vendor_name:N'), use_container_width=True)
        if heat is not None and not heat.empty:
            st.altair_chart(alt.Chart(heat).mark_rect().encode(x='vendor_name:N', y='followup_status:N', color='Cases:Q', tooltip=['vendor_name','followup_status','Cases']), use_container_width=True)

    elif page == "Department Health":
        st.subheader("Department Health Dashboard")
        dept = build_department_health(df_ticket_filtered)
        if dept.empty:
            st.info("No department analytics available.")
        else:
            st.dataframe(dept, use_container_width=True)
            st.altair_chart(alt.Chart(dept).mark_bar().encode(x='department:N', y='Load_%:Q', color='Department_Health:N'), use_container_width=True)

    elif page == "Asset Health":
        st.subheader("Asset Health Module")
        assets_df = load_assets_df(conn)
        with st.expander("Register new asset"):
            c1, c2, c3, c4 = st.columns(4)
            asset_id = c1.text_input('Asset ID', key='asset_id_new')
            asset_type = c2.selectbox('Asset Type', ['Laptop','Desktop','Printer','Camera','Switch','Firewall','Server','UPS'], key='asset_type_new')
            asset_loc = c3.text_input('Location', key='asset_loc_new')
            asset_vendor = c4.text_input('Vendor', key='asset_vendor_new')
            c5, c6, c7 = st.columns(3)
            purchase_date = c5.date_input('Purchase Date', key='asset_purchase_date')
            warranty_end = c6.date_input('Warranty End', key='asset_warranty_end')
            status = c7.selectbox('Status', ['Active','Under Repair','Retired'], key='asset_status_new')
            if st.button('Add Asset', key='asset_add_btn'):
                create_asset(conn, {'asset_id': asset_id, 'asset_type': asset_type, 'location': asset_loc, 'vendor': asset_vendor, 'purchase_date': str(purchase_date), 'warranty_end': str(warranty_end), 'status': status})
                st.success('Asset added.')
                st.rerun()
        asset_pack = build_asset_health(assets_df, df_ticket_filtered)
        st.dataframe(asset_pack.get('registry', pd.DataFrame()), use_container_width=True)
        st.markdown('### Assets Near Warranty Expiry')
        st.dataframe(asset_pack.get('near_expiry', pd.DataFrame()), use_container_width=True)
        st.markdown('### Replacement Recommendations')
        st.dataframe(asset_pack.get('recommendations', pd.DataFrame()), use_container_width=True)

    elif page == "Team Chat":
        st.markdown('''<div class="panel"><div class="panel-title">Team Chat</div><div class="panel-sub">Unread badges, presence indicators, mentions, and ticket-linked collaboration stay functionally unchanged while using a cleaner shell.</div></div>''', unsafe_allow_html=True)
        st.subheader("Team Chat")
        status_df = load_user_status_df(conn)
        threads_df = load_chat_threads_df(conn)
        user_key = user.get("username") or display_name.lower()
        unread_map = build_thread_unread_map(conn, user.get("username"))
        left, right = st.columns([1, 2])
        with left:
            chosen_status = st.selectbox("Your status", ["Available", "Busy", "In Meeting", "Offline"], key="team_chat_status")
            if st.button("Save Status", key="team_chat_save_status"):
                set_user_status(conn, user_key, display_name, chosen_status)
                st.success("Status updated.")
                st.rerun()
            st.markdown("#### Team presence")
            st.dataframe(status_df, use_container_width=True)
            st.markdown("#### Threads")
            if threads_df.empty:
                default_thread = create_chat_thread(conn, "General Team Chat", display_name)
                post_chat_message(conn, default_thread, display_name, "General thread created.")
                st.rerun()
            thread_labels = []
            thread_map = {}
            for _, row in threads_df.iterrows():
                tid = int(row['id'])
                unread = unread_map.get(tid, 0)
                label = f"{row['title']} (#{tid})"
                if unread > 0:
                    label += f" • unread {unread}"
                thread_labels.append(label)
                thread_map[label] = tid
            selected_thread_label = st.selectbox("Select thread", thread_labels, key="team_chat_thread")
            selected_thread_id = thread_map[selected_thread_label]
            new_thread_title = st.text_input("New thread title", key="team_chat_new_thread")
            if st.button("Create Thread", key="team_chat_create_thread"):
                if str(new_thread_title).strip():
                    create_chat_thread(conn, new_thread_title.strip(), display_name)
                    st.success("Thread created.")
                    st.rerun()
        with right:
            ticket_options = ["No linked ticket"]
            if not df_ticket_filtered.empty and 'id' in df_ticket_filtered.columns:
                ticket_options += [f"{int(r['id'])} | {r.get('System Ticket ID', '')} | {str(r.get('complaint', ''))[:50]}" for _, r in df_ticket_filtered[['id', 'System Ticket ID', 'complaint']].drop_duplicates().iterrows()]
            linked_ticket = st.selectbox("Link this reply to ticket", ticket_options, key="chat_link_ticket")
            messages_df = load_chat_messages_df(conn, selected_thread_id)
            if messages_df.empty:
                st.info("No messages in this thread yet.")
            else:
                for _, row in messages_df.iterrows():
                    with st.chat_message("user" if str(row['sender']) == str(display_name) else "assistant"):
                        msg = str(row['message'])
                        words = []
                        for token in msg.split():
                            if token.startswith('@'):
                                words.append(f"**{token}**")
                            else:
                                words.append(token)
                        st.markdown(" ".join(words))
                        meta = f"{row['sender']} • {row['created_at']}"
                        if 'linked_ticket_id' in row and pd.notna(row['linked_ticket_id']):
                            meta += f" • Ticket #{int(row['linked_ticket_id'])}"
                        st.caption(meta)
            prompt = st.chat_input("Type a message or mention @user")
            if prompt:
                linked_ticket_id = None
                if linked_ticket != "No linked ticket":
                    linked_ticket_id = int(str(linked_ticket).split('|')[0].strip())
                post_chat_message(conn, selected_thread_id, display_name, prompt, linked_ticket_id=linked_ticket_id)
                st.rerun()

conn_global_for_pdf = None

# Main Application Entrypoint
if __name__ == "__main__":
    conn = get_db_connection()
    init_support_data(conn)
    seed_supabase_users_if_needed()
    bootstrap_auth_gate(conn)
    render_dashboard(conn)
