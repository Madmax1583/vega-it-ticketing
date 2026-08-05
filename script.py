import io
import hashlib
import sqlite3
from datetime import datetime, time
from pathlib import Path

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
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

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
        cur.execute("SELECT id FROM users WHERE username=?", (username,))
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO users (username, display_name, role, password_hash, active, must_change_password) VALUES (?, ?, ?, ?, 1, 1)",
                (username, display_name, role, None),
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
AI_SUGGESTIONS = {
    "CCTVCamera": {"title_en": "📷 AI Video Infrastructure Diagnostics", "title_hi": "📷 एआई वीडियो इन्फ्रास्ट्रक्चर डायग्नोस्टिक्स", "English": ["Check whether the camera POE switch port light is blinking.", "Ping the camera IP address through CMD to confirm network continuity.", "If NVR shows no video, restart the camera channel or re-login the device."], "Hindi": ["जांचें कि कैमरा POE स्विच पोर्ट की लाइट ब्लिंक कर रही है या नहीं।", "नेटवर्क कनेक्टिविटी जांचने के लिए कैमरा IP एड्रेस को पिंग करें।", "यदि NVR 'No Video' दिखाए, तो कैमरा चैनल रीस्टार्ट या री-लॉगिन करें।"]},
    "LaptopHardware": {"title_en": "💻 AI Endpoint Hardware Diagnostics", "title_hi": "💻 एआई एंडपॉइंट हार्डवेयर डायग्नोस्टिक्स", "English": ["Perform a hard reset by disconnecting power and holding the power button for 30 seconds.", "Connect to an external display to isolate panel versus motherboard issues.", "Check Device Manager and reinstall chipset or hardware drivers if needed."], "Hindi": ["पावर डिस्कनेक्ट करके 30 सेकंड तक पावर बटन दबाकर हार्ड रीसेट करें।", "LCD और मदरबोर्ड समस्या अलग करने के लिए बाहरी मॉनिटर लगाएं।", "Device Manager जांचें और आवश्यक होने पर ड्राइवर पुनः इंस्टॉल करें।"]},
    "EmailOutlook": {"title_en": "📧 AI Communication Layer Diagnostics", "title_hi": "📧 एआई कम्यूनिकेशन लेयर डायग्नोस्टिक्स", "English": ["Run outlook.exe /safe to isolate add-in conflicts.", "Check PST or OST file size and compact it if very large.", "Clear Credential Manager entries if password prompts repeat."], "Hindi": ["Add-in conflict जांचने के लिए outlook.exe /safe चलाएं।", "PST या OST फ़ाइल का आकार जांचें और जरूरत हो तो compact करें।", "बार-बार पासवर्ड आने पर Credential Manager entries साफ करें।"]},
    "Printer": {"title_en": "🖨️ AI Print Management Diagnostics", "title_hi": "🖨️ एआई प्रिंट मैनेजमेंट डायग्नोस्टिक्स", "English": ["Verify Printer Properties, configured port, and SNMP setting.", "Restart Print Spooler and clear stuck jobs in the PRINTERS folder.", "Inspect cartridge, rollers, and scanner glass for quality issues."], "Hindi": ["Printer Properties, port configuration और SNMP setting जांचें।", "Print Spooler restart करें और stuck jobs साफ करें।", "कार्ट्रिज, रोलर्स और स्कैनर ग्लास जांचें।"]},
    "SAP": {"title_en": "🏢 AI Enterprise ERP Diagnostics", "title_hi": "🏢 एआई एंटरप्राइज ईआरपी डायग्नोस्टिक्स", "English": ["Verify SAP logon configuration and network reachability.", "Check for locked or hung sessions through SAP tools.", "Repair SAP GUI or clear cache if the client is unstable."], "Hindi": ["SAP logon configuration और network connectivity जांचें।", "Locked या hung sessions जांचें।", "Client unstable होने पर SAP GUI repair या cache clear करें।"]},
    "Network": {"title_en": "🌐 AI Network Routing Diagnostics", "title_hi": "🌐 एआई नेटवर्क राउटिंग डायग्नोस्टिक्स", "English": ["Reset Winsock and inspect the adapter driver for frequent drops.", "Release and renew IP configuration if conflict is suspected.", "Check the SSID and frequency band being used by the device."], "Hindi": ["बार-बार डिस्कनेक्ट होने पर Winsock reset और adapter driver जांचें।", "IP conflict शक होने पर release और renew करें।", "SSID और frequency band की पुष्टि करें।"]},
    "ServerUPS": {"title_en": "🖥️ Server & Power Infrastructure Diagnostics", "title_hi": "🖥️ सर्वर और पावर इन्फ्रास्ट्रक्चर डायग्नोस्टिक्स", "English": ["Check UPS load and input power if alarms are active.", "Verify rack airflow and server room temperature.", "Review DNS and authentication dependencies if logins fail."], "Hindi": ["अलार्म आने पर UPS load और input power जांचें।", "Rack airflow और server room temperature जांचें।", "Login fail होने पर DNS और authentication dependencies देखें।"]},
}

