import io
from datetime import datetime

import pandas as pd
import streamlit as st
from supabase import create_client

# =========================================================================
# PAGE CONFIGURATION & STYLING
# =========================================================================
st.set_page_config(page_title="Vega & Knitpro IT Ticketing", layout="wide")

st.markdown(
    """
<style>
    .ai-card {
        background-color: #1e293b;
        border-left: 5px solid #ef4444;
        padding: 18px;
        border-radius: 8px;
        margin: 12px 0;
        color: #f8fafc;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
    }
    .ai-title {
        color: #f87171;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 10px;
    }
    .step-item {
        margin-bottom: 8px;
        font-size: 0.95rem;
        line-height: 1.45;
    }
    .kpi-box {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
    }
    .kpi-label {
        color: #94a3b8;
        font-size: 0.88rem;
        margin-bottom: 6px;
    }
    .kpi-value {
        color: #f8fafc;
        font-size: 1.7rem;
        font-weight: 700;
        margin: 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 6px 6px 0 0;
        padding: 10px 18px;
        color: #cbd5e1;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ef4444 !important;
        color: white !important;
    }
    div.stButton > button:first-child {
        background-color: #ef4444;
        color: white;
        border: none;
    }
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================================
# BRANDING
# =========================================================================
logo_col1, logo_col2, _, _ = st.columns([1, 1, 2, 2])
with logo_col1:
    try:
        st.image("vega_logo.png", width=150)
    except Exception:
        st.caption("🔺 [Vega Logo]")
with logo_col2:
    try:
        st.image("knitpro_logo.png", width=150)
    except Exception:
        st.caption("🔺 [Knitpro Logo]")

st.title("🛠️ Vega & Knitpro IT Ticketing & Analysis System")
st.markdown("---")

# =========================================================================
# DATABASE
# =========================================================================
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

st.sidebar.header("⚙️ Node Connection Frame")
if db_connected:
    st.sidebar.success("⚡ Live Cloud Node: Connected")
else:
    st.sidebar.warning("⚠️ Session Sandbox Mode")

# =========================================================================
# CONSTANTS
# =========================================================================
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
            "Check if the camera POE switch port light is blinking. If not, swap ports or check the patch cord.",
            "Ping the camera IP address via CMD to check network dropouts.",
            "If NVR shows 'No Video', check if the camera channel needs a firmware restart or re-login.",
        ],
        "Hindi": [
            "जांचें कि कैमरा POE स्विच पोर्ट की लाइट ब्लिंक कर रही है या नहीं। यदि नहीं, तो पोर्ट बदलें या पैच कॉर्ड चेक करें।",
            "नेटवर्क DROP-OUT चेक करने के लिए CMD के माध्यम से कैमरा IP एड्रेस को पिंग करें।",
            "यदि NVR 'No Video' दिखाता है, तो जांचें कि कैमरा चैनल को फर्मवेयर रीस्टार्ट या री-लॉगिन की आवश्यकता है या नहीं।",
        ],
    },
    "Laptop/Hardware": {
        "title_en": "💻 AI Endpoint Hardware Diagnostics",
        "title_hi": "💻 एआई एंडपॉइंट हार्डवेयर डायग्नोस्टिक्स",
        "English": [
            "No Power: Perform a hard reset by disconnecting power, isolating battery if applicable, and holding power for 30 seconds.",
            "Display Black: Connect to an external monitor to isolate LCD versus motherboard failure.",
            "Keyboard/Touchpad: Inspect Device Manager and reinstall relevant chipset or I2C drivers.",
        ],
        "Hindi": [
            "पावर नहीं आ रही: पावर डिस्कनेक्ट करें, यदि संभव हो तो बैटरी अलग करें और 30 सेकंड तक पावर बटन दबाकर हार्ड रीसेट करें।",
            "डिस्प्ले ब्लैक है: बाहरी मॉनिटर से कनेक्ट करके LCD और मदरबोर्ड समस्या को अलग करें।",
            "कीबोर्ड/टचपैड: डिवाइस मैनेजर की जांच करें और संबंधित चिपसेट या I2C ड्राइवर पुनः इंस्टॉल करें।",
        ],
    },
    "Email/Outlook": {
        "title_en": "📧 AI Communication Layer Diagnostics",
        "title_hi": "📧 एआई कम्यूनिकेशन लेयर डायग्नोस्टिक्स",
        "English": [
            "Run outlook.exe /safe to check whether an add-in is causing instability.",
            "Check PST or OST file size and compact the file if it is large.",
            "Clear cached credentials in Windows Credential Manager if password prompts repeat.",
        ],
        "Hindi": [
            "यह जांचने के लिए outlook.exe /safe चलाएं कि कोई add-in समस्या पैदा कर रहा है या नहीं।",
            "PST या OST फ़ाइल का आकार जांचें और आवश्यकता होने पर उसे compact करें।",
            "यदि पासवर्ड बार-बार पूछा जा रहा है, तो Windows Credential Manager में cached credentials साफ करें।",
        ],
    },
    "Printer": {
        "title_en": "🖨️ AI Print Management Diagnostics",
        "title_hi": "🖨️ एआई प्रिंट मैनेजमेंट डायग्नोस्टिक्स",
        "English": [
            "Check Printer Properties and review the configured port and SNMP status option.",
            "Restart the Print Spooler service and clear the PRINTERS directory if jobs are stuck.",
            "Inspect toner, cartridge, rollers, or scanner glass if print quality is poor.",
        ],
        "Hindi": [
            "Printer Properties में configured port और SNMP status option जांचें।",
            "यदि jobs अटकी हैं तो Print Spooler service restart करें और PRINTERS directory साफ करें।",
            "यदि print quality खराब है तो toner, cartridge, rollers या scanner glass जांचें।",
        ],
    },
    "SAP": {
        "title_en": "🏢 AI Enterprise ERP Diagnostics",
        "title_hi": "🏢 एआई एंटरप्राइज ईआरपी डायग्नोस्टिक्स",
        "English": [
            "Verify saplogon configuration and network path or VPN reachability.",
            "Check for locked or hung sessions using the appropriate SAP transaction.",
            "Clear local SAP cache or repair SAP GUI if the client is unstable.",
        ],
        "Hindi": [
            "saplogon configuration और network path या VPN connectivity सत्यापित करें।",
            "उचित SAP transaction से locked या hung sessions जांचें।",
            "यदि client unstable है तो local SAP cache साफ करें या SAP GUI repair करें।",
        ],
    },
    "Network": {
        "title_en": "🌐 AI Network Routing Diagnostics",
        "title_hi": "🌐 एआई नेटवर्क राउटिंग डायग्नोस्टिक्स",
        "English": [
            "Reset Winsock and inspect the network adapter driver if Wi-Fi drops frequently.",
            "Release and renew IP configuration if an address conflict is suspected.",
            "Confirm whether the user is on the intended SSID and frequency band.",
        ],
        "Hindi": [
            "यदि Wi-Fi बार-बार कटता है तो Winsock reset करें और network adapter driver जांचें।",
            "यदि address conflict हो तो IP configuration release और renew करें।",
            "पुष्टि करें कि user सही SSID और frequency band पर है।",
        ],
    },
    "Server/UPS": {
        "title_en": "🖥️ Server & Power Infrastructure Diagnostics",
        "title_hi": "🖥️ सर्वर और पावर इन्फ्रास्ट्रक्चर डायग्नोस्टिक्स",
        "English": [
            "Check UPS load and power input if alarms or beeps are active.",
            "Verify server room temperature and rack airflow path.",
            "Review DNS and authentication dependencies if domain logins fail.",
        ],
        "Hindi": [
            "यदि alarms या beeps सक्रिय हैं तो UPS load और power input जांचें।",
            "Server room temperature और rack airflow path सत्यापित करें।",
            "यदि domain logins fail हो रहे हों तो DNS और authentication dependencies जांचें।",
        ],
    },
}

# =========================================================================
# SESSION SANDBOX FALLBACKS
# =========================================================================
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
        ]
    )

if "local_nas" not in st.session_state:
    st.session_state.local_nas = pd.DataFrame(
        [
            {"date": "2026-07-11", "server_name": "HRI", "status": "Success", "storage_used": 450.0, "remarks": "Daily backup completed."},
            {"date": "2026-07-12", "server_name": "HRI", "status": "Success", "storage_used": 452.6, "remarks": "Daily backup completed."},
            {"date": "2026-07-13", "server_name": "HRI", "status": "Failed", "storage_used": 452.6, "remarks": "Handshake timeout."},
            {"date": "2026-07-11", "server_name": "Vega", "status": "Success", "storage_used": 890.0, "remarks": "Weekly image backup completed."},
            {"date": "2026-07-12", "server_name": "Vega", "status": "Warning / Partial", "storage_used": 895.5, "remarks": "Profile sync partial."},
            {"date": "2026-07-13", "server_name": "Sery", "status": "Success", "storage_used": 310.0, "remarks": "Incremental snapshot success."},
            {"date": "2026-07-13", "server_name": "Rise", "status": "Success", "storage_used": 220.0, "remarks": "Replication completed."},
        ]
    )

# =========================================================================
# HELPERS
# =========================================================================
def format_ticket_number(ticket_id, location_str):
    try:
        clean_id = int(float(ticket_id))
        if pd.isna(location_str) or not location_str:
            return f"IT-2026-{clean_id:04d}"
        loc = str(location_str).lower()
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
    if any(k in text for k in ["laptop", "desktop", "keyboard", "touchpad", "battery", "hinge", "screen", "power", "hardware"]):
        return "Laptop/Hardware"
    if any(k in text for k in ["outlook", "email", "mail", "pst"]):
        return "Email/Outlook"
    if any(k in text for k in ["printer", "scanner", "cartridge", "print"]):
        return "Printer"
    if any(k in text for k in ["sap", "erp"]):
        return "SAP"
    if any(k in text for k in ["network", "wifi", "internet", "vpn", "ping", "ip", "firewall", "switch", "router"]):
        return "Network"
    if any(k in text for k in ["server", "ups", "rack", "backup", "domain", "dns"]):
        return "Server/UPS"
    return "Other"


def get_next_ticket_id(df):
    if df.empty or "id" not in df.columns:
        return 1
    return int(pd.to_numeric(df["id"], errors="coerce").fillna(0).max()) + 1


def normalize_ticket_df(df):
    expected = [
        "id",
        "date",
        "user_name",
        "department",
        "complaint",
        "location",
        "attended_by",
        "status",
        "category",
        "start_time",
        "close_time",
        "resolution_time",
        "remarks",
    ]
    if df is None or df.empty:
        return pd.DataFrame(columns=expected)
    out = df.copy()
    for col in expected:
        if col not in out.columns:
            out[col] = None
    out["id"] = pd.to_numeric(out["id"], errors="coerce").fillna(0).astype(int)
    out["resolution_time"] = pd.to_numeric(out["resolution_time"], errors="coerce").fillna(0).astype(int)
    out["remarks"] = out["remarks"].fillna("")
    return out[expected]


def normalize_nas_df(df):
    expected = ["date", "server_name", "status", "storage_used", "remarks"]
    if df is None or df.empty:
        return pd.DataFrame(columns=expected)
    out = df.copy()
    for col in expected:
        if col not in out.columns:
            out[col] = None
    out["storage_used"] = pd.to_numeric(out["storage_used"], errors="coerce").fillna(0.0)
    out["remarks"] = out["remarks"].fillna("")
    return out[expected]


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
        return int(response.data[0]["id"])
    current = st.session_state.local_tickets.copy()
    new_row = dict(new_row)
    new_row["id"] = get_next_ticket_id(current)
    st.session_state.local_tickets = pd.concat([current, pd.DataFrame([new_row])], ignore_index=True)
    return int(new_row["id"])


def update_ticket(ticket_id, payload):
    if db_connected:
        supabase_client.table("tickets").update(payload).eq("id", int(ticket_id)).execute()
        return
    idx = st.session_state.local_tickets[st.session_state.local_tickets["id"] == int(ticket_id)].index
    for key, value in payload.items():
        st.session_state.local_tickets.loc[idx, key] = value


def save_nas_log(new_row):
    if db_connected:
        supabase_client.table("nas_backups").insert(new_row).execute()
        return
    st.session_state.local_nas = pd.concat([st.session_state.local_nas, pd.DataFrame([new_row])], ignore_index=True)


# =========================================================================
# DATA LOAD
# =========================================================================
df_live = load_tickets()
df_nas = load_nas_data()

# =========================================================================
# SESSION STATE INIT
# =========================================================================
if "ticket_submitted" not in st.session_state:
    st.session_state.ticket_submitted = False
if "last_ticket_info" not in st.session_state:
    st.session_state.last_ticket_info = {}
if "form_default_start" not in st.session_state:
    st.session_state.form_default_start = datetime.now().time()
if "form_default_close" not in st.session_state:
    st.session_state.form_default_close = datetime.now().time()

# =========================================================================
# TABS
# =========================================================================
tab_log, tab_view, tab_analysis, tab_monthly, tab_nas, tab_recurring = st.tabs(
    [
        "🆕 Log New Ticket",
        "📑 View & Edit Tickets",
        "📊 Analysis Dashboard",
        "📥 Reporting Center",
        "💾 NAS Backup Monitoring",
        "🔄 Recurring Users",
    ]
)

# =========================================================================
# TAB 1: LOG NEW TICKET
# =========================================================================
with tab_log:
    st.header("📋 Log New Operations Ticket")

    if st.session_state.ticket_submitted:
        info = st.session_state.last_ticket_info
        st.success("🎉 TICKET RECORD SAVED SUCCESSFULLY")
        with st.container(border=True):
            st.markdown(f"**Generated ID:** `{format_ticket_number(info['id'], info['loc'])}`")
            st.markdown(f"**Date:** {info['date']}  |  **Category:** {info['category']}")
            st.markdown(f"**User:** {info['user']} ({info['dept']})  |  **Technician:** {info['tech']}")
            st.markdown(f"**Location:** {info['loc']}  |  **Status:** {info['status']}")
            st.markdown(f"**Resolution Time:** {info['duration']} mins")
            st.markdown(f"**Remarks:** {info['remarks'] or '-'}")
        if st.button("Log Another Ticket", type="primary"):
            st.session_state.ticket_submitted = False
            st.session_state.form_default_start = datetime.now().time()
            st.session_state.form_default_close = datetime.now().time()
            st.rerun()
    else:
        existing_users = sorted(df_live["user_name"].dropna().astype(str).unique().tolist()) if not df_live.empty else []
        selected_user = st.selectbox("💡 Search Existing User Name to Auto-Fill Details", ["New User / Type Below"] + existing_users)

        default_user_name, default_dept, default_loc = "", "", ""
        if selected_user != "New User / Type Below" and not df_live.empty:
            hist = df_live[df_live["user_name"] == selected_user].sort_values(by="id", ascending=False)
            if not hist.empty:
                default_user_name = selected_user
                default_dept = str(hist.iloc[0].get("department", ""))
                default_loc = str(hist.iloc[0].get("location", ""))

        form_col, ai_col = st.columns([1.1, 0.9], gap="large")

        with form_col:
            with st.form("ticket_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                user_name = c1.text_input("User Name *", value=default_user_name)
                attended_by = c2.selectbox("Attended By", list(TECH_MAP.keys()))

                c3, c4 = st.columns(2)
                department = c3.text_input("Department *", value=default_dept)
                status = c4.selectbox("Initial Status", STATUS_OPTIONS, index=0)

                default_index = OFFICIAL_LOCATIONS.index(default_loc) if default_loc in OFFICIAL_LOCATIONS else 0
                location = st.selectbox("Location / Sector *", OFFICIAL_LOCATIONS, index=default_index)

                complaint_desc = st.text_area("Complaint Description *", height=100)
                tech_remarks = st.text_area("Technician Operational Remarks", height=90)

                t1, t2 = st.columns(2)
                custom_start = t1.time_input("Start Time", value=st.session_state.form_default_start, key="widget_start_time")
                custom_close = t2.time_input("Resolve Time", value=st.session_state.form_default_close, key="widget_close_time")

                submit_btn = st.form_submit_button("Submit Ticket")

                if submit_btn:
                    if not user_name or not department or not complaint_desc:
                        st.error("❌ Please populate all required fields (*).")
                    else:
                        cat_final = auto_categorize(complaint_desc)
                        formatted_date = datetime.now().strftime("%Y-%m-%d")

                        if status in ["Open", "On Hold - User Busy"]:
                            start_val, close_val, duration_mins = None, None, 0
                        else:
                            start_val = f"{formatted_date} {custom_start.strftime('%H:%M:%S')}"
                            close_val = f"{formatted_date} {custom_close.strftime('%H:%M:%S')}" if status == "Resolved" else None
                            if status == "Resolved":
                                duration_mins = max(
                                    1,
                                    int(
                                        (
                                            datetime.combine(datetime.now().date(), custom_close)
                                            - datetime.combine(datetime.now().date(), custom_start)
                                        ).total_seconds()
                                        / 60
                                    ),
                                )
                            else:
                                duration_mins = 0

                        new_row = {
                            "date": formatted_date,
                            "user_name": user_name,
                            "department": department,
                            "complaint": complaint_desc,
                            "location": location,
                            "attended_by": attended_by,
                            "status": status,
                            "category": cat_final,
                            "remarks": tech_remarks,
                            "start_time": start_val,
                            "close_time": close_val,
                            "resolution_time": duration_mins,
                        }

                        try:
                            new_id = save_ticket(new_row)
                            st.session_state.last_ticket_info = {
                                "id": new_id,
                                "date": formatted_date,
                                "category": cat_final,
                                "user": user_name,
                                "dept": department,
                                "tech": attended_by,
                                "loc": location,
                                "status": status,
                                "duration": duration_mins,
                                "remarks": tech_remarks,
                            }
                            st.session_state.ticket_submitted = True
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Insertion Error: {e}")

        with ai_col:
            st.subheader("🧠 AI Copilot Diagnostics")
            ai_input = st.text_area(
                "Type complaint scenario details to extract rapid triage steps:",
                height=140,
                placeholder="e.g., Printer is showing offline state...",
            )
            lang_choice = st.radio("Output Language Target", ["English", "हिंदी"], index=0, horizontal=True)
            parse_btn = st.button("💡 AI Assistance", use_container_width=True)

            if parse_btn:
                text_to_analyze = ai_input.strip()
                if text_to_analyze:
                    cat = auto_categorize(text_to_analyze)
                    if cat in AI_SUGGESTIONS:
                        details = AI_SUGGESTIONS[cat]
                        title = details["title_en"] if lang_choice == "English" else details["title_hi"]
                        steps = details["English"] if lang_choice == "English" else details["Hindi"]
                        steps_html = "".join([f"<div class='step-item'>🔹 {step}</div>" for step in steps])
                        st.markdown(f"<div class='ai-card'><div class='ai-title'>{title}</div>{steps_html}</div>", unsafe_allow_html=True)
                    else:
                        st.info("🔍 No specific category matched. Proceed with standard physical, network, and permission checks.")
                else:
                    st.warning("⚠️ Please provide complaint details first.")

# =========================================================================
# TAB 2: VIEW & EDIT
# =========================================================================
with tab_view:
    st.subheader("📋 Master Ticket Queue")
    if df_live.empty:
        st.info("No active tickets found.")
    else:
        f1, f2, f3 = st.columns(3)
        with f1:
            sel_status = st.multiselect("Filter by Status", STATUS_OPTIONS, default=STATUS_OPTIONS)
        with f2:
            sel_location = st.multiselect("Filter by Location", OFFICIAL_LOCATIONS, default=OFFICIAL_LOCATIONS)
        with f3:
            available_cats = sorted(df_live["category"].dropna().astype(str).unique().tolist())
            sel_cat = st.multiselect("Filter by Category", available_cats, default=available_cats)

        df_display = df_live.copy()
        df_display["System Ticket ID"] = df_display.apply(lambda r: format_ticket_number(r["id"], r["location"]), axis=1)
        filtered_df = df_display[
            (df_display["status"].isin(sel_status))
            & (df_display["location"].isin(sel_location))
            & (df_display["category"].isin(sel_cat))
        ].sort_values(by="id", ascending=False)

        st.dataframe(
            filtered_df[
                [
                    "System Ticket ID",
                    "date",
                    "user_name",
                    "department",
                    "location",
                    "category",
                    "complaint",
                    "attended_by",
                    "status",
                    "resolution_time",
                    "remarks",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("---")
        st.subheader("🔄 Update / Close Existing Ticket")
        if filtered_df.empty:
            st.info("No tickets match the selected filters.")
        else:
            ticket_options = {
                f"{row['System Ticket ID']} — {row['user_name']} [{row['status']}]": int(row["id"])
                for _, row in filtered_df.iterrows()
            }
            selected_label = st.selectbox("🎯 Choose a ticket to modify", list(ticket_options.keys()))
            target_id = ticket_options[selected_label]
            ticket_data = df_display[df_display["id"] == target_id].iloc[0]

            with st.container(border=True):
                a, b, c = st.columns(3)
                a.markdown(f"**Target User:** {ticket_data['user_name']}")
                b.markdown(f"**Department:** {ticket_data['department']}")
                c.markdown(f"**Current Status:** `{ticket_data['status']}`")
                st.info(f"📝 **Original Complaint:** {ticket_data['complaint']}")

                with st.form(f"update_form_{target_id}"):
                    u1, u2 = st.columns(2)
                    with u1:
                        c_idx = STATUS_OPTIONS.index(ticket_data["status"]) if ticket_data["status"] in STATUS_OPTIONS else 0
                        new_status = st.selectbox("Modify Status", STATUS_OPTIONS, index=c_idx)
                        tech_list = list(TECH_MAP.keys())
                        t_idx = tech_list.index(ticket_data["attended_by"]) if ticket_data["attended_by"] in tech_list else 0
                        new_tech = st.selectbox("Reassign Technician", tech_list, index=t_idx)
                    with u2:
                        new_remarks = st.text_area("Update Resolution Remarks", value=str(ticket_data.get("remarks", "")))
                        duration_input = st.number_input(
                            "Resolution Duration (Minutes)",
                            min_value=0,
                            value=int(ticket_data["resolution_time"]) if pd.notna(ticket_data["resolution_time"]) else 0,
                        )

                    save_update_btn = st.form_submit_button("Save Changes & Sync Data")
                    if save_update_btn:
                        final_remarks = str(new_remarks)
                        if new_status == "On Hold - User Busy" and not final_remarks.strip():
                            final_remarks = "Technician reached user, but work was postponed due to business activity."
                        payload = {
                            "status": new_status,
                            "attended_by": new_tech,
                            "remarks": final_remarks,
                            "resolution_time": int(duration_input),
                        }
                        if new_status == "Resolved" and not ticket_data.get("close_time"):
                            payload["close_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        try:
                            update_ticket(target_id, payload)
                            st.success(f"⚡ Ticket synchronized to status: {new_status}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Update Sync Error: {e}")

# =========================================================================
# TAB 3: ANALYSIS DASHBOARD
# =========================================================================
with tab_analysis:
    st.subheader("📊 Analysis Dashboard")
    if df_live.empty:
        st.info("Log ticket entries to initialize the dashboard engine.")
    else:
        total_tickets = len(df_live)
        resolved_tickets = len(df_live[df_live["status"].astype(str).str.lower() == "resolved"])
        held_tickets = len(df_live[df_live["status"].astype(str).str.lower() == "on hold - user busy"])
        open_tickets = len(df_live[df_live["status"].astype(str).str.lower().isin(["open", "in progress"])])
        resolved_df = df_live[(df_live["status"].astype(str).str.lower() == "resolved") & (df_live["resolution_time"] > 0)]
        avg_res_time = int(resolved_df["resolution_time"].mean()) if not resolved_df.empty else 0
        resolution_rate = round((resolved_tickets / total_tickets) * 100, 1) if total_tickets else 0.0

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Logged Volume", total_tickets)
        k2.metric("Resolved Queries", resolved_tickets)
        k3.metric("On Hold", held_tickets)
        k4.metric("Active Backlog", open_tickets)
        k5.metric("Avg Resolution", f"{avg_res_time} mins")
        st.caption(f"Resolution efficiency: {resolution_rate}%")

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🧑‍💻 Technician Workload")
            st.bar_chart(df_live["attended_by"].value_counts())
        with c2:
            st.markdown("### 🗂️ Status Breakdown")
            st.bar_chart(df_live["status"].value_counts())

        c3, c4 = st.columns(2)
        with c3:
            st.markdown("### 📦 Tickets by Category")
            st.bar_chart(df_live["category"].value_counts())
        with c4:
            st.markdown("### 📍 Tickets by Location")
            st.bar_chart(df_live["location"].value_counts())

# =========================================================================
# TAB 4: REPORTING CENTER
# =========================================================================
with tab_monthly:
    st.header("📥 Reporting Center")
    if df_live.empty:
        st.info("No logs present for reporting.")
    else:
        df_export = df_live.copy()
        df_export["date_parsed"] = pd.to_datetime(df_export["date"], errors="coerce")
        df_export = df_export.dropna(subset=["date_parsed"])
        df_export["Month"] = df_export["date_parsed"].dt.strftime("%Y-%m (%B)")
        df_export["Week_of_Year"] = df_export["date_parsed"].dt.isocalendar().week.astype(str)
        df_export["Week_Label"] = df_export["date_parsed"].dt.strftime("%Y-W") + df_export["Week_of_Year"]
        df_export["System Ticket ID"] = df_export.apply(lambda r: format_ticket_number(r["id"], r["location"]), axis=1)

        full_csv = df_export.drop(columns=["date_parsed"], errors="ignore").to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Master Log Sheet (.CSV)", full_csv, "it_master_production_log.csv", "text/csv")

        st.markdown("---")
        exp_tab_month, exp_tab_week, exp_tab_tech, exp_tab_loc = st.tabs(
            ["📅 Monthly Logs", "📆 Weekly Logs", "🧑‍💻 Technician Logs", "🏢 Location Logs"]
        )

        with exp_tab_month:
            selected_month = st.selectbox("Select Target Month", sorted(df_export["Month"].unique().tolist(), reverse=True), key="m_sel")
            f_m_df = df_export[df_export["Month"] == selected_month].drop(columns=["date_parsed", "Month", "Week_of_Year", "Week_Label"], errors="ignore")
            st.dataframe(f_m_df, use_container_width=True, hide_index=True)
            st.download_button(f"📥 Download {selected_month} Logs (.CSV)", f_m_df.to_csv(index=False).encode("utf-8"), f"monthly_{selected_month}.csv", "text/csv")

        with exp_tab_week:
            selected_week = st.selectbox("Select Target Week", sorted(df_export["Week_Label"].unique().tolist(), reverse=True), key="w_sel")
            f_w_df = df_export[df_export["Week_Label"] == selected_week].drop(columns=["date_parsed", "Month", "Week_of_Year", "Week_Label"], errors="ignore")
            st.dataframe(f_w_df, use_container_width=True, hide_index=True)
            st.download_button(f"📥 Download {selected_week} Logs (.CSV)", f_w_df.to_csv(index=False).encode("utf-8"), f"weekly_{selected_week}.csv", "text/csv")

        with exp_tab_tech:
            selected_tech = st.selectbox("Select Technician", sorted(df_export["attended_by"].dropna().astype(str).unique().tolist()), key="t_sel")
            f_t_df = df_export[df_export["attended_by"] == selected_tech].drop(columns=["date_parsed", "Month", "Week_of_Year", "Week_Label"], errors="ignore")
            st.dataframe(f_t_df, use_container_width=True, hide_index=True)
            st.download_button(f"📥 Download {selected_tech} Logs (.CSV)", f_t_df.to_csv(index=False).encode("utf-8"), f"tech_{selected_tech.lower()}.csv", "text/csv")

        with exp_tab_loc:
            selected_loc = st.selectbox("Select Site Location", sorted(df_export["location"].dropna().astype(str).unique().tolist()), key="l_sel")
            f_l_df = df_export[df_export["location"] == selected_loc].drop(columns=["date_parsed", "Month", "Week_of_Year", "Week_Label"], errors="ignore")
            st.dataframe(f_l_df, use_container_width=True, hide_index=True)
            st.download_button("📥 Download Site Logs (.CSV)", f_l_df.to_csv(index=False).encode("utf-8"), "location_report.csv", "text/csv")

# =========================================================================
# TAB 5: NAS BACKUP MONITORING
# =========================================================================
with tab_nas:
    st.header("💾 NAS Backup Monitoring")
    st.info("This module tracks NAS backup logs by server name, not by physical location.")

    left_col, right_col = st.columns([1, 1.4])

    with left_col:
        st.subheader("📝 Log Backup Entry")
        with st.form("nas_log_form", clear_on_submit=True):
            log_date = st.date_input("Backup Date", value=datetime.now())
            server_name = st.selectbox("Server Name *", SERVER_NAMES)
            st.caption(f"Mapped worksheet reference: {SERVER_SHEET_MAP.get(server_name, 'N/A')}")
            log_status = st.selectbox("Backup Status", ["Success", "Failed", "Warning / Partial"])
            log_storage_kb = st.number_input("Storage Used (KB) *", min_value=0.0, step=1024.0)
            storage_gb_preview = round(log_storage_kb / (1024 * 1024), 4)
            st.caption(f"Automatic conversion preview: {storage_gb_preview} GB")
            log_remarks = st.text_area("Operational Remarks / Error Logs")
            submit_nas = st.form_submit_button("Submit Backup Log 💾")

            if submit_nas:
                try:
                    new_nas_entry = {
                        "date": log_date.strftime("%Y-%m-%d"),
                        "server_name": server_name,
                        "status": log_status,
                        "storage_used": round(float(log_storage_kb) / (1024 * 1024), 4),
                        "remarks": log_remarks,
                    }
                    save_nas_log(new_nas_entry)
                    st.success(f"✅ Backup state saved for server {server_name}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ NAS log save error: {e}")

    with right_col:
        st.subheader("📊 Backup Health & Storage Growth")
        selected_server = st.selectbox("Select Server to View", SERVER_NAMES)
        df_nas_filtered = df_nas[df_nas["server_name"] == selected_server].copy() if not df_nas.empty else pd.DataFrame()

        if df_nas_filtered.empty:
            st.info(f"No backup logs found for server {selected_server}.")
        else:
            df_nas_sorted = df_nas_filtered.sort_values(by="date", ascending=True).copy()
            df_nas_sorted["Change (GB)"] = df_nas_sorted["storage_used"].diff().round(4)
            df_nas_sorted["Change (%)"] = (df_nas_sorted["storage_used"].pct_change() * 100).round(2)

            latest_status = df_nas_sorted.iloc[-1]["status"]
            latest_date = df_nas_sorted.iloc[-1]["date"]
            latest_size = df_nas_sorted.iloc[-1]["storage_used"]

            if latest_status == "Failed":
                st.error(f"⚠️ Critical alert: last backup on {latest_date} for {selected_server} failed.")
            elif latest_status == "Warning / Partial":
                st.warning(f"⚠️ Attention required: backup on {latest_date} for {selected_server} completed with warnings.")
            else:
                st.success(f"💚 Last backup on {latest_date} for {selected_server} completed successfully.")

            m1, m2 = st.columns(2)
            with m1:
                if len(df_nas_sorted) >= 2 and pd.notna(df_nas_sorted.iloc[-1]["Change (GB)"]):
                    delta_label = f"{df_nas_sorted.iloc[-1]['Change (GB)']:+.4f} GB ({df_nas_sorted.iloc[-1]['Change (%)']:+.2f}%)"
                else:
                    delta_label = "Baseline Init"
                st.metric("Latest Storage Footprint", f"{latest_size:,.4f} GB", delta=delta_label)
            with m2:
                st.metric("Mapped Log Entries", str(len(df_nas_sorted)))

            df_nas_table = df_nas_sorted.sort_values(by="date", ascending=False).copy()
            df_nas_table["Change (GB)"] = df_nas_table["Change (GB)"].apply(lambda x: f"{x:+.4f} GB" if pd.notnull(x) else "— Baseline")
            df_nas_table["Change (%)"] = df_nas_table["Change (%)"].apply(lambda x: f"{x:+.2f}%" if pd.notnull(x) else "— Baseline")
            st.dataframe(df_nas_table, use_container_width=True, hide_index=True)
            st.markdown("**Storage Footprint Over Time (GB)**")
            st.line_chart(df_nas_sorted.set_index("date")["storage_used"])

        st.markdown("---")
        st.subheader("📦 Server Summary")
        if df_nas.empty:
            st.info("No NAS summary available.")
        else:
            summary = (
                df_nas.groupby("server_name")
                .agg(
                    total_logs=("server_name", "count"),
                    latest_storage_gb=("storage_used", "max"),
                )
                .reset_index()
            )
            st.dataframe(summary, use_container_width=True, hide_index=True)
            st.bar_chart(summary.set_index("server_name")["latest_storage_gb"])

# =========================================================================
# TAB 6: RECURRING USERS
# =========================================================================
with tab_recurring:
    st.subheader("🔄 Repeated Incident Mapping Matrix")
    if df_live.empty:
        st.info("User activity log mapping system not yet populated.")
    else:
        user_metrics = (
            df_live.groupby("user_name")
            .agg(
                total_incidents=("id", "count"),
                resolved_count=("status", lambda s: (s == "Resolved").sum()),
                pending_backlog=("status", lambda s: (s != "Resolved").sum()),
            )
            .reset_index()
            .sort_values(by="total_incidents", ascending=False)
        )
        st.dataframe(user_metrics, use_container_width=True, hide_index=True)
        chronic_users = user_metrics[user_metrics["total_incidents"] >= 2]
        if not chronic_users.empty:
            st.warning(
                f"⚠️ {len(chronic_users)} user accounts have repeated incidents. Consider device inspection, training, or root-cause review."
            )
