import io
import hashlib
import sqlite3
from datetime import datetime, time

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
        border: 1px solid #1f2937;
        border-radius: 16px;
        padding: 18px 22px;
        margin-bottom: 10px;
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
        margin-bottom: 0;
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

    .panel-card {
        background: rgba(15, 23, 42, 0.72);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 14px;
        color: var(--text);
        margin-bottom: 12px;
    }

    .summary-card {
        background: var(--panel-soft);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 14px;
        color: var(--text);
        margin-bottom: 12px;
    }

    .summary-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px 16px;
    }

    .sum-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--muted);
        margin-bottom: 2px;
    }

    .sum-value {
        font-size: 1rem;
        font-weight: 700;
        color: var(--text);
        word-break: break-word;
    }

    .span-2 {
        grid-column: span 2;
    }

    .status-chip {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        border: 1px solid transparent;
        white-space: nowrap;
    }

    .status-open {
        color: #fecaca;
        background: rgba(239, 68, 68, 0.12);
        border-color: rgba(239, 68, 68, 0.28);
    }

    .status-progress {
        color: #bfdbfe;
        background: rgba(59, 130, 246, 0.12);
        border-color: rgba(59, 130, 246, 0.28);
    }

    .status-hold {
        color: #fde68a;
        background: rgba(245, 158, 11, 0.12);
        border-color: rgba(245, 158, 11, 0.28);
    }

    .status-resolved {
        color: #bbf7d0;
        background: rgba(34, 197, 94, 0.12);
        border-color: rgba(34, 197, 94, 0.28);
    }

    .queue-shell {
        background: rgba(15, 23, 42, 0.72);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 14px;
        margin-top: 8px;
    }

    .table-scroll {
        width: 100%;
        overflow-x: auto;
        border: 1px solid var(--border);
        border-radius: 14px;
        background: var(--panel-soft);
    }

    .table-scroll table {
        width: 100%;
        border-collapse: collapse;
        min-width: 940px;
    }

    .table-scroll th, .table-scroll td {
        padding: 10px 12px;
        border-bottom: 1px solid rgba(39, 52, 73, 0.9);
        vertical-align: top;
        text-align: left;
        font-size: 0.88rem;
    }

    .table-scroll th {
        position: sticky;
        top: 0;
        background: #162033;
        color: #e5eefc;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        z-index: 1;
    }

    .table-scroll tr:last-child td {
        border-bottom: none;
    }

    .compact-table table {
        min-width: 760px;
    }

    .compact-table th, .compact-table td {
        padding: 8px 10px;
        font-size: 0.85rem;
    }

    .danger-box {
        background: rgba(127, 29, 29, 0.22);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 14px;
        padding: 14px;
    }

    .danger-box h4 {
        margin: 0 0 8px 0;
        color: #fecaca;
    }

    .mini-note {
        color: var(--muted);
        font-size: 0.84rem;
        margin-bottom: 0.5rem;
    }

    [data-testid="stMetric"] {
        background: #0f172a;
        border: 1px solid #1e293b;
        padding: 12px;
        border-radius: 14px;
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background: #111827;
        border-radius: 8px 8px 0 0;
        color: #cbd5e1;
        padding: 10px 14px;
    }

    .stTabs [aria-selected="true"] {
        background: #ef4444 !important;
        color: white !important;
    }

    div[data-testid="stForm"] {
        background: rgba(15, 23, 42, 0.55);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 0.9rem;
    }

    div.stButton > button:first-child,
    div[data-testid="stDownloadButton"] > button:first-child,
    div[data-testid="baseButton-secondary"] > button:first-child {
        background-color: #ef4444;
        color: white;
        border: none;
        border-radius: 10px;
    }

    @media (max-width: 900px) {
        .summary-grid {
            grid-template-columns: 1fr;
        }
        .span-2 {
            grid-column: span 1;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 2. SQLITE & SUPABASE INITIALIZATION
# ==========================================
def get_db_connection():
    conn = sqlite3.connect('it_ops.db', check_same_thread=False)
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
    ('amit', 'Amit', 'IT Manager'),
    ('satish', 'Satish', 'IT AM'),
    ('ranjan', 'Ranjan', 'Sr. Executive'),
    ('priyanshu', 'Priyanshu', 'IT Executive'),
    ('manish', 'Manish', 'IT Executive'),
    ('satender', 'Mr. Satender Vashisht', 'AVP'),
]

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def ensure_support_tables(conn):
    conn.execute(USERS_TABLE_SQL)
    conn.execute(TASKS_TABLE_SQL)
    conn.execute(COMMENTS_TABLE_SQL)
    conn.execute(NOTIFICATIONS_TABLE_SQL)
    conn.execute(VENDOR_TABLE_SQL)
    conn.commit()

def seed_default_users(conn):
    cur = conn.cursor()
    for username, display_name, role in DEFAULT_USERS:
        cur.execute('SELECT id FROM users WHERE username=?', (username,))
        if cur.fetchone() is None:
            cur.execute(
                'INSERT INTO users (username, display_name, role, password_hash, active, must_change_password) VALUES (?, ?, ?, ?, 1, 1)',
                (username, display_name, role, None)
            )
    conn.commit()

def init_support_data(conn):
    ensure_support_tables(conn)
    seed_default_users(conn)

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

# ==========================================
# 3. GLOBAL MAPS & PRESETS
# ==========================================
TECH_MAP = {
    "Satish": "TECH-01",
    "Priyanshu": "TECH-02",
    "Amit": "TECH-03",
    "Ranjan": "TECH-04",
    "Manish": "TECH-05",
}

OFFICIAL_LOCATIONS = [
    "Sector - 136 Vega",
    "Knitpro 28-29",
    "Sector - 155 Vega",
    "Knitpro - Jaipur",
    "Knitpro 42",
    "Knitpro 72-73",
    "Knitpro 75",
    "Bharat Composite Sector 80",
    "Vega Sector 80",
]

STATUS_OPTIONS = ["Open", "In Progress", "On Hold - User Busy", "Resolved"]
SERVER_NAMES = ["HRI", "Vega", "Sery", "Rise"]
SERVER_SHEET_MAP = {
    "HRI": "Sheet 1",
    "Vega": "Sheet 2",
    "Sery": "Sheet 3",
    "Rise": "Sheet 4",
}

AI_SUGGESTIONS = {
    "CCTV/Camera": {
        "title_en": "📷 AI Video Infrastructure Diagnostics",
        "title_hi": "📷 एआई वीडियो इन्फ्रास्ट्रक्चर डायग्नोस्टिक्स",
        "English": [
            "Check whether the camera POE switch port light is blinking.",
            "Ping the camera IP address through CMD to confirm network continuity.",
            "If NVR shows no video, restart the camera channel or re-login the device.",
        ],
        "Hindi": [
            "जांचें कि कैमरा POE स्विच पोर्ट की लाइट ब्लिंक कर रही है या नहीं।",
            "नेटवर्क कनेक्टिविटी जांचने के लिए कैमरा IP एड्रेस को पिंग करें।",
            "यदि NVR 'No Video' दिखाए, तो कैमरा चैनल रीस्टार्ट या री-लॉगिन करें।",
        ],
    },
    "Laptop/Hardware": {
        "title_en": "💻 AI Endpoint Hardware Diagnostics",
        "title_hi": "💻 एआई एंडपॉइंट हार्डवेयर डायग्नोस्टिक्स",
        "English": [
            "Perform a hard reset by disconnecting power and holding the power button for 30 seconds.",
            "Connect to an external display to isolate panel versus motherboard issues.",
            "Check Device Manager and reinstall chipset or hardware drivers if needed.",
        ],
        "Hindi": [
            "पावर डिस्कनेक्ट करके 30 सेकंड तक पावर बटन दबाकर हार्ड रीसेट करें।",
            "LCD और मदरबोर्ड समस्या अलग करने के लिए बाहरी मॉनिटर लगाएं।",
            "Device Manager जांचें और आवश्यक होने पर ड्राइवर पुनः इंस्टॉल करें।",
        ],
    },
    "Email/Outlook": {
        "title_en": "📧 AI Communication Layer Diagnostics",
        "title_hi": "📧 एआई कम्यूनिकेशन लेयर डायग्नोस्टिक्स",
        "English": [
            "Run outlook.exe /safe to isolate add-in conflicts.",
            "Check PST or OST file size and compact it if very large.",
            "Clear Credential Manager entries if password prompts repeat.",
        ],
        "Hindi": [
            "Add-in conflict जांचने के लिए outlook.exe /safe चलाएं।",
            "PST या OST फ़ाइल का आकार जांचें और जरूरत हो तो compact करें।",
            "बार-बार पासवर्ड आने पर Credential Manager entries साफ करें।",
        ],
    },
    "Printer": {
        "title_en": "🖨️ AI Print Management Diagnostics",
        "title_hi": "🖨️ एआई प्रिंट मैनेजमेंट डायग्नोस्टिक्स",
        "English": [
            "Verify Printer Properties, configured port, and SNMP setting.",
            "Restart Print Spooler and clear stuck jobs in the PRINTERS folder.",
            "Inspect cartridge, rollers, and scanner glass for quality issues.",
        ],
        "Hindi": [
            "Printer Properties, port configuration और SNMP setting जांचें।",
            "Print Spooler restart करें और stuck jobs साफ करें।",
            "कार्ट्रिज, रोलर्स और स्कैनर ग्लास जांचें।",
        ],
    },
    "SAP": {
        "title_en": "🏢 AI Enterprise ERP Diagnostics",
        "title_hi": "🏢 एआई एंटरप्राइज ईआरपी डायग्नोस्टिक्स",
        "English": [
            "Verify SAP logon configuration and network reachability.",
            "Check for locked or hung sessions through SAP tools.",
            "Repair SAP GUI or clear cache if the client is unstable.",
        ],
        "Hindi": [
            "SAP logon configuration और network connectivity जांचें।",
            "Locked या hung sessions जांचें।",
            "Client unstable होने पर SAP GUI repair या cache clear करें।",
        ],
    },
    "Network": {
        "title_en": "🌐 AI Network Routing Diagnostics",
        "title_hi": "🌐 एआई नेटवर्क राउटिंग डायग्नोस्टिक्स",
        "English": [
            "Reset Winsock and inspect the adapter driver for frequent drops.",
            "Release and renew IP configuration if conflict is suspected.",
            "Check the SSID and frequency band being used by the device.",
        ],
        "Hindi": [
            "बार-बार डिस्कनेक्ट होने पर Winsock reset और adapter driver जांचें।",
            "IP conflict शक होने पर release और renew करें।",
            "SSID और frequency band की पुष्टि करें।",
        ],
    },
    "Server/UPS": {
        "title_en": "🖥️ Server & Power Infrastructure Diagnostics",
        "title_hi": "🖥️ सर्वर और पावर इन्फ्रास्ट्रक्चर डायग्नोस्टिक्स",
        "English": [
            "Check UPS load and input power if alarms are active.",
            "Verify rack airflow and server room temperature.",
            "Review DNS and authentication dependencies if logins fail.",
        ],
        "Hindi": [
            "अलार्म आने पर UPS load और input power जांचें।",
            "Rack airflow और server room temperature जांचें।",
            "Login fail होने पर DNS और authentication dependencies देखें।",
        ],
    },
}

# Initialize Fallback / In-Memory Mock Structures
if "local_tickets" not in st.session_state:
    st.session_state.local_tickets = pd.DataFrame(
        [
            {
                "id": 1,
                "date": "2026-07-01",
                "user_name": "Amit Sharma",
                "department": "Production",
                "complaint": "CCTV camera in main corridor is flickering",
                "location": "Sector - 136 Vega",
                "attended_by": "Satish",
                "status": "In Progress",
                "category": "CCTV/Camera",
                "start_time": "2026-07-01 10:15:00",
                "close_time": None,
                "resolution_time": 0,
                "remarks": "POE check in progress",
            },
            {
                "id": 2,
                "date": "2026-07-03",
                "user_name": "Sunita Rao",
                "department": "Finance",
                "complaint": "Desktop showing blue screen after update",
                "location": "Knitpro 28-29",
                "attended_by": "Priyanshu",
                "status": "Open",
                "category": "Laptop/Hardware",
                "start_time": None,
                "close_time": None,
                "resolution_time": 0,
                "remarks": "",
            },
            {
                "id": 3,
                "date": "2026-07-05",
                "user_name": "Rajesh Kumar",
                "department": "HR",
                "complaint": "Office printer offline and queue is stuck",
                "location": "Sector - 155 Vega",
                "attended_by": "Amit",
                "status": "Resolved",
                "category": "Printer",
                "start_time": "2026-07-05 10:00:00",
                "close_time": "2026-07-05 10:35:00",
                "resolution_time": 35,
                "remarks": "Spooler restarted and queue flushed",
            },
        ]
    )

if "local_nas" not in st.session_state:
    st.session_state.local_nas = pd.DataFrame(
        [
            {"id": 1, "date": "2026-07-11", "server_name": "HRI", "status": "Success", "storage_used": 43.3975, "remarks": "Daily backup completed."},
            {"id": 2, "date": "2026-07-12", "server_name": "HRI", "status": "Success", "storage_used": 43.3985, "remarks": "Daily backup completed."},
            {"id": 3, "date": "2026-07-13", "server_name": "HRI", "status": "Failed", "storage_used": 43.3985, "remarks": "Handshake timeout."},
            {"id": 4, "date": "2026-07-13", "server_name": "Vega", "status": "Success", "storage_used": 236.1529, "remarks": "Backup completed."},
            {"id": 5, "date": "2026-07-15", "server_name": "Sery", "status": "Success", "storage_used": 4.2406, "remarks": "Incremental snapshot success."},
            {"id": 6, "date": "2026-07-15", "server_name": "Rise", "status": "Success", "storage_used": 6.4914, "remarks": "Replication completed."},
        ]
    )

# ==========================================
# 4. HELPER UTILITIES & DATA NORMALIZERS
# ==========================================
def format_ticket_number(ticket_id, location_str):
    try:
        clean_id = int(float(ticket_id))
        loc = str(location_str).lower() if pd.notna(location_str) else ""
        if "vega" in loc or "136" in loc or "155" in loc:
            prefix = "VEGA"
        elif "knitpro" in loc or "jaipur" in loc:
            prefix = "KP"
        else:
            prefix = "IT"
        return f"{prefix}-2026-{clean_id:04d}"
    except Exception:
        return f"IT-2026-{ticket_id}"

def auto_categorize(complaint):
    text = str(complaint).lower()
    if any(k in text for k in ["cctv", "camera", "nvr"]):
        return "CCTV/Camera"
    if any(k in text for k in ["laptop", "desktop", "keyboard", "touchpad", "battery", "screen", "hardware", "monitor"]):
        return "Laptop/Hardware"
    if any(k in text for k in ["outlook", "email", "mail", "pst", "ost"]):
        return "Email/Outlook"
    if any(k in text for k in ["printer", "scanner", "cartridge", "print"]):
        return "Printer"
    if any(k in text for k in ["sap", "erp"]):
        return "SAP"
    if any(k in text for k in ["network", "wifi", "internet", "vpn", "ping", "ip", "router", "switch", "lan"]):
        return "Network"
    if any(k in text for k in ["server", "ups", "rack", "dns", "domain", "backup"]):
        return "Server/UPS"
    return "Other"

def normalize_ticket_df(df):
    expected = [
        "id", "date", "user_name", "department", "complaint", "location",
        "attended_by", "status", "category", "start_time", "close_time",
        "resolution_time", "remarks",
    ]
    if df is None or df.empty:
        return pd.DataFrame(columns=expected)
    out = df.copy()
    for col in expected:
        if col not in out.columns:
            out[col] = None
    out["id"] = pd.to_numeric(out["id"], errors="coerce").fillna(0).astype(int)
    out["resolution_time"] = pd.to_numeric(out["resolution_time"], errors="coerce").fillna(0).astype(int)
    out["remarks"] = out["remarks"].fillna("").astype(str)
    out["status"] = out["status"].fillna("").astype(str)
    out["category"] = out["category"].fillna("").astype(str)
    out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    return out[expected]

def normalize_nas_df(df):
    expected = ["id", "date", "server_name", "status", "storage_used", "remarks"]
    if df is None or df.empty:
        return pd.DataFrame(columns=expected)
    out = df.copy()
    for col in expected:
        if col not in out.columns:
            out[col] = None
    out["id"] = pd.to_numeric(out["id"], errors="coerce").fillna(0).astype(int)
    out["storage_used"] = pd.to_numeric(out["storage_used"], errors="coerce").fillna(0.0)
    out["remarks"] = out["remarks"].fillna("").astype(str)
    out["server_name"] = out["server_name"].fillna("").astype(str)
    out["status"] = out["status"].fillna("").astype(str).str.strip().map(normalize_nas_status)
    out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    return out[expected]

def get_next_ticket_id(df):
    if df.empty or "id" not in df.columns:
        return 1
    return int(pd.to_numeric(df["id"], errors="coerce").fillna(0).max()) + 1

def get_next_nas_id(df):
    if df.empty or "id" not in df.columns:
        return 1
    return int(pd.to_numeric(df["id"], errors="coerce").fillna(0).max()) + 1

# ==========================================
# 5. DATA FETCHING & PERSISTENCE
# ==========================================
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
            response = supabase_client.table("nas_backups").select("*").execute()
            return normalize_nas_df(pd.DataFrame(response.data) if response.data else pd.DataFrame())
        except Exception:
            pass
    return normalize_nas_df(st.session_state.local_nas)

def save_ticket(new_row):
    if db_connected:
        response = supabase_client.table("tickets").insert(new_row).execute()
        if response.data and "id" in response.data[0]:
            return int(response.data[0]["id"])
        return None
    current = st.session_state.local_tickets.copy()
    row = dict(new_row)
    row["id"] = get_next_ticket_id(current)
    st.session_state.local_tickets = pd.concat([current, pd.DataFrame([row])], ignore_index=True)
    return int(row["id"])

def update_ticket(ticket_id, payload):
    if db_connected:
        supabase_client.table("tickets").update(payload).eq("id", int(ticket_id)).execute()
        return
    idx = st.session_state.local_tickets[st.session_state.local_tickets["id"] == int(ticket_id)].index
    for key, value in payload.items():
        st.session_state.local_tickets.loc[idx, key] = value

def delete_ticket(ticket_id):
    if db_connected:
        supabase_client.table("tickets").delete().eq("id", int(ticket_id)).execute()
        return
    st.session_state.local_tickets = st.session_state.local_tickets[
        st.session_state.local_tickets["id"] != int(ticket_id)
    ].reset_index(drop=True)

def save_nas_log(new_row):
    if db_connected:
        response = supabase_client.table("nas_backups").insert(new_row).execute()
        if response.data and "id" in response.data[0]:
            return int(response.data[0]["id"])
        return None
    current = st.session_state.local_nas.copy()
    row = dict(new_row)
    row["id"] = get_next_nas_id(current)
    st.session_state.local_nas = pd.concat([current, pd.DataFrame([row])], ignore_index=True)
    return int(row["id"])

def delete_nas_log(log_id):
    if db_connected:
        supabase_client.table("nas_backups").delete().eq("id", int(log_id)).execute()
        return
    st.session_state.local_nas = st.session_state.local_nas[
        st.session_state.local_nas["id"] != int(log_id)
    ].reset_index(drop=True)

# ==========================================
# 6. CHARTING, TABLE RENDERERS & ALTAIR
# ==========================================
def status_badge_html(status):
    s = str(status).strip().lower()
    if s == "resolved":
        return '<span class="status-chip status-resolved">Resolved</span>'
    if s == "in progress":
        return '<span class="status-chip status-progress">In Progress</span>'
    if s == "on hold - user busy":
        return '<span class="status-chip status-hold">On Hold</span>'
    return '<span class="status-chip status-open">Open</span>'

def prepare_ticket_view(df):
    view = df.copy()
    if not view.empty:
        view["System Ticket ID"] = view.apply(lambda r: format_ticket_number(r["id"], r["location"]), axis=1)
        view["date_parsed"] = pd.to_datetime(view["date"], errors="coerce")
    return view

def filtered_tickets(df, site_filter, status_filter, tech_filter):
    out = df.copy()
    if out.empty:
        return out
    if site_filter != "All":
        out = out[out["location"] == site_filter]
    if status_filter != "All":
        out = out[out["status"] == status_filter]
    if tech_filter != "All":
        out = out[out["attended_by"] == tech_filter]
    return out

def filtered_nas(df, server_filter):
    out = df.copy()
    if out.empty:
        return out
    if server_filter != "All":
        out = out[out["server_name"] == server_filter]
    return out

def normalize_nas_status(value):
    s = str(value).strip().lower()
    if s in {"success", "ok", "passed", "pass", "complete", "completed"}:
        return "Success"
    if s in {"failed", "fail", "error", "warning", "warn", "partial", "warning / partial"}:
        return "Failed"
    return "Failed"

def render_nas_status(status):
    return '<span class="status-chip status-resolved">Success</span>' if str(status).strip() == "Success" else '<span class="status-chip status-open">Failed</span>'

def separate_nas_series(df):
    if df.empty:
        return df
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    return out.dropna(subset=["date"])

def render_status_table(df, columns, compact=False, nas_mode=False):
    if df.empty:
        st.info("No records found.")
        return
    show_df = df.copy()
    if "status" in show_df.columns:
        if nas_mode:
            show_df["status"] = show_df["status"].apply(render_nas_status)
        else:
            show_df["status"] = show_df["status"].apply(status_badge_html)
    styled = show_df[columns].to_html(escape=False, index=False)
    css_class = "table-scroll compact-table" if compact else "table-scroll"
    st.markdown(f"<div class='{css_class}'>{styled}</div>", unsafe_allow_html=True)

def build_bar_chart(df, x_col, y_col, color="#ef4444", title=""):
    return (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X(x_col, sort="-y", title=None),
            y=alt.Y(y_col, title=None),
            tooltip=list(df.columns),
            color=alt.value(color),
        )
        .properties(height=300, title=title)
    )