CATEGORY_OPTIONS = [
    "LaptopHardware",
    "Printer",
    "EmailOutlook",
    "Network",
    "CCTVCamera",
    "SAP",
    "ServerUPS",
    "AVSupport",
    "AccessControl",
    "Telephony",
    "SoftwareSupport",
    "FileShareAccess",
    "InstallationSetup",
    "Other",
]

CATEGORY_SUBCATEGORY_MAP = {
    "LaptopHardware": ["Slow/Hanging", "Boot/Startup", "Power", "Battery", "Charging", "Keyboard/Mouse", "Display/Monitor", "RAM Upgrade", "Driver/Update", "User Profile/Login", "Device Handover"],
    "Printer": ["Printer Install", "Driver Issue", "Print Queue", "Paper Jam", "Cartridge/Drum", "Scanner Issue", "USB/LAN Printer", "Page Size/Settings"],
    "EmailOutlook": ["Outlook Not Opening", "Mail Send/Receive", "PST/Archive", "O365 License", "New Email ID", "Delete/Reactivate ID", "Forwarding", "Signature", "Mobile Config"],
    "Network": ["Internet Down", "Wi-Fi", "LAN", "Router/Booster", "Firewall", "VPN", "RDP Access", "Remote Access"],
    "CCTVCamera": ["Live View", "Playback", "Recording", "Camera Install", "Camera Relocation", "NVR Status", "IVMS Tool"],
    "SAP": ["SAP Login", "SAP Slow/Hang", "SAP Attachment", "SAP Mail", "RDP for SAP", "DTW/Data Transfer"],
    "ServerUPS": ["Server Health Check", "Backup", "UPS Issue", "Virus on Server", "Warranty/Renewal", "Server Restart"],
    "AVSupport": ["Projector Install", "TV/OPS Setup", "Boardroom Support", "Meeting Join Support", "HDMI/Display Sharing"],
    "AccessControl": ["Attendance Portal", "Biometric Device", "Spintly", "Door Access", "Punching Device"],
    "Telephony": ["Telephone Instrument", "Extension Issue", "EPBX Setting", "Intercom", "IO Box"],
    "SoftwareSupport": ["Zoom Install", "Adobe/PDF Reader", "AutoCAD Renewal", "Photoshop", "Java Update", "Browser/Website/App Issue"],
    "FileShareAccess": ["OneDrive Sync/Backup", "Shared Folder Access", "File Search", "File Open Issue", "Data Copy/Migration"],
    "InstallationSetup": ["New System Install", "Software Install", "New Joiner Setup", "Device Configuration", "LCD/Display Install"],
    "Other": ["Other"],
}

AUTO_CATEGORY_RULES = [
    ("CCTVCamera", ["cctv", "camera", "nvr", "playback", "recording", "footage", "ivms"]),
    ("AccessControl", ["attendance", "biometric", "spintly", "door access", "punching"]),
    ("AVSupport", ["projector", "tv", "ops", "meeting room", "board room", "boardroom", "conference room", "hdmi", "display sharing"]),
    ("Telephony", ["telephone", "extension", "epbx", "intercom", "io box"]),
    ("Printer", ["printer", "scanner", "scan", "cartridge", "drum", "print", "spooler", "paper jam"]),
    ("EmailOutlook", ["outlook", "email", "mail", "pst", "ost", "o365", "office 365", "mailbox", "forwarding", "signature"]),
    ("SAP", ["sap", "erp", "dtw", "data transfer workbench"]),
    ("Network", ["network", "wifi", "wi-fi", "internet", "vpn", "ping", "ip", "router", "switch", "lan", "rdp", "remote access"]),
    ("ServerUPS", ["server", "ups", "rack", "dns", "domain", "backup", "replication", "nas"]),
    ("FileShareAccess", ["onedrive", "shared folder", "shared drive", "file search", "windows explorer", "file not opening", "data copy", "data backup", "cloud storage"]),
    ("SoftwareSupport", ["zoom", "autocad", "photoshop", "adobe", "pdf", "java", "browser", "website", "web side", "software", "application"]),
    ("InstallationSetup", ["new system install", "new joining", "new joiner", "configured", "configuration", "setup", "install software", "device handover"]),
    ("LaptopHardware", ["laptop", "desktop", "keyboard", "touchpad", "battery", "charger", "charging", "screen", "hardware", "monitor", "slow", "hanging", "hang", "boot", "startup", "power issue", "ram", "display", "mouse", "login issue", "stuck"]),
]

