import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# =========================================================================
# 🎛️ PAGE CONFIGURATION & INTERACTIVE STYLING
# =========================================================================
st.set_page_config(page_title="Vega & Knitpro IT Ticketing", layout="wide")

st.markdown("""
<style>
    .ai-card {
        background-color: #1e293b;
        border-left: 5px solid #3b82f6;
        padding: 18px;
        border-radius: 8px;
        margin-top: 10px;
        margin-bottom: 15px;
        color: #f8fafc;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .ai-title {
        color: #60a5fa;
        font-weight: bold;
        font-size: 1.15rem;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .step-item {
        margin-bottom: 8px;
        font-size: 0.95rem;
        line-height: 1.4;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 6px 6px 0px 0px;
        padding: 10px 20px;
        color: #cbd5e1;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================================
# 🏢 BRANDING & HEADERS
# =========================================================================
log_col1, log_col2, _, _ = st.columns([1, 1, 2, 2])
with log_col1:
    try:
        st.image("vega_logo.png", width=150)
    except Exception:
        st.caption("🔺 [Vega Logo]")

with log_col2:
    try:
        st.image("knitpro_logo.png", width=150)
    except Exception:
        st.caption("🔺 [Knitpro Logo]")

st.title("🛠️ Vega & Knitpro IT Ticketing & Analysis System")
st.markdown("---")

# =========================================================================
# 🔑 ROBUST SUPABASE INITIALIZATION
# =========================================================================
@st.cache_resource
def init_supabase() -> Client:
    if "supabase" not in st.secrets:
        raise KeyError("Missing '[supabase]' block tag header inside cloud deployment variables config.")
    url: str = st.secrets["supabase"].get("url", "")
    key: str = st.secrets["supabase"].get("key", "")
    if not url or not key:
        raise ValueError("Target credential strings extracted are blank or invalid.")
    return create_client(url, key)

supabase_client = None
db_connected = False
try:
    supabase_client = init_supabase()
    db_connected = True
except Exception as e:
    st.error(f"🔑 **Could not connect to Supabase Engine:** {str(e)}")

# =========================================================================
# 🤖 MULTILINGUAL KNOWLEDGE DICTIONARY
# =========================================================================
AI_SUGGESTIONS = {
    "CCTV/Camera": {
        "title_en": "📷 AI Video Infrastructure Diagnostics",
        "title_hi": "📷 एआई वीडियो इन्फ्रास्ट्रक्चर डायग्नोस्टिक्स",
        "English": [
            "Check if the camera POE switch port light is blinking. If not, swap ports or check the patch cord.",
            "Ping the camera IP address via CMD to check network dropouts.",
            "If NVR shows 'No Video', check if the camera channel needs a firmware restart or re-login."
        ],
        "Hindi": [
            "जांचें कि कैमरा POE स्विच पोर्ट की लाइट ब्लिंक कर रही है या नहीं। यदि नहीं, तो पोर्ट बदलें या पैच कॉर्ड चेक करें।",
            "नेटवर्क DROP-OUT चेक करने के लिए CMD के माध्यम से कैमरा IP एड्रेस को पिंग करें।",
            "यदि NVR 'No Video' दिखाता है, तो जांचें कि कैमरा चैनल को फर्मवेयर रीस्टार्ट या री-लॉगिन की आवश्यकता है या नहीं।"
        ]
    },
    "Laptop/Hardware": {
        "title_en": "💻 AI Endpoint Hardware Diagnostics",
        "title_hi": "💻 एआई एंडपॉइंट हार्डवेयर डायग्नोस्टिक्स",
        "English": [
            "**No Power:** Perform a hard reset (unplug battery, hold down power button for 30 seconds, reconnect).",
            "**Display Black:** Connect to an external monitor to verify if it's a motherboard issue or LCD panel failure.",
            "**Keyboard/Touchpad:** Check Device Manager for driver error codes and reinstall I2C drivers."
        ],
        "Hindi": [
            "**पावर नहीं आ रही:** हार्ड रीसेट करें (बैटरी निकालें, पावर बटन को 30 सेकंड तक दबाकर रखें, फिर फिर से कनेक्ट करें)।",
            "**डिस्प्ले ब्लैक है:** बाहरी मॉनिटर से कनेक्ट करके जांचें कि यह मदरबोर्ड की समस्या है या LCD पैनल खराब है।",
            "**कीबोर्ड/टचपैड:** ड्राइवर त्रुटि कोड के लिए डिवाइस मैनेजर की जांच करें और I2C ड्राइवरों को रीइन्स्टॉल करें।"
        ]
    },
    "Email/Outlook": {
        "title_en": "📧 AI Communication Layer Diagnostics",
        "title_hi": "📧 एआई कम्यूनिकेशन लेयर डायग्नोस्टिक्स",
        "English": [
            "**Outlook Crashing/Freezing:** Run `outlook.exe /safe` to see if a third-party add-in is causing the crash.",
            "**Send/Receive Error:** Check if the PST/OST file size has reached its limit (usually 50GB). Compact the data file.",
            "**Password Prompt:** Clear Windows Credential Manager cached passwords under 'Generic Credentials'."
        ],
        "Hindi": [
            "**आउटलुक क्रैश/फ्रीज:** यह देखने के लिए कि क्या कोई थर्ड-पार्टी ऐड-इन क्रैश का कारण बन रहा है, `outlook.exe /safe` चलाएं।",
            "**सेंड/रिसीव एरर:** जांचें कि क्या PST/OST फ़ाइल का आकार अपनी सीमा (आमतौर पर 50GB) तक पहुंच गया है। डेटा फ़ाइल को कॉम्पैक्ट करें।",
            "**पासवर्ड प्रॉम्प्ट:** विंडोज क्रेडेंशियल मैनेजर में कैश्ड पासवर्ड साफ़ करें।"
        ]
    },
    "Printer": {
        "title_en": "🖨️ AI Print Management Diagnostics",
        "title_hi": "🖨️ एआई प्रिंट MANAGEMENT डायग्नोस्टिक्स",
        "English": [
            "**Offline Mismatch:** Go to Printer Properties -> Ports -> Uncheck 'SNMP Status Enabled'.",
            "**Spooler Stuck:** Open `services.msc`, stop 'Print Spooler', clear PRINTERS directory, restart Spooler.",
            "**Faded Print:** Check toner cartridge level or clean the scanner glass mirror element."
        ],
        "Hindi": [
            "**ऑफलाइन मिसमैच:** प्रिंटर प्रॉपर्टीज -> पोर्ट्स पर जाएं -> 'SNMP Status Enabled' को अनचेक करें।",
            "**स्पूलर अटक गया:** `services.msc` खोलें, 'Print Spooler' को रोकें, PRINTERS फ़ोल्डर को खाली करें, फिर स्पूलर रीस्टार्ट करें।",
            "**हल्की प्रिंटिंग:** टोनर कार्ट्रिज लेवल की जांच करें या प्रिंटर कवर के अंदर स्कैनर ग्लास मिरर को साफ करें।"
        ]
    },
    "SAP": {
        "title_en": "🏢 AI Enterprise ERP Diagnostics",
        "title_hi": "🏢 एआई एंटरप्राइज ईआरपी डायग्नोस्टिक्स",
        "English": [
            "**Connection Timeout:** Verify `saplogon.ini` settings or check corporate local office VPN gateway.",
            "**Locked Session:** Go to transaction code `SM04` or `SM12` to clear old hung sessions.",
            "**GUI Error:** Clear the local SAP cache or reinstall SAP GUI patch level updates."
        ],
        "Hindi": [
            "**कनेक्शन टाइमआउट:** `saplogon.ini` सेटिंग्स को सत्यापित करें या जांचें कि उपयोगकर्ता कार्यालय गेटवे/VPN से जुड़ा है या नहीं।",
            "**लॉक्ड सेशन:** उपयोगकर्ता के लिए पुराने अटके हुए सेशन को हटाने के लिए ट्रांजेक्शन कोड `SM04` या `SM12` पर जाएं।",
            "**GUI एरर:** लोकल SAP कैश साफ़ करें या SAP GUI पैच लेवल अपडेट को रीइन्स्टॉल करें।"
        ]
    },
    "Network": {
        "title_en": "🌐 AI Network Routing Diagnostics",
        "title_hi": "🌐 एआई नेटवर्क राउटिंग डायग्नोस्टिक्स",
        "English": [
            "**Wi-Fi Dropping:** Run `netsh winsock reset` and update network adapter drivers.",
            "**IP Conflict:** Run `ipconfig /release` followed by `ipconfig /renew` to lease a fresh address.",
            "**Slow Speed:** Check if the user is connected to the 2.4GHz band instead of the 5GHz corporate tier."
        ],
        "Hindi": [
            "**वाई-फाई का बार-बार कटना:** `netsh winsock reset` चलाएं और नेटवर्क एडाप्टर ड्राइवरों को अपडेट करें।",
            "**आईपी संघर्ष (Conflict):** एक नया डायनेमिक एड्रेस प्राप्त करने के लिए `ipconfig /release` के बाद `ipconfig /renew` चलाएं।",
            "**धीमी गति:** जांचें कि क्या उपयोगकर्ता तेज 5GHz कॉर्पोरेट नेटवर्क के बजाय 2.4GHz बैंड से जुड़ा हुआ है।"
        ]
    }
}

# =========================================================================
# ⚙️ DATA PIPELINE CONTROLLERS
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

def load_data():
    if not db_connected or not supabase_client:
        return pd.DataFrame()
    try:
        response = supabase_client.table("tickets").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            if 'id' in df.columns:
                df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
            if 'resolution_time' in df.columns:
                df['resolution_time'] = pd.to_numeric(df['resolution_time'], errors='coerce').fillna(0).astype(int)
            if 'remarks' in df.columns:
                df['remarks'] = df['remarks'].fillna("")
            return df
        return pd.DataFrame(columns=['id', 'date', 'user_name', 'department', 'complaint', 'location', 'attended_by', 'status', 'category', 'start_time', 'close_time', 'resolution_time', 'remarks'])
    except Exception as e:
        st.warning(f"⚠️ Backlog array fetch status: Offline ({e})")
        return pd.DataFrame()

df_live = load_data()

TECH_MAP = {"Satish": "TECH-01", "Priyanshu": "TECH-02", "Amit": "TECH-03", "Ranjan": "TECH-04", "Manish": "TECH-05"}
OFFICIAL_LOCATIONS = ["Sector - 136 Vega", "Knitpro 28-29", "Sector - 155 Vega", "Knitpro - Jaipur", "Knitpro 42", "Knitpro 72-73", "Knitpro 75", "Bharat Composite Sector 80", "Vega Sector 80"]

def auto_categorize(complaint):
    text = str(complaint).lower()
    if any(k in text for k in ['cctv', 'camera', 'nvr']): return 'CCTV/Camera'
    elif any(k in text for k in ['laptop', 'desktop', 'keyboard', 'touchpad', 'battery', 'hinge', 'screen', 'power']): return 'Laptop/Hardware'
    elif any(k in text for k in ['outlook', 'email', 'mail', 'pst']): return 'Email/Outlook'
    elif any(k in text for k in ['printer', 'scanner', 'cartridge', 'print']): return 'Printer'
    elif any(k in text for k in ['sap']): return 'SAP'
    elif any(k in text for k in ['network', 'wifi', 'internet', 'vpn', 'ping', 'ip']): return 'Network'
    else: return 'Other'

# =========================================================================
# 🎛️ SIDEBAR CONTROL FRAME
# =========================================================================
st.sidebar.header("⚙️ Technician Settings")
suggestion_lang = st.sidebar.radio("🌐 Suggestion Language / भाषा चुनें", ["English", "Hindi"], index=0)
st.sidebar.markdown("---")
if db_connected:
    st.sidebar.success("⚡ Live Cloud Node: Connected")
else:
    st.sidebar.error("🛑 Cloud Node: Disconnected")

# =========================================================================
# 🗂️ TABBED WORKSPACE ARRANGEMENT
# =========================================================================
tab_log, tab_view, tab_analysis, tab_monthly, tab_recurring = st.tabs([
    "🆕 Enter Ticket Details", 
    "📂 Manage Active Backlog Queue", 
    "📊 Performance Matrix", 
    "📅 Monthly Closure Summaries",
    "👥 Chronic Fault Analysis"
])

# -------------------------------------------------------------------------
# TAB 1: FORM WORKSPACE
# -------------------------------------------------------------------------
with tab_log:
    st.write("")
    st.subheader("📝 Interactive Quick-Log Form")
    
    if "ticket_submitted" not in st.session_state: st.session_state.ticket_submitted = False
    if "last_ticket_info" not in st.session_state: st.session_state.last_ticket_info = {}

    if st.session_state.ticket_submitted:
        info = st.session_state.last_ticket_info
        st.success("🎉 **TICKET SUBMITTED AND SECURED IN SUPABASE CLOUD!**")
        formatted_id_string = format_ticket_number(info['id'], info['loc'])
        
        with st.container(border=True):
            col_a, col_b, col_c = st.columns(3)
            col_a.markdown(f"**Ticket Number:** `{formatted_id_string}`")
            col_b.markdown(f"**Date Assigned:** {info['date']}")
            col_c.markdown(f"**Category:** {info['category']}")
            st.markdown(f"**User:** {info['user']} ({info['dept']}) | **Handled By:** {info['tech']} | **Location:** {info['loc']}")
            st.caption(f"**Status:** {info['status']} | **Duration:** {info['duration']} mins")
            st.markdown(f"**Action/Remarks:** {info['remarks']}")
            
        if st.button("Log Another Ticket", type="primary"):
            st.session_state.ticket_submitted = False
            st.rerun()
            
    else:
        existing_users = sorted(df_live['user_name'].dropna().astype(str).unique().tolist()) if not df_live.empty else []
        selected_user = st.selectbox("💡 Search Existing User Name to Auto-Fill Details", ["New User / Type Below"] + existing_users)
        
        default_user_name, default_dept, default_loc = "", "", ""
        if selected_user != "New User / Type Below" and not df_live.empty:
            default_user_name = selected_user
            user_history = df_live[df_live['user_name'] == selected_user].sort_values(by='id', ascending=False)
            if not user_history.empty:
                default_dept = str(user_history.iloc[0].get('department', ''))
                default_loc = str(user_history.iloc[0].get('location', ''))

        form_col, ai_col = st.columns([1.1, 0.9], gap="large")
        
        with form_col:
            with st.form("ticket_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    user_name = st.text_input("Employee Name *", value=default_user_name)
                    department = st.text_input("Department Group *", value=default_dept)
                    
                    loc_default = default_loc.lower() if default_loc else ""
                    default_index = 0
                    for idx, loc_name in enumerate(OFFICIAL_LOCATIONS):
                        if any(token in loc_default for token in loc_name.lower().split()):
                            default_index = idx
                            break
                            
                    location = st.selectbox("Location Site Selector *", options=OFFICIAL_LOCATIONS, index=default_index)
                
                with col2:
                    ticket_date = st.date_input("Ticket Date *", value=datetime.now().date())
                    attended_by = st.selectbox("Attended By Technician", list(TECH_MAP.keys()))
                    status = st.selectbox("Initial Status State", ["Open", "In Progress", "Resolved"], index=0)
                
                st.caption("⚠️ Make sure to describe the issue in the **Live Copilot Core** field on the right before saving.")
                remarks = st.text_area("Resolution Actions Taken / Remarks (Optional)", height=80)
                
                col_t1, col_t2 = st.columns(2)
                custom_start = col_t1.time_input("START Time", value=datetime.now().time())
                custom_close = col_t2.time_input("RESOLVE Time", value=datetime.now().time())
                
                submit_btn = st.form_submit_button("Log Entry", type="primary")

        with ai_col:
            st.subheader("🧠 Live Copilot Core")
            complaint = st.text_area(
                "🎯 Live Complaint Scan (Type complaint keywords here first) *", 
                height=115, 
                placeholder="e.g., Printer is showing offline state or Outlook PST file size full..."
            )
            
            if complaint:
                cat = auto_categorize(complaint)
                st.markdown(f"**Calculated Auto-Category Type:** ` {cat} `")
                
                if cat in AI_SUGGESTIONS:
                    details = AI_SUGGESTIONS[cat]
                    title = details['title_en'] if suggestion_lang == "English" else details['title_hi']
                    steps = details['English'] if suggestion_lang == "English" else details['Hindi']
                    
                    steps_html = "".join([f"<div class='step-item'>✅ {step}</div>" for step in steps])
                    st.markdown(f"<div class='ai-card'><div class='ai-title'>{title}</div>{steps_html}</div>", unsafe_allow_html=True)
            else:
                msg = "💡 *Start typing out issue details to generate live troubleshooting roadmaps.*" if suggestion_lang == "English" else "💡 *समस्या निवारण रोडमैप देखने के लिए बॉक्स में विवरण टाइप करना शुरू करें।*"
                st.info(msg)

        if submit_btn:
            if not db_connected:
                st.error("❌ Submission blocked. The application cannot write entries while disconnected from the cloud database node.")
            elif not user_name or not complaint or not department or not location:
                st.error("❌ Missing required metadata values. Please populate the required fields (*).")
            else:
                cat_final = auto_categorize(complaint)
                formatted_date = ticket_date.strftime("%Y-%m-%d")
                
                if status == "Open":
                    start_val, close_val, duration_mins = None, None, None
                else:
                    start_val = f"{formatted_date} {custom_start.strftime('%H:%M:%S')}"
                    close_val = f"{formatted_date} {custom_close.strftime('%H:%M:%S')}" if status == "Resolved" else None
                    duration_mins = max(1, int((datetime.combine(ticket_date, custom_close) - datetime.combine(ticket_date, custom_start)).total_seconds() / 60)) if status == "Resolved" else None

                new_row = {
                    'date': str(formatted_date), 'user_name': str(user_name), 'department': str(department),
                    'complaint': str(complaint), 'location': str(location), 'attended_by': str(attended_by),
                    'status': str(status), 'category': str(cat_final), 'start_time': start_val,
                    'close_time': close_val, 'resolution_time': duration_mins, 'remarks': str(remarks)
                }
                
                try:
                    response = supabase_client.table("tickets").insert(new_row).execute()
                    st.session_state.last_ticket_info = {
                        "id": int(response.data[0]['id']), "date": formatted_date, "category": cat_final,
                        "user": user_name, "dept": department, "tech": attended_by, "loc": location,
                        "status": status, "duration": duration_mins if duration_mins else 0, "remarks": remarks
                    }
                    st.session_state.ticket_submitted = True
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Database Insertion Blocked: {e}")

# -------------------------------------------------------------------------
# TAB 2: DATA BACKLOG GRID & INTERACTIVE EDITOR
# -------------------------------------------------------------------------
with tab_view:
    st.write("")
    
    if not df_live.empty:
        df_sorted = df_live.sort_values(by='id', ascending=False).reset_index(drop=True)
        df_display = df_sorted.copy()
        df_display.insert(0, 'S.No.', range(1, len(df_display) + 1))
        df_display['Ticket Number'] = df_display.apply(lambda row: format_ticket_number(row['id'], row['location']), axis=1)
        
        cols = list(df_display.columns)
        if 'Ticket Number' in cols:
            cols.insert(1, cols.pop(cols.index('Ticket Number')))
        df_display = df_display[cols]
        
        # --- SECTION A: LIVE DATA VIEW ---
        st.subheader("📋 Master Production Backlog")
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # --- SECTION B: INTERACTIVE UPDATE CONTROLLER ---
        st.subheader("🔄 Update / Close an Existing Ticket")
        
        # Build an explicit drop-down mapping out clean Display IDs to their real internal database Primary Keys
        ticket_options = {}
        for _, r in df_sorted.iterrows():
            lbl = f"{format_ticket_number(r['id'], r['location'])} — {r['user_name']} ({r['complaint'][:30]}...)"
            ticket_options[lbl] = r['id']
            
        selected_ticket_lbl = st.selectbox("🎯 Choose a ticket from the active list to modify:", list(ticket_options.keys()))
        
        if selected_ticket_lbl:
            target_id = ticket_options[selected_ticket_lbl]
            ticket_data = df_sorted[df_sorted['id'] == target_id].iloc[0]
            
            # Display current metadata securely inside an organized layout
            with st.container(border=True):
                m_col1, m_col2, m_col3 = st.columns(3)
                m_col1.markdown(f"**Target User:** {ticket_data['user_name']}")
                m_col2.markdown(f"**Department:** {ticket_data['department']}")
                m_col3.markdown(f"**Current Status:** `{ticket_data['status']}`")