def build_line_chart(df, x_col, y_col, color="#3b82f6", title=""):
    return (
        alt.Chart(df)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X(x_col, title=None),
            y=alt.Y(y_col, title=None),
            tooltip=list(df.columns),
            color=alt.value(color),
        )
        .properties(height=300, title=title)
    )

# ==========================================
# 7. NAS DELTA COMPUTATION & ADVANCED REPORTS
# ==========================================
def compute_nas_changes(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=['id', 'date', 'server_name', 'status', 'storage_used', 'delta_gb', 'delta_pct', 'change_label', 'change_type', 'remarks'])
    
    out = normalize_nas_df(df).copy()
    out['date'] = pd.to_datetime(out['date'], errors='coerce')
    out = out.dropna(subset=['date']).sort_values(['server_name', 'date'])
    
    out['delta_gb'] = out.groupby('server_name')['storage_used'].diff().fillna(0.0)
    prev = out.groupby('server_name')['storage_used'].shift(1)
    
    out['delta_pct'] = ((out['storage_used'] - prev) / prev.replace(0, pd.NA) * 100).fillna(0.0)
    out['change_label'] = out['delta_gb'].apply(lambda x: f"+{x:.4f} GB" if x > 0 else f"{x:.4f} GB" if x < 0 else '0.0000 GB')
    out['change_type'] = out['delta_gb'].apply(lambda x: 'Increment' if x > 0 else 'Decrement' if x < 0 else 'No Change')
    
    return out