SUBCATEGORY_HINT_RULES = {
    "LaptopHardware": [("Slow/Hanging", ["slow", "hang", "hanging", "stuck", "not responding"]), ("Boot/Startup", ["boot", "startup", "turning on", "not turning on", "start"]), ("Battery", ["battery", "backup", "swollen"]), ("Charging", ["charging", "charger", "socket", "dc jack", "adapter", "adopter"]), ("Keyboard/Mouse", ["keyboard", "mouse", "touchpad"]), ("Display/Monitor", ["display", "monitor", "screen", "hdmi", "ghosting", "font"]), ("RAM Upgrade", ["ram"]), ("Driver/Update", ["driver", "windows update", "bios", "patch"]), ("User Profile/Login", ["login", "credential", "profile"]), ("Device Handover", ["handover", "transfer the laptop", "configured in new joineer"] )],
    "Printer": [("Scanner Issue", ["scanner", "scan"]), ("Cartridge/Drum", ["cartridge", "drum"]), ("Paper Jam", ["paper jam"]), ("Print Queue", ["queue", "pending print", "spooler"]), ("USB/LAN Printer", ["usb", "lan"]), ("Page Size/Settings", ["page size", "settings"]), ("Driver Issue", ["driver"]), ("Printer Install", ["install", "add"] )],
    "EmailOutlook": [("Mail Send/Receive", ["send", "receive", "incoming", "attachment"]), ("PST/Archive", ["pst", "archive"]), ("O365 License", ["license", "licence", "o365 basic", "standard"]), ("New Email ID", ["create new", "new joining email", "new email id"]), ("Delete/Reactivate ID", ["delete", "reactivate", "remove the email"]), ("Forwarding", ["forwarding"]), ("Signature", ["signature"]), ("Mobile Config", ["mobile", "phone"]), ("Outlook Not Opening", ["outlook is not opening", "outlook problem", "mail open problem"] )],
    "Network": [("Wi-Fi", ["wifi", "wi-fi"]), ("LAN", ["lan"]), ("Router/Booster", ["router", "signal booster"]), ("Firewall", ["firewall"]), ("VPN", ["vpn"]), ("RDP Access", ["rdp"]), ("Remote Access", ["remote access", "any desk", "anydesk"]), ("Internet Down", ["internet"] )],
    "CCTVCamera": [("Playback", ["playback", "footage"]), ("Recording", ["recording"]), ("Camera Install", ["install"]), ("Camera Relocation", ["relocated", "reposition", "coverage"]), ("NVR Status", ["nvr status", "matrix nvr"]), ("IVMS Tool", ["ivms"]), ("Live View", ["live"] )],
    "SAP": [("SAP Login", ["login"]), ("SAP Slow/Hang", ["slow", "hang"]), ("SAP Attachment", ["attachment", "file not open"]), ("SAP Mail", ["sap mail"]), ("RDP for SAP", ["rdp"]), ("DTW/Data Transfer", ["dtw", "data transfer"] )],
    "ServerUPS": [("Backup", ["backup"]), ("UPS Issue", ["ups"]), ("Virus on Server", ["virus"]), ("Warranty/Renewal", ["warranty", "renewal"]), ("Server Restart", ["restart", "down"]), ("Server Health Check", ["health", "server"] )],
    "AVSupport": [("Projector Install", ["projector"]), ("TV/OPS Setup", ["tv", "ops"]), ("Meeting Join Support", ["meeting joining", "meeting"]), ("Boardroom Support", ["board room", "boardroom", "conference room"]), ("HDMI/Display Sharing", ["hdmi", "display sharing", "tv share"] )],
    "AccessControl": [("Attendance Portal", ["attendance"]), ("Biometric Device", ["biometric"]), ("Spintly", ["spintly"]), ("Door Access", ["door access"]), ("Punching Device", ["punching"] )],
    "Telephony": [("Telephone Instrument", ["telephone"]), ("Extension Issue", ["extension"]), ("EPBX Setting", ["epbx"]), ("Intercom", ["intercom"]), ("IO Box", ["io box"] )],
    "SoftwareSupport": [("Zoom Install", ["zoom"]), ("Adobe/PDF Reader", ["adobe", "pdf"]), ("AutoCAD Renewal", ["autocad"]), ("Photoshop", ["photoshop"]), ("Java Update", ["java"]), ("Browser/Website/App Issue", ["website", "web side", "browser", "application", "app"] )],
    "FileShareAccess": [("OneDrive Sync/Backup", ["onedrive", "backup"]), ("Shared Folder Access", ["shared folder", "shared drive"]), ("File Search", ["file search", "windows explorer"]), ("File Open Issue", ["file not opening", "not opening"]), ("Data Copy/Migration", ["data copy", "migration", "cloud storage"] )],
    "InstallationSetup": [("New System Install", ["new system"]), ("Software Install", ["install"]), ("New Joiner Setup", ["new joining", "new joiner"]), ("Device Configuration", ["configured", "configuration", "setup"]), ("LCD/Display Install", ["lcd install"] )],
}