def build_nas_reports(df):
    if df is None or df.empty:
        empty = pd.DataFrame(columns=['server_name', 'date', 'storage_used', 'delta_gb', 'delta_pct', 'change_type'])
        return empty, empty, empty
    
    d = compute_nas_changes(df).copy()
    d['date'] = pd.to_datetime(d['date'], errors='coerce')
    d = d.dropna(subset=['date'])
    d['month'] = d['date'].dt.strftime('%Y-%m')
    
    cols = ['id', 'date', 'server_name', 'status', 'storage_used', 'delta_gb', 'delta_pct', 'change_type', 'remarks']
    master = d[[c for c in cols if c in d.columns]].copy()
    
    monthly = d.groupby(['month', 'server_name'], as_index=False).agg(
        logs=('server_name', 'size'),
        avg_storage=('storage_used', 'mean'),
        min_storage=('storage_used', 'min'),
        max_storage=('storage_used', 'max'),
        total_increment=('delta_gb', lambda s: s[s > 0].sum()),
        total_decrement=('delta_gb', lambda s: abs(s[s < 0].sum())),
        failures=('status', lambda s: (s == 'Failed').sum())
    )
    
    serverwise = d.groupby('server_name', as_index=False).agg(
        logs=('server_name', 'size'),
        latest_date=('date', 'max'),
        latest_storage=('storage_used', 'last'),
        prev_storage=('storage_used', 'first'),
        total_increment=('delta_gb', lambda s: s[s > 0].sum()),
        total_decrement=('delta_gb', lambda s: abs(s[s < 0].sum())),
        failures=('status', lambda s: (s == 'Failed').sum())
    )
    return master, monthly, serverwise

# ==========================================
# 8. AUTHENTICATION PROCEDURES & FORMS
# ==========================================
def get_user_by_username(conn, username):
    cur = conn.cursor()
    cur.execute('SELECT id, username, display_name, role, password_hash, active, must_change_password FROM users WHERE username=?', (username,))
    row = cur.fetchone()
    if row is None:
        return None
    keys = ['id', 'username', 'display_name', 'role', 'password_hash', 'active', 'must_change_password']
    return dict(zip(keys, row))

def set_user_password(conn, username, password):
    conn.execute('UPDATE users SET password_hash=?, must_change_password=0, active=1, updated_at=CURRENT_TIMESTAMP WHERE username=?', (hash_password(password), username))
    conn.commit()

def authenticate_user(conn, username, password):
    user = get_user_by_username(conn, username)
    if not user or not user['active']:
        return None
    if not user['password_hash']:
        return {'must_change_password': True, **user}
    if user['password_hash'] == hash_password(password):
        return {'must_change_password': bool(user['must_change_password']), **user}
    return None

def login_page(conn):
    st.title('Vega IT System Login')
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input('Username').strip().lower()
    with col2:
        password = st.text_input('Password', type='password')
    if st.button('Login'):
        user = authenticate_user(conn, username, password)
        if not user:
            st.error('Invalid credentials or inactive account')
            return None
        st.session_state['current_user'] = user
        if user['must_change_password'] or not user['password_hash']:
            st.session_state['must_set_password'] = True
        st.success(f"Welcome {user['display_name']}")
        st.rerun()
    return None

def first_password_setup(conn):
    user = st.session_state.get('current_user')
    if not user:
        return
    st.warning('Set your password to continue')
    p1 = st.text_input('New password', type='password')
    p2 = st.text_input('Confirm password', type='password')
    if st.button('Save Password'):
        if not p1 or p1 != p2:
            st.error('Passwords do not match')
            return
        set_user_password(conn, user['username'], p1)
        user = get_user_by_username(conn, user['username'])
        st.session_state['current_user'] = user
        st.session_state['must_set_password'] = False
        st.success('Password saved')
        st.rerun()

def bootstrap_auth_gate(conn):
    if 'current_user' not in st.session_state:
        st.session_state['current_user'] = None
    if 'must_set_password' not in st.session_state:
        st.session_state['must_set_password'] = False
    if st.session_state['current_user'] is None:
        login_page(conn)
        st.stop()
    if st.session_state.get('must_set_password'):
        first_password_setup(conn)
        st.stop()

def get_role_pages(role):
    if role == 'IT Manager':
        return ['Overview', 'Ticket Operations', 'NAS Monitoring', 'Reports', 'Admin Tools', 'Task Center', 'AVP Dashboard']
    if role == 'IT AM':
        return ['Overview', 'Ticket Operations', 'NAS Monitoring', 'Reports', 'Task Center']
    if role == 'AVP':
        return ['Overview', 'AVP Dashboard', 'Reports', 'Task Center']
    return ['Overview', 'Ticket Operations', 'Task Center', 'NAS Monitoring']

def render_role_sidebar():
    user = st.session_state.get('current_user', {})
    role = user.get('role', 'IT Executive')
    st.sidebar.markdown(f"**User:** {user.get('display_name', 'Guest')}")
    st.sidebar.markdown(f"**Role:** {role}")
    if st.sidebar.button('Logout'):
        st.session_state['current_user'] = None
        st.session_state['must_set_password'] = False
        st.rerun()
    return get_role_pages(role)