def suggest_subcategory(category, complaint):
    text = str(complaint).lower().strip()
    for subcat, keywords in SUBCATEGORY_HINT_RULES.get(category, []):
        if any(k in text for k in keywords):
            return subcat
    return CATEGORY_SUBCATEGORY_MAP.get(category, ["Other"])[0]

if "local_tickets" not in st.session_state:
    st.session_state.local_tickets = pd.DataFrame([
        {"id": 1, "date": "2026-07-01", "user_name": "Amit Sharma", "department": "Production", "complaint": "CCTV camera in main corridor is flickering", "location": "Sector - 136 Vega", "attended_by": "Satish", "status": "In Progress", "category": "CCTVCamera", "start_time": "2026-07-01 10:15:00", "close_time": None, "resolution_time": 0, "remarks": "POE check in progress"},
        {"id": 2, "date": "2026-07-03", "user_name": "Sunita Rao", "department": "Finance", "complaint": "Desktop showing blue screen after update", "location": "Knitpro 28-29", "attended_by": "Priyanshu", "status": "Open", "category": "LaptopHardware", "start_time": None, "close_time": None, "resolution_time": 0, "remarks": ""},
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

def auto_categorize(complaint):
    text = str(complaint).lower().strip()
    for category, keywords in AUTO_CATEGORY_RULES:
        if any(k in text for k in keywords):
            return category
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
    out["category"] = out["category"].fillna("").astype(str)
    out["category"] = out.apply(lambda r: r["category"] if str(r["category"]).strip() else auto_categorize(r.get("complaint", "")), axis=1)
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
        tickets_df.to_excel(writer, sheet_name="Master Tickets", index=False)
        nas_master, nas_monthly, nas_serverwise = build_nas_reports(nas_df)
        if not nas_master.empty:
            nas_master.to_excel(writer, sheet_name="NAS Storage Logs", index=False)
            nas_monthly.to_excel(writer, sheet_name="NAS Monthly Summary", index=False)
            nas_serverwise.to_excel(writer, sheet_name="NAS Server Summary", index=False)
    return output.getvalue()

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
        if response.data and "id" in response.data[0]: return int(response.data[0]["id"])
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
    st.session_state.local_tickets = st.session_state.local_tickets[st.session_state.local_tickets["id"] != int(ticket_id)].reset_index(drop=True)

def save_nas_log(new_row):
    if db_connected:
        response = supabase_client.table("nas_backups").insert(new_row).execute()
        if response.data and "id" in response.data[0]: return int(response.data[0]["id"])
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

def get_user_by_username(conn, username):
    cur = conn.cursor()
    cur.execute("SELECT id, username, display_name, role, password_hash, active, must_change_password FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    return dict(zip(["id", "username", "display_name", "role", "password_hash", "active", "must_change_password"], row)) if row else None

def set_user_password(conn, username, password):
    conn.execute("UPDATE users SET password_hash=?, must_change_password=0, active=1, updated_at=CURRENT_TIMESTAMP WHERE username=?", (hash_password(password), username))
    conn.commit()

def authenticate_user(conn, username, password):
    user = get_user_by_username(conn, username)
    if not user or not user["active"]: return None
    if not user["password_hash"]:
        if password == "vega123": return {"must_change_password": True, **user}
        return None
    if user["password_hash"] == hash_password(password):
        return {"must_change_password": bool(user["must_change_password"]), **user}
    return None

def login_page(conn):
    st.title("Vega IT System Login")
    c1, c2 = st.columns(2)
    username = c1.text_input("Username").strip().lower()
    password = c2.text_input("Password", type="password")
    st.caption("Default setup password for new unconfigured accounts is: **vega123**")
    if st.button("Login"):
        user = authenticate_user(conn, username, password)
        if not user:
            st.error("Invalid credentials or inactive account.")
            return
        st.session_state["current_user"] = user
        if user["must_change_password"]:
            st.session_state["must_set_password"] = True
        st.rerun()

def first_password_setup(conn):
    user = st.session_state.get("current_user")
    st.warning("First time login detected. Set a new password to continue.")
    p1 = st.text_input("New password", type="password")
    p2 = st.text_input("Confirm password", type="password")
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
    if role == "IT Manager": return ["Overview", "Ticket Operations", "NAS Monitoring", "Reports", "Task Center", "Admin Tools", "AVP Dashboard"]
    if role == "IT AM": return ["Overview", "Ticket Operations", "NAS Monitoring", "Reports", "Task Center"]
    if role == "AVP": return ["Overview", "AVP Dashboard", "Reports", "Task Center"]
    return ["Overview", "Ticket Operations", "NAS Monitoring", "Task Center"]

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

def render_dashboard(conn):
    user = st.session_state.get("current_user", {})
    role = user.get("role", "IT Executive")
    display_name = user.get("display_name", "Guest")
    df_tickets = prepare_ticket_view(load_tickets())
    df_nas = load_nas_data()
    st.sidebar.markdown(f"👤 **{display_name}** ({role})")
    if st.sidebar.button("Logout"):
        st.session_state["current_user"] = None
        st.session_state["must_set_password"] = False
        st.rerun()
    allowed_pages = get_role_pages(role)
    st.sidebar.markdown("---")
    site_filter = st.sidebar.selectbox("Site", ["All"] + OFFICIAL_LOCATIONS)
    status_filter = st.sidebar.selectbox("Ticket Status", ["All"] + STATUS_OPTIONS)
    tech_filter = st.sidebar.selectbox("Technician", ["All"] + list(TECH_MAP.keys()))
    server_filter = st.sidebar.selectbox("NAS Server", ["All"] + SERVER_NAMES)
    st.sidebar.markdown("---")
    page = st.sidebar.radio("Navigation", allowed_pages)
    st.sidebar.markdown("---")
    if db_connected:
        st.sidebar.success("Supabase cloud connected")
    else:
        st.sidebar.warning("Session sandbox mode active")
    df_ticket_filtered = filtered_tickets(df_tickets, site_filter, status_filter, tech_filter)
    df_nas_filtered = filtered_nas(df_nas, server_filter)
    st.markdown("<div class='app-banner'><div class='app-title'>🛠️ Vega & Knitpro IT Command Suite</div><div class='app-subtitle'>Single-window support operations, NAS monitoring, reporting, tasking, and infrastructure analytics</div></div>", unsafe_allow_html=True)
    if page == "Overview":
        st.subheader("Operations Overview")
        total_tickets = len(df_ticket_filtered)
        resolved_tickets = len(df_ticket_filtered[df_ticket_filtered["status"] == "Resolved"])
        open_tickets = len(df_ticket_filtered[df_ticket_filtered["status"].isin(["Open", "In Progress"])])
        hold_tickets = len(df_ticket_filtered[df_ticket_filtered["status"] == "On Hold - User Busy"])
        resolved_df = df_ticket_filtered[(df_ticket_filtered["status"] == "Resolved") & (df_ticket_filtered["resolution_time"] > 0)]
        avg_res_time = int(resolved_df["resolution_time"].mean()) if not resolved_df.empty else 0
        nas_failures = int((df_nas_filtered["status"] == "Failed").sum()) if not df_nas_filtered.empty else 0
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: render_glass_card("Total Tickets", total_tickets, "Current filter", "--info")
        with c2: render_glass_card("Open Backlog", open_tickets, "Open + In Progress", "--accent")
        with c3: render_glass_card("Resolved", resolved_tickets, "Closed tickets", "--success")
        with c4: render_glass_card("On Hold", hold_tickets, "User busy", "--warning")
        with c5: render_glass_card("Avg Resolution", f"{avg_res_time} min", "Resolved only", "--info")
        if nas_failures > 0:
            st.error(f"Critical NAS alerts: {nas_failures} failed backup entries in current filter.")
        else:
            st.success("No NAS failure alert in the current filtered view.")
        ch1, ch2 = st.columns(2)
        with ch1:
            st.markdown("### Ticket Volume by Category")
            if not df_ticket_filtered.empty:
                cat_df = df_ticket_filtered["category"].value_counts().reset_index(); cat_df.columns = ["category", "count"]
                st.altair_chart(build_bar_chart(cat_df, "category:N", "count:Q", "#ef4444"), use_container_width=True)
        with ch2:
            st.markdown("### Ticket Volume by Location")
            if not df_ticket_filtered.empty:
                loc_df = df_ticket_filtered["location"].value_counts().reset_index(); loc_df.columns = ["location", "count"]
                st.altair_chart(build_bar_chart(loc_df, "location:N", "count:Q", "#3b82f6"), use_container_width=True)
        ch3, ch4 = st.columns(2)
        with ch3:
            st.markdown("### Technician Load")
            if not df_ticket_filtered.empty:
                tech_df = df_ticket_filtered["attended_by"].value_counts().reset_index(); tech_df.columns = ["attended_by", "count"]
                st.altair_chart(build_bar_chart(tech_df, "attended_by:N", "count:Q", "#22c55e"), use_container_width=True)
        with ch4:
            st.markdown("### NAS Storage Trend")
            trend_df = separate_nas_series(df_nas_filtered)
            if not trend_df.empty:
                if server_filter == "All":
                    chart = alt.Chart(trend_df).mark_line(point=True, strokeWidth=3).encode(x=alt.X("date:T", title=None), y=alt.Y("storage_used:Q", title=None), color=alt.Color("server_name:N", title="Server"), tooltip=["date:T", "server_name:N", "storage_used:Q", "status:N"]).properties(height=280)
                    st.altair_chart(chart, use_container_width=True)
                else:
                    trend_df = trend_df.sort_values("date"); trend_df["date_label"] = trend_df["date"].dt.strftime("%Y-%m-%d")
                    st.altair_chart(build_line_chart(trend_df, "date_label:N", "storage_used:Q", "#f59e0b"), use_container_width=True)
        st.markdown("### Recent Ticket Activity")
        recent = df_ticket_filtered.sort_values("id", ascending=False).head(8).copy() if not df_ticket_filtered.empty else pd.DataFrame()
        if not recent.empty:
            render_status_table(recent, ["System Ticket ID", "date", "user_name", "department", "location", "category", "attended_by", "status", "resolution_time"], compact=True)
        else:
            st.info("No ticket data available for the selected filters.")
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
                complaint_desc = st.text_area("Complaint Description", height=110)
                tech_remarks = st.text_area("Technician Remarks", height=90)
                c1, c2 = st.columns(2)
                start_input = c1.time_input("Start Time", value=time(datetime.now().hour, datetime.now().minute))
                close_input = c2.time_input("Close Time", value=time(datetime.now().hour, datetime.now().minute))
                submitted = st.form_submit_button("Submit Ticket", use_container_width=True)
                if submitted:
                    if not user_name.strip() or not department.strip() or not complaint_desc.strip():
                        st.error("Please fill all required fields.")
                    else:
                        category = auto_categorize(complaint_desc)
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
        st.subheader("Advanced Reports & Analytics Portal")
        tab1, tab2, tab3 = st.tabs(["Ticket Activity Logs", "NAS Performance Deltas", "Excel Export"])
        with tab1:
            if df_ticket_filtered.empty: st.info("No ticket records available.")
            else:
                export_df = df_ticket_filtered.copy(); export_df["date_parsed"] = pd.to_datetime(export_df["date"], errors="coerce"); export_df = export_df.dropna(subset=["date_parsed"])
                export_df["Month"] = export_df["date_parsed"].dt.strftime("%Y-%m"); export_df["WeekLabel"] = export_df["date_parsed"].dt.strftime("%Y-W") + export_df["date_parsed"].dt.isocalendar().week.astype(str)
                st.download_button("Download Master Ticket Log (.csv)", export_df.drop(columns=["date_parsed"], errors="ignore").to_csv(index=False).encode("utf-8"), file_name="it_master_production_log.csv", mime="text/csv")
                r1, r2, r3, r4 = st.tabs(["Monthly", "Weekly", "Technician", "Location"])
                with r1:
                    st.dataframe(export_df.groupby("Month", as_index=False).agg(Tickets=("id", "size"), Resolved=("status", lambda s: (s == "Resolved").sum())), use_container_width=True)
                with r2:
                    st.dataframe(export_df.groupby("WeekLabel", as_index=False).agg(Tickets=("id", "size"), Resolved=("status", lambda s: (s == "Resolved").sum())), use_container_width=True)
                with r3:
                    st.dataframe(export_df.groupby("attended_by", as_index=False).agg(Tickets=("id", "size"), Resolved=("status", lambda s: (s == "Resolved").sum())), use_container_width=True)
                with r4:
                    st.dataframe(export_df.groupby("location", as_index=False).agg(Tickets=("id", "size"), Resolved=("status", lambda s: (s == "Resolved").sum())), use_container_width=True)
        with tab2:
            st.markdown("### Interactive Storage Growth Delta Heatmap")
            nas_changes = compute_nas_changes(df_nas_filtered)
            if not nas_changes.empty:
                nas_changes["date_str"] = nas_changes["date"].dt.strftime("%Y-%m-%d")
                heatmap = alt.Chart(nas_changes).mark_rect().encode(
                    x=alt.X("date_str:O", title="Date"),
                    y=alt.Y("server_name:O", title="Server Name"),
                    color=alt.Color("delta_gb:Q", title="Storage Delta (GB)"),
                    tooltip=[
                        alt.Tooltip("date_str:O", title="Date"),
                        alt.Tooltip("server_name:N", title="Server"),
                        alt.Tooltip("storage_used:Q", title="Storage Used (GB)", format=".4f"),
                        alt.Tooltip("delta_gb:Q", title="Delta (GB)", format=".4f"),
                        alt.Tooltip("status:N", title="Status"),
                    ],
                ).properties(height=280)
                st.altair_chart(heatmap, use_container_width=True)
                nas_master, nas_monthly, nas_serverwise = build_nas_reports(df_nas_filtered)
                st.markdown("### NAS Master Delta Table"); st.dataframe(nas_master, use_container_width=True)
                st.markdown("### NAS Monthly Summary"); st.dataframe(nas_monthly, use_container_width=True)
                st.markdown("### NAS Server Summary"); st.dataframe(nas_serverwise, use_container_width=True)
            else: st.info("No sufficient historical NAS data to calculate deltas.")
        with tab3:
            try:
                excel_bytes = build_excel_report(df_ticket_filtered.drop(columns=["date_parsed"], errors="ignore"), df_nas_filtered)
                st.download_button(
                    "📥 Download Multi-Tab Formatted Excel Report",
                    data=excel_bytes,
                    file_name="IT_Operations_Master_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            except ModuleNotFoundError:
                st.warning("Excel export is unavailable because openpyxl is not installed in this environment.")
            except Exception as e:
                st.error(f"Excel export failed: {e}")
    elif page == "Task Center":
        st.subheader("Operational Tasks & Assignments")
        t1, t2, t3, t4 = st.tabs(["Task Board", "Create Task", "Comments", "Notifications"])
        with t1:
            tasks_df = pd.read_sql_query("SELECT * FROM tasks ORDER BY id DESC", conn)
            st.dataframe(tasks_df, use_container_width=True)
            if not tasks_df.empty:
                task_options = {f"Task #{row['id']} | {row['title']} | {row['status']}": int(row['id']) for _, row in tasks_df.iterrows()}
                selected_task_label = st.selectbox("Select task to update", list(task_options.keys()))
                task_id = task_options[selected_task_label]
                row = tasks_df[tasks_df["id"] == task_id].iloc[0]
                with st.form(f"update_task_{task_id}"):
                    c1, c2 = st.columns(2)
                    opts = ["Open", "In Progress", "Completed", "Blocked"]
                    new_status = c1.selectbox("Task Status", opts, index=opts.index(row["status"]) if row["status"] in opts else 0)
                    new_progress = c2.slider("Progress %", 0, 100, int(row["progress"]) if pd.notna(row["progress"]) else 0)
                    new_vendor_status = st.text_input("Vendor Status", value=str(row.get("vendor_status", "") or ""))
                    new_vendor_remark = st.text_area("Vendor Remark", value=str(row.get("vendor_remark", "") or ""))
                    if st.form_submit_button("Update Task"):
                        update_task(conn, task_id, {"status": new_status, "progress": new_progress, "vendor_status": new_vendor_status.strip(), "vendor_remark": new_vendor_remark.strip()})
                        st.success("Task updated successfully."); st.rerun()
        with t2:
            with st.form("create_task_form", clear_on_submit=True):
                title = st.text_input("Task Title")
                description = st.text_area("Description", height=100)
                d1, d2 = st.columns(2)
                assigned_to = d1.selectbox("Assign To", list(TECH_MAP.keys()))
                priority = d2.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
                d3, d4 = st.columns(2)
                due_date = d3.date_input("Due Date", value=datetime.now().date())
                vendor_flag = d4.checkbox("Vendor Involved")
                if st.form_submit_button("Create Task"):
                    create_task(conn, {"title": title.strip(), "description": description.strip(), "assigned_by": display_name, "assigned_to": assigned_to, "priority": priority, "status": "Open", "progress": 0, "due_date": due_date.strftime("%Y-%m-%d"), "vendor_flag": int(vendor_flag), "vendor_status": "Pending from Vendor" if vendor_flag else "", "vendor_remark": "", "reminder_date": due_date.strftime("%Y-%m-%d")})
                    add_notification(conn, assigned_to.lower(), f"New task assigned by {display_name}: {title.strip()}")
                    st.success("Task created successfully."); st.rerun()
        with t3:
            tasks_df = pd.read_sql_query("SELECT id, title FROM tasks ORDER BY id DESC", conn)
            if tasks_df.empty: st.info("No tasks available for comments.")
            else:
                task_map = {f"Task #{row['id']} | {row['title']}": int(row['id']) for _, row in tasks_df.iterrows()}
                selected = st.selectbox("Choose task", list(task_map.keys()), key="task_comment_select")
                selected_task_id = task_map[selected]
                comments_df = pd.read_sql_query(f"SELECT * FROM task_comments WHERE task_id={selected_task_id} ORDER BY id DESC", conn)
                st.dataframe(comments_df, use_container_width=True)
                with st.form("comment_form", clear_on_submit=True):
                    comment = st.text_area("Add Comment", height=90)
                    if st.form_submit_button("Save Comment"):
                        add_task_comment(conn, selected_task_id, comment.strip(), display_name)
                        st.success("Comment added."); st.rerun()
        with t4:
            notif_df = pd.read_sql_query("SELECT * FROM notifications ORDER BY id DESC", conn)
            st.dataframe(notif_df, use_container_width=True)
            unread = notif_df[notif_df["is_read"] == 0] if not notif_df.empty else pd.DataFrame()
            if not unread.empty:
                mark_id = st.selectbox("Mark notification as read", unread["id"].tolist())
                if st.button("Mark Read"):
                    mark_notification_read(conn, int(mark_id))
                    st.success("Notification updated."); st.rerun()
    elif page == "Admin Tools":
        st.subheader("Admin Tools")
        t1, t2, t3 = st.tabs(["Recurring Issues", "Vendor Follow-up", "System Snapshot"])
        with t1:
            if df_tickets.empty: st.info("No ticket data available.")
            else: st.dataframe(df_tickets.groupby(["category", "location"], as_index=False).agg(Tickets=("id", "size")).sort_values("Tickets", ascending=False), use_container_width=True)
        with t2:
            st.dataframe(pd.read_sql_query("SELECT * FROM vendor_followups ORDER BY id DESC", conn), use_container_width=True)
        with t3:
            st.markdown("### Users")
            st.dataframe(pd.read_sql_query("SELECT username, display_name, role, active, must_change_password FROM users ORDER BY username", conn), use_container_width=True)
            st.markdown("### Tasks Snapshot")
            st.dataframe(pd.read_sql_query("SELECT * FROM tasks ORDER BY id DESC", conn), use_container_width=True)
            st.markdown("### Database Mode")
            st.write("Supabase connected" if db_connected else "Local session mode")
    elif page == "AVP Dashboard":
        st.subheader("Executive Command Suite")
        tasks_df = pd.read_sql_query("SELECT * FROM tasks", conn)
        open_tasks = tasks_df[tasks_df["status"] != "Completed"] if not tasks_df.empty else pd.DataFrame()
        critical_tasks = tasks_df[tasks_df["priority"].isin(["Critical", "High"])] if not tasks_df.empty else pd.DataFrame()
        a1, a2, a3 = st.columns(3)
        a1.metric("Total Active Tasks", len(open_tasks))
        a2.metric("Critical/High Tasks", len(critical_tasks))
        a3.metric("Open Tickets", len(df_tickets[df_tickets["status"] != "Resolved"]))
        st.markdown("### High Priority Tasks")
        if critical_tasks.empty:
            st.success("All critical high-priority tasks are currently clear.")
        else:
            st.dataframe(critical_tasks[["id", "title", "assigned_to", "priority", "status", "due_date"]], use_container_width=True)
        st.markdown("### Ticket Status Summary")
        if not df_tickets.empty: st.dataframe(df_tickets.groupby("status", as_index=False).agg(Tickets=("id", "size")), use_container_width=True)

def app_startup():
    conn = None
    try:
        conn = get_db_connection()
        init_support_data(conn)
        bootstrap_auth_gate(conn)
        render_dashboard(conn)
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    app_startup()