# ==========================================
# 9. CONSOLIDATED MAIN DASHBOARD CONTROLLER
# ==========================================
def render_dashboard():
    # Global definitions
    df_live = prepare_ticket_view(load_tickets())
    df_nas = load_nas_data()

    # Load Role Navigation Selection
    allowed_pages = render_role_sidebar()
    
    st.sidebar.markdown("## Navigation")
    page = st.sidebar.radio(
        "Go to",
        allowed_pages,
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Global Filters")
    site_filter = st.sidebar.selectbox("Site", ["All"] + OFFICIAL_LOCATIONS)
    status_filter = st.sidebar.selectbox("Ticket Status", ["All"] + STATUS_OPTIONS)
    tech_filter = st.sidebar.selectbox("Technician", ["All"] + list(TECH_MAP.keys()))
    server_filter = st.sidebar.selectbox("NAS Server", ["All"] + SERVER_NAMES)

    st.sidebar.markdown("---")
    if db_connected:
        st.sidebar.success("⚡ Supabase cloud connected")
    else:
        st.sidebar.warning("⚠️ Session sandbox active")

    df_ticket_filtered = filtered_tickets(df_live, site_filter, status_filter, tech_filter)
    df_nas = normalize_nas_df(df_nas)
    df_nas_filtered_global = filtered_nas(df_nas, server_filter)

    # Title Banner
    logo_col1, logo_col2, title_col = st.columns([1, 1, 5], vertical_alignment="center")
    with logo_col1:
        st.caption("🔺 Vega")
    with logo_col2:
        st.caption("🔺 KnitPro")
    with title_col:
        st.markdown(
            """
            <div class="app-banner">
                <div class="app-title">🛠️ Vega & Knitpro IT Operations Dashboard</div>
                <div class="app-subtitle">Single-window support operations, NAS monitoring, reporting, and recurring issue analysis</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ------------------ OVERVIEW PAGE ------------------
    if page == "Overview":
        st.subheader("Overview")
        if df_ticket_filtered.empty:
            st.info("No ticket data available for the selected filters.")
        else:
            total_tickets = len(df_ticket_filtered)
            resolved_tickets = len(df_ticket_filtered[df_ticket_filtered["status"] == "Resolved"])
            open_tickets = len(df_ticket_filtered[df_ticket_filtered["status"].isin(["Open", "In Progress"])])
            hold_tickets = len(df_ticket_filtered[df_ticket_filtered["status"] == "On Hold - User Busy"])
            resolved_df = df_ticket_filtered[(df_ticket_filtered["status"] == "Resolved") & (df_ticket_filtered["resolution_time"] > 0)]
            avg_res_time = int(resolved_df["resolution_time"].mean()) if not resolved_df.empty else 0
            nas_failures = int((df_nas_filtered_global["status"] == "Failed").sum()) if not df_nas_filtered_global.empty else 0

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Total Tickets", total_tickets)
            c2.metric("Open Backlog", open_tickets)
            c3.metric("Resolved", resolved_tickets)
            c4.metric("On Hold", hold_tickets)
            c5.metric("Avg Resolution", f"{avg_res_time} min")

            if nas_failures > 0:
                st.error(f"Critical NAS alerts: {nas_failures} failed backup entries in current filter.")
            else:
                st.success("No NAS failure alert in the current filtered view.")

            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                st.markdown("### Ticket Volume by Category")
                cat_df = df_ticket_filtered["category"].value_counts().reset_index()
                cat_df.columns = ["category", "count"]
                st.altair_chart(build_bar_chart(cat_df, "category:N", "count:Q", "#ef4444"), use_container_width=True)
            with chart_col2:
                st.markdown("### Ticket Volume by Location")
                loc_df = df_ticket_filtered["location"].value_counts().reset_index()
                loc_df.columns = ["location", "count"]
                st.altair_chart(build_bar_chart(loc_df, "location:N", "count:Q", "#3b82f6"), use_container_width=True)

            chart_col3, chart_col4 = st.columns(2)
            with chart_col3:
                st.markdown("### Technician Load")
                tech_df = df_ticket_filtered["attended_by"].value_counts().reset_index()
                tech_df.columns = ["attended_by", "count"]
                st.altair_chart(build_bar_chart(tech_df, "attended_by:N", "count:Q", "#22c55e"), use_container_width=True)
            with chart_col4:
                st.markdown("### NAS Storage Trend")
                if not df_nas_filtered_global.empty:
                    trend_df = separate_nas_series(df_nas_filtered_global)
                    trend_df = trend_df.sort_values("date")
                    if server_filter == "All":
                        chart = alt.Chart(trend_df).mark_line(point=True, strokeWidth=3).encode(
                            x=alt.X("date:T", title=None),
                            y=alt.Y("storage_used:Q", title=None),
                            color=alt.Color("server_name:N", title="Server"),
                            tooltip=["date:T", "server_name:N", "storage_used:Q", "status:N"],
                        ).properties(height=300)
                        st.altair_chart(chart, use_container_width=True)
                    else:
                        trend_df["date_label"] = trend_df["date"].dt.strftime("%Y-%m-%d")
                        st.altair_chart(build_line_chart(trend_df, "date_label:N", "storage_used:Q", "#f59e0b"), use_container_width=True)
                else:
                    st.info("No NAS data available.")

            st.markdown("### Recent Ticket Activity")
            recent = df_ticket_filtered.sort_values(by="id", ascending=False).head(8).copy()
            render_status_table(recent, ["System Ticket ID", "date", "user_name", "department", "location", "category", "attended_by", "status", "resolution_time"], compact=True)

    # ------------------ TICKET OPERATIONS PAGE ------------------
    elif page == "Ticket Operations":
        st.subheader("Ticket Operations")
        left_col, right_col = st.columns([1.05, 1.2], gap="large")

        with left_col:
            st.markdown("### Log New Ticket")
            st.markdown("<div class='section-note'>Use existing user details when possible. Keep complaint text short but specific.</div>", unsafe_allow_html=True)

            existing_users = sorted(df_live["user_name"].dropna().astype(str).unique().tolist()) if not df_live.empty else []
            selected_user = st.selectbox("Use existing user details", ["New User / Type Below"] + existing_users)

            default_user_name, default_dept, default_loc = "", "", OFFICIAL_LOCATIONS[0]
            if selected_user != "New User / Type Below" and not df_live.empty:
                hist = df_live[df_live["user_name"] == selected_user].sort_values(by="id", ascending=False)
                if not hist.empty:
                    default_user_name = selected_user
                    default_dept = str(hist.iloc[0].get("department", ""))
                    default_loc = str(hist.iloc[0].get("location", OFFICIAL_LOCATIONS[0]))

            with st.form("new_ticket_form", clear_on_submit=True):
                a1, a2 = st.columns(2)
                user_name = a1.text_input("User Name *", value=default_user_name, placeholder="Employee name")
                attended_by = a2.selectbox("Technician", list(TECH_MAP.keys()))

                b1, b2 = st.columns(2)
                department = b1.text_input("Department *", value=default_dept, placeholder="Department / team")
                status = b2.selectbox("Initial Status", STATUS_OPTIONS)

                loc_index = OFFICIAL_LOCATIONS.index(default_loc) if default_loc in OFFICIAL_LOCATIONS else 0
                location = st.selectbox("Location / Sector *", OFFICIAL_LOCATIONS, index=loc_index)
                ticket_date = st.date_input("Ticket Date *", value=datetime.now().date())
                complaint_desc = st.text_area("Complaint Description *", height=110, placeholder="Details of issue...")
                tech_remarks = st.text_area("Technician Remarks", height=90)

                c1, c2 = st.columns(2)
                start_input = c1.time_input("Start Time", value=time(datetime.now().hour, datetime.now().minute))
                close_input = c2.time_input("Close Time", value=time(datetime.now().hour, datetime.now().minute))

                submit_ticket = st.form_submit_button("Submit Ticket", use_container_width=True)
                if submit_ticket:
                    if not user_name.strip() or not department.strip() or not complaint_desc.strip():
                        st.error("Please fill all required fields.")
                    else:
                        category = auto_categorize(complaint_desc)
                        date_str = ticket_date.strftime("%Y-%m-%d")
                        if status == "Open":
                            start_val, close_val, duration_mins = None, None, 0
                        elif status == "In Progress":
                            start_val = f"{date_str} {start_input.strftime('%H:%M:%S')}"
                            close_val = None
                            duration_mins = 0
                        elif status == "On Hold - User Busy":
                            start_val, close_val, duration_mins = None, None, 0
                        else:
                            start_val = f"{date_str} {start_input.strftime('%H:%M:%S')}"
                            close_val = f"{date_str} {close_input.strftime('%H:%M:%S')}"
                            duration_mins = max(1, int((datetime.combine(ticket_date, close_input) - datetime.combine(ticket_date, start_input)).total_seconds() / 60))

                        new_row = {
                            "date": date_str,
                            "user_name": user_name.strip(),
                            "department": department.strip(),
                            "complaint": complaint_desc.strip(),
                            "location": location,
                            "attended_by": attended_by,
                            "status": status,
                            "category": category,
                            "remarks": tech_remarks.strip(),
                            "start_time": start_val,
                            "close_time": close_val,
                            "resolution_time": duration_mins,
                        }
                        try:
                            new_id = save_ticket(new_row)
                            st.success(f"Ticket saved: {format_ticket_number(new_id, location)}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Insertion error: {e}")

            st.markdown("### Last 3 Recent Tickets")
            recent_tickets = df_live.copy()
            if not recent_tickets.empty:
                recent_tickets = recent_tickets.sort_values(by="id", ascending=False).head(3)
                render_status_table(recent_tickets, ["System Ticket ID", "date", "user_name", "location", "attended_by", "status", "remarks"], compact=True)
            else:
                st.info("No recent ticket entries available.")

            st.markdown("### AI Copilot")
            ai_text = st.text_area("Paste issue text for troubleshooting help", height=120, placeholder="Example: Outlook asking password...")
            ai_lang = st.radio("Language", ["English", "हिंदी"], horizontal=True)
            if st.button("Run AI Guidance", use_container_width=True):
                if not ai_text.strip():
                    st.warning("Please enter issue details first.")
                else:
                    cat = auto_categorize(ai_text)
                    if cat in AI_SUGGESTIONS:
                        details = AI_SUGGESTIONS[cat]
                        title = details["title_en"] if ai_lang == "English" else details["title_hi"]
                        steps = details["English"] if ai_lang == "English" else details["Hindi"]
                        html = f"<div class='panel-card'><div style='font-weight:700;color:#f87171;margin-bottom:8px;'>{title}</div>"
                        for step in steps:
                            html += f"<div style='margin-bottom:6px;'>🔹 {step}</div>"
                        html += "</div>"
                        st.markdown(html, unsafe_allow_html=True)
                    else:
                        st.info("No specific category found. Use standard physical, network, and access checks.")

        with right_col:
            if df_ticket_filtered.empty:
                st.info("No tickets found for the current filters.")
            else:
                queue_df = df_ticket_filtered.sort_values(by="id", ascending=False).copy()
                st.markdown("### Update Existing Ticket")
                ticket_options = {f"{row['System Ticket ID']} — {row['user_name']} [{row['status']}]": int(row["id"]) for _, row in queue_df.iterrows()}
                selected_label = st.selectbox("Choose a ticket", list(ticket_options.keys()))
                target_id = ticket_options[selected_label]
                target_row = queue_df[queue_df["id"] == target_id].iloc[0]

                summary_col, delete_col = st.columns([1.75, 1], gap="medium")
                with summary_col:
                    st.markdown(
                        f"""
                        <div class="summary-card">
                            <div class="summary-grid">
                                <div><div class="sum-label">User</div><div class="sum-value">{target_row['user_name']}</div></div>
                                <div><div class="sum-label">Department</div><div class="sum-value">{target_row['department']}</div></div>
                                <div><div class="sum-label">Location</div><div class="sum-value">{target_row['location']}</div></div>
                                <div><div class="sum-label">Status</div><div class="sum-value">{target_row['status']}</div></div>
                                <div class="span-2"><div class="sum-label">Complaint</div><div class="sum-value">{target_row['complaint']}</div></div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    with st.form(f"update_ticket_form_{target_id}"):
                        u1, u2 = st.columns(2)
                        current_status_idx = STATUS_OPTIONS.index(target_row["status"]) if target_row["status"] in STATUS_OPTIONS else 0
                        tech_list = list(TECH_MAP.keys())
                        current_tech_idx = tech_list.index(target_row["attended_by"]) if target_row["attended_by"] in tech_list else 0
                        new_status = u1.selectbox("Modify Status", STATUS_OPTIONS, index=current_status_idx)
                        new_tech = u2.selectbox("Reassign Technician", tech_list, index=current_tech_idx)
                        new_duration = st.number_input("Resolution Duration (minutes)", min_value=0, value=int(target_row["resolution_time"]) if pd.notna(target_row["resolution_time"]) else 0)
                        new_remarks = st.text_area("Update Remarks", value=str(target_row.get("remarks", "")), height=90)
                        save_update = st.form_submit_button("Save Changes")
                        if save_update:
                            final_remarks = new_remarks.strip()
                            if new_status == "On Hold - User Busy" and not final_remarks:
                                final_remarks = "Technician reached user, but action postponed due to business activity."
                            payload = {
                                "status": new_status,
                                "attended_by": new_tech,
                                "resolution_time": int(new_duration),
                                "remarks": final_remarks,
                            }
                            if new_status == "Resolved" and not target_row.get("close_time"):
                                payload["close_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            try:
                                update_ticket(target_id, payload)
                                st.success("Ticket updated successfully.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Update error: {e}")

                with delete_col:
                    st.markdown("<div class='danger-box'><h4>Delete Ticket</h4><div class='mini-note'>Delete only if incorrect.</div></div>", unsafe_allow_html=True)
                    confirm_ticket_delete = st.checkbox("I confirm delete.", key="ticket_delete_confirm")
                    if st.button("Delete Selected Ticket", disabled=not confirm_ticket_delete, use_container_width=True):
                        try:
                            delete_ticket(target_id)
                            st.success("Ticket deleted successfully.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Delete error: {e}")

                st.markdown("### Active Queue")
                st.markdown("<div class='queue-shell'>", unsafe_allow_html=True)
                render_status_table(queue_df.head(10), ["System Ticket ID", "date", "user_name", "department", "location", "category", "attended_by", "status"], compact=True)
                st.markdown("</div>", unsafe_allow_html=True)

    # ------------------ NAS MONITORING PAGE ------------------
    elif page == "NAS Monitoring":
        st.subheader("NAS Monitoring")
        nas_tab1, nas_tab2, nas_tab3, nas_tab4 = st.tabs(["Log Entry", "Health Dashboard", "Raw Logs", "Delete Wrong Entry"])

        with nas_tab1:
            st.markdown("### Log Backup Entry")
            with st.form("nas_form", clear_on_submit=True):
                n1, n2 = st.columns(2)
                log_date = n1.date_input("Backup Date", value=datetime.now().date())
                server_name = n2.selectbox("Server Name", SERVER_NAMES)
                st.caption(f"Mapped worksheet reference: {SERVER_SHEET_MAP.get(server_name, 'N/A')}")
                n3, n4 = st.columns(2)
                log_status = n3.selectbox("Backup Status", ["Success", "Failed"])
                log_storage_kb = n4.number_input("Storage Used (KB)", min_value=0.0, step=1024.0)
                st.caption(f"Automatic conversion preview: {round(log_storage_kb / (1024 * 1024), 4)} GB")
                log_remarks = st.text_area("Operational Remarks / Error Logs", height=90)
                submit_nas = st.form_submit_button("Submit Backup Log")
                if submit_nas:
                    try:
                        new_log = {
                            "date": log_date.strftime("%Y-%m-%d"),
                            "server_name": server_name,
                            "status": log_status,
                            "storage_used": round(float(log_storage_kb) / (1024 * 1024), 4),
                            "remarks": log_remarks.strip(),
                        }
                        new_id = save_nas_log(new_log)
                        st.success(f"NAS log saved successfully. Entry ID: {new_id}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"NAS save error: {e}")

            st.markdown("### Last 3 Backup Entries")
            latest_nas = df_nas.copy()
            if not latest_nas.empty:
                latest_nas = latest_nas[latest_nas["server_name"] == server_name].copy()
                if not latest_nas.empty:
                    latest_nas = latest_nas.sort_values(by=["id", "date"], ascending=[False, False]).head(3)
                    latest_nas["storage_used"] = latest_nas["storage_used"].map(lambda x: f"{x:.4f} GB")
                    render_status_table(latest_nas, ["id", "date", "server_name", "status", "storage_used", "remarks"], compact=True, nas_mode=True)
                else:
                    st.info(f"No previous NAS entries found for server {server_name}.")

        with nas_tab2:
            st.markdown("### Health Dashboard")
            if df_nas_filtered_global.empty:
                st.info("No NAS logs found for the selected filter.")
            else:
                selected_server = st.selectbox("Choose server view", SERVER_NAMES, key="nas_server_dashboard")
                server_df = df_nas[df_nas["server_name"] == selected_server].copy()
                if server_df.empty:
                    st.info("No logs available for this server.")
                else:
                    server_df = server_df.sort_values(by="date", ascending=True).copy()
                    server_df["Change (GB)"] = server_df["storage_used"].diff().round(4)
                    server_df["Change (%)"] = (server_df["storage_used"].pct_change() * 100).round(2)
                    latest = server_df.iloc[-1]
                    latest_status = latest["status"]
                    latest_date = latest["date"]
                    latest_size = latest["storage_used"]
                    if latest_status == "Failed":
                        st.error(f"Critical alert: latest backup on {latest_date} for {selected_server} failed.")
                    else:
                        st.success(f"Latest backup on {latest_date} for {selected_server} completed successfully.")
                    
                    m1, m2, m3 = st.columns(3)
                    delta_text = f"{server_df.iloc[-1]['Change (GB)']:+.4f} GB" if len(server_df) >= 2 and pd.notna(server_df.iloc[-1]["Change (GB)"]) else "Baseline"
                    m1.metric("Latest Footprint", f"{latest_size:,.4f} GB", delta=delta_text)
                    m2.metric("Total Logs", len(server_df))
                    m3.metric("Failures", int((server_df["status"] == "Failed").sum()))
                    
                    trend_df = server_df.copy()
                    trend_df["date"] = pd.to_datetime(trend_df["date"], errors="coerce")
                    trend_df["date_label"] = trend_df["date"].dt.strftime("%Y-%m-%d")
                    st.markdown("#### Storage Trend")
                    st.altair_chart(build_line_chart(trend_df, "date_label:N", "storage_used:Q", "#3b82f6"), use_container_width=True)
                    
                    st.markdown("#### Historical Log Matrix")
                    table_df = server_df.sort_values(by="date", ascending=False).copy()
                    table_df["Change (GB)"] = table_df["Change (GB)"].apply(lambda x: f"{x:+.4f} GB" if pd.notnull(x) else "— Baseline")
                    table_df["Change (%)"] = table_df["Change (%)"].apply(lambda x: f"{x:+.2f}%" if pd.notnull(x) else "— Baseline")
                    table_df["storage_used"] = table_df["storage_used"].map(lambda x: f"{x:.4f} GB")
                    render_status_table(table_df, ["id", "date", "server_name", "status", "storage_used", "Change (GB)", "Change (%)", "remarks"], compact=True, nas_mode=True)

        with nas_tab3:
            st.markdown("### Raw NAS Logs")
            if df_nas_filtered_global.empty:
                st.info("No NAS records found.")
            else:
                raw_view = df_nas_filtered_global.sort_values(by=["date", "id"], ascending=[False, False]).copy()
                raw_view["storage_used"] = raw_view["storage_used"].map(lambda x: f"{x:.4f} GB")
                render_status_table(raw_view, ["id", "date", "server_name", "status", "storage_used", "remarks"], compact=True, nas_mode=True)

        with nas_tab4:
            st.markdown("### Delete Wrong NAS Entry")
            st.warning("Use this only when an incorrect backup log was entered.")
            if df_nas.empty:
                st.info("No NAS entries available to delete.")
            else:
                delete_view = df_nas.sort_values(by=["date", "id"], ascending=[False, False]).copy()
                delete_view["entry_label"] = delete_view.apply(lambda r: f"ID {r['id']} | {r['date']} | {r['server_name']} | {r['status']} | {r['storage_used']:.4f} GB", axis=1)
                selected_entry = st.selectbox("Select wrong NAS entry", delete_view["entry_label"].tolist())
                row = delete_view[delete_view["entry_label"] == selected_entry].iloc[0]
                confirm_delete = st.checkbox("I confirm this entry is wrong and should be deleted.")
                if st.button("Delete Selected NAS Entry", disabled=not confirm_delete):
                    try:
                        delete_nas_log(int(row["id"]))
                        st.success(f"NAS entry ID {int(row['id'])} deleted.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Delete error: {e}")

    # ------------------ REPORTS PAGE ------------------
    elif page == "Reports":
        st.subheader("Reports Portal")
        
        # TAB SEGMENTS
        t_tickets, t_nas = st.tabs(["Ticket Activity Logs", "NAS Performance & Deltas"])
        
        with t_tickets:
            if df_ticket_filtered.empty:
                st.info("No ticket records available.")
            else:
                export_df = df_ticket_filtered.copy()
                export_df["date_parsed"] = pd.to_datetime(export_df["date"], errors="coerce")
                export_df = export_df.dropna(subset=["date_parsed"])
                export_df["Month"] = export_df["date_parsed"].dt.strftime("%Y-%m (%B)")
                export_df["Week_of_Year"] = export_df["date_parsed"].dt.isocalendar().week.astype(str)
                export_df["Week_Label"] = export_df["date_parsed"].dt.strftime("%Y-W") + export_df["Week_of_Year"]
                
                st.download_button("Download Master Ticket Log (.csv)", export_df.drop(columns=["date_parsed"], errors="ignore").to_csv(index=False).encode("utf-8"), file_name="it_master_production_log.csv", mime="text/csv")

                rep_tab1, rep_tab2, rep_tab3, rep_tab4 = st.tabs(["Monthly", "Weekly", "Technician", "Location"])
                with rep_tab1:
                    months = sorted(export_df["Month"].dropna().unique().tolist(), reverse=True)
                    if months:
                        selected_month = st.selectbox("Select month", months)
                        month_df = export_df[export_df["Month"] == selected_month].drop(columns=["date_parsed", "Month", "Week_of_Year", "Week_Label"], errors="ignore")
                        render_status_table(month_df, ["System Ticket ID", "date", "user_name", "department", "location", "attended_by", "status", "resolution_time", "remarks"], compact=True)
                with rep_tab2:
                    weeks = sorted(export_df["Week_Label"].dropna().unique().tolist(), reverse=True)
                    if weeks:
                        selected_week = st.selectbox("Select week", weeks)
                        week_df = export_df[export_df["Week_Label"] == selected_week].drop(columns=["date_parsed", "Month", "Week_of_Year", "Week_Label"], errors="ignore")
                        render_status_table(week_df, ["System Ticket ID", "date", "user_name", "department", "location", "attended_by", "status", "resolution_time", "remarks"], compact=True)
                with rep_tab3:
                    techs = sorted(export_df["attended_by"].dropna().astype(str).unique().tolist())
                    if techs:
                        selected_tech = st.selectbox("Select technician", techs)
                        tech_df = export_df[export_df["attended_by"] == selected_tech].drop(columns=["date_parsed", "Month", "Week_of_Year", "Week_Label"], errors="ignore")
                        render_status_table(tech_df, ["System Ticket ID", "date", "user_name", "department", "location", "status", "resolution_time", "remarks"], compact=True)
                with rep_tab4:
                    locations = sorted(export_df["location"].dropna().astype(str).unique().tolist())
                    if locations:
                        selected_loc = st.selectbox("Select location", locations)
                        loc_df = export_df[export_df["location"] == selected_loc].drop(columns=["date_parsed", "Month", "Week_of_Year", "Week_Label"], errors="ignore")
                        render_status_table(loc_df, ["System Ticket ID", "date", "user_name", "department", "attended_by", "status", "resolution_time", "remarks"], compact=True)
        
        with t_nas:
            if df_nas_filtered_global.empty:
                st.info("No NAS logs found.")
            else:
                master_df, monthly_df, serverwise_df = build_nas_reports(df_nas_filtered_global)
                
                col_n1, col_n2, col_n3 = st.columns(3)
                col_n1.download_button('Download NAS Master Data', master_df.to_csv(index=False).encode('utf-8'), 'nas_master_report.csv', 'text/csv', use_container_width=True)
                col_n2.download_button('Download NAS Monthly Report', monthly_df.to_csv(index=False).encode('utf-8'), 'nas_monthly_report.csv', 'text/csv', use_container_width=True)
                col_n3.download_button('Download NAS Server-wise Report', serverwise_df.to_csv(index=False).encode('utf-8'), 'nas_serverwise_report.csv', 'text/csv', use_container_width=True)
                
                st.markdown("### Server-wise Aggregations")
                st.dataframe(serverwise_df, use_container_width=True, hide_index=True)
                
                st.markdown("### Monthly Data Matrix")
                st.dataframe(monthly_df, use_container_width=True, hide_index=True)

    # ------------------ ADMIN TOOLS PAGE ------------------
    elif page == "Admin Tools":
        st.subheader("Admin Tools")
        a1, a2 = st.columns([1.1, 1], gap="large")
        with a1:
            st.markdown("### Recurring User Analysis")
            if df_live.empty:
                st.info("No ticket data available.")
            else:
                recurring = (
                    df_live.groupby("user_name")
                    .agg(
                        total_requests=("id", "count"),
                        resolved_count=("status", lambda s: (s == "Resolved").sum()),
                        pending_backlog=("status", lambda s: (s != "Resolved").sum()),
                    )
                    .reset_index()
                    .sort_values(by="total_requests", ascending=False)
                )
                st.dataframe(recurring, use_container_width=True, hide_index=True)
                chronic = recurring[recurring["total_requests"] >= 2]
                if not chronic.empty:
                    st.warning(f"{len(chronic)} users have repeated incidents. Consider root-cause reviews.")
        with a2:
            st.markdown("### System Snapshot")
            st.metric("Cloud Connection", "Connected" if db_connected else "Sandbox")
            st.metric("Ticket Rows", len(df_live))
            st.metric("NAS Rows", len(df_nas))
            st.markdown("### Quick Health Check")
            if not df_nas.empty and (df_nas["status"] == "Failed").any():
                st.error("There are failed NAS backup entries that need review.")
            else:
                st.success("No NAS failures currently visible.")

    # ------------------ TASK CENTER PAGE ------------------
    elif page == "Task Center":
        st.subheader("Operational Tasks & Vendor Actions")
        conn = get_db_connection()
        user_info = st.session_state['current_user']
        cur_role = user_info['role']
        cur_user = user_info['display_name']

        t_view, t_create = st.tabs(["Tasks Overview", "Assign New Task / Vendor Action"])

        with t_view:
            st.markdown("### Track Current Progress")
            query = "SELECT * FROM tasks ORDER BY id DESC"
            tasks_df = pd.read_sql_query(query, conn)
            
            if tasks_df.empty:
                st.info("No tasks assigned yet.")
            else:
                # Filter viewing permissions
                if cur_role not in ['IT Manager', 'IT AM', 'AVP']:
                    tasks_df = tasks_df[tasks_df['assigned_to'] == cur_user]

                if tasks_df.empty:
                    st.info("No active tasks found assigned to you.")
                else:
                    for idx, r in tasks_df.iterrows():
                        with st.expander(f"Task ID: {r['id']} | {r['title']} [{r['status']}]"):
                            st.write(f"**Description:** {r['description']}")
                            st.write(f"**Assigned By:** {r['assigned_by']} | **Assigned To:** {r['assigned_to']}")
                            st.write(f"**Priority:** {r['priority']} | **Due Date:** {r['due_date']}")
                            
                            # Vendor Tracking Details
                            if r['vendor_flag'] == 1:
                                st.info(f"Vendor Operations: {r['vendor_status']} — {r['vendor_remark']}")
                            
                            # Log Task Comments
                            st.markdown("---")
                            st.caption("Comments & Updates")
                            comments_query = f"SELECT * FROM task_comments WHERE task_id = {r['id']} ORDER BY id DESC"
                            comm_df = pd.read_sql_query(comments_query, conn)
                            for _, c in comm_df.iterrows():
                                st.write(f"*{c['created_at']} - {c['commented_by']}:* {c['comment']}")
                            
                            # Task Modification Section
                            with st.form(f"task_mod_{r['id']}"):
                                new_status = st.selectbox("Update Status", ["Open", "In Progress", "Completed", "On Hold"], index=["Open", "In Progress", "Completed", "On Hold"].index(r['status']))
                                new_progress = st.slider("Progress %", 0, 100, int(r['progress']))
                                comment_txt = st.text_input("Add Comment / Action Note")
                                
                                # Vendor Flag Management (Manager/AM only)
                                if cur_role in ['IT Manager', 'IT AM']:
                                    new_v_status = st.text_input("Vendor Status", value=str(r['vendor_status'] or ""))
                                    new_v_remark = st.text_area("Vendor Remark", value=str(r['vendor_remark'] or ""))
                                else:
                                    new_v_status = r['vendor_status']
                                    new_v_remark = r['vendor_remark']

                                update_btn = st.form_submit_button("Update Task Status")
                                if update_btn:
                                    conn.execute(
                                        "UPDATE tasks SET status=?, progress=?, vendor_status=?, vendor_remark=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                                        (new_status, new_progress, new_v_status, new_v_remark, r['id'])
                                    )
                                    if comment_txt.strip():
                                        conn.execute(
                                            "INSERT INTO task_comments (task_id, comment, commented_by) VALUES (?, ?, ?)",
                                            (r['id'], comment_txt.strip(), cur_user)
                                        )
                                    conn.commit()
                                    st.success("Task updated.")
                                    st.rerun()

        with t_create:
            if cur_role not in ['IT Manager', 'IT AM']:
                st.warning("Only IT Managers and Assistant Managers are authorized to create or assign tasks.")
            else:
                st.markdown("### Launch Task Action")
                with st.form("create_task_form"):
                    title = st.text_input("Task Title *")
                    desc = st.text_area("Detailed Description")
                    assigned_to = st.selectbox("Assign To", ["All Techs"] + list(TECH_MAP.keys()) + ["Amit", "Satish", "Ranjan", "Priyanshu", "Manish"])
                    priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
                    due_date = st.date_input("Due Date")
                    
                    # Vendor Follow-up flag
                    vendor_flag = st.checkbox("Requires Vendor Follow-up?")
                    v_name = st.text_input("Vendor Name (Optional)")
                    
                    submit_t = st.form_submit_button("Create Assignment")
                    if submit_t:
                        if not title.strip():
                            st.error("Task Title is required.")
                        else:
                            conn.execute(
                                """INSERT INTO tasks (title, description, assigned_by, assigned_to, priority, due_date, vendor_flag, vendor_status)
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                                (title, desc, cur_user, assigned_to, priority, due_date.strftime("%Y-%m-%d"), 1 if vendor_flag else 0, "Initial Assignment" if vendor_flag else None)
                            )
                            conn.commit()
                            st.success("Task created and assigned successfully.")
                            st.rerun()
        conn.close()

    # ------------------ AVP DASHBOARD PAGE ------------------
    elif page == "AVP Dashboard":
        st.subheader("AVP Executive Command Suite")
        conn = get_db_connection()
        
        # Pull Tasks and Tickets for High-Level Calculations
        tasks_df = pd.read_sql_query("SELECT * FROM tasks", conn)
        tickets_df = df_live.copy()
        
        # High Level SLA & Summary Metrics
        st.markdown("### SLA Status & Active Operations Summary")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        
        open_tickets_cnt = len(tickets_df[tickets_df['status'].isin(['Open', 'In Progress'])])
        resolved_tickets_cnt = len(tickets_df[tickets_df['status'] == 'Resolved'])
        total_backlog_ratio = round((open_tickets_cnt / len(tickets_df) * 100), 1) if not tickets_df.empty else 0
        
        m_col1.metric("Active Incident Backlog", open_tickets_cnt)
        m_col2.metric("Backlog-to-Resolution Ratio", f"{total_backlog_ratio}%")
        m_col3.metric("Total Completed Tasks", len(tasks_df[tasks_df['status'] == 'Completed']) if not tasks_df.empty else 0)
        
        active_nas_fails = int((df_nas["status"] == "Failed").sum()) if not df_nas.empty else 0
        m_col4.metric("Active Critical NAS Errors", active_nas_fails)

        st.markdown("---")
        st.markdown("### Department Incident Distributions")
        
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            if not tickets_df.empty:
                dept_df = tickets_df['department'].value_counts().reset_index()
                dept_df.columns = ["department", "count"]
                st.altair_chart(build_bar_chart(dept_df, "department:N", "count:Q", "#ef4444"), use_container_width=True)
        with col_chart2:
            if not tasks_df.empty:
                st.markdown("#### Pending Tasks Priorities")
                task_prio = tasks_df['priority'].value_counts().reset_index()
                task_prio.columns = ["priority", "count"]
                st.altair_chart(build_bar_chart(task_prio, "priority:N", "count:Q", "#3b82f6"), use_container_width=True)

        st.markdown("---")
        st.markdown("### Critical High-Priority Tasks")
        if not tasks_df.empty:
            crit_tasks = tasks_df[tasks_df['priority'].isin(['High', 'Critical']) & (tasks_df['status'] != 'Completed')]
            if crit_tasks.empty:
                st.success("All critical high-priority tasks are currently clear.")
            else:
                st.dataframe(crit_tasks[['id', 'title', 'assigned_to', 'priority', 'status', 'due_date']], use_container_width=True, hide_index=True)
        else:
            st.info("No tracking task metrics available.")
            
        conn.close()

# ==========================================
# 10. APP ENTRYPOINT & CONTROL ROUTER
# ==========================================
def app_startup():
    conn = None
    try:
        conn = get_db_connection()
        init_support_data(conn)
        bootstrap_auth_gate(conn)
        render_dashboard()
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    app_startup()
