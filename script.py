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

if not db_connected:
    st.warning("⚠️ **Database Credentials Missing:** Please make sure to add your `url` and `key` under the Streamlit App Secrets panel.")

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
            "**आउटलुक क्रैश/फ्रीज:** यह देखने के लिए कि क्या कोई协同-पार्टी ऐड-इन क्रैश का कारण बन रहा है, `outlook.exe /safe` चलाएं।",
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
    },
    "Server/UPS": {
        "title_en": "🖥️ Server & Power Infrastructure Diagnostics",
        "title_hi": "🖥️ सर्वर और पावर इन्फ्रास्ट्रक्चर डायग्नोस्टिक्स",
        "English": [
            "**UPS Beeping:** Check if input voltage is stable or if the load capacity is exceeding maximum parameters.",
            "**Server Room/Health:** Check temperature sensors; verify rack ventilation airflow paths.",
            "**Domain/AD:** Verify DNS forwarders configuration if clients fail authentication loops."
        ],
        "Hindi": [
            "**UPS बीपिंग:** जांचें कि इनपुट वोल्टेज स्थिर है या लोड क्षमता अधिकतम पैरामीटर से अधिक है।",
            "**सर्वर रूम/स्वास्थ्य:** तापमान सेंसर की जांच करें; रैक वेंटिलेशन एयरफ़्लो पथों को सत्यापित करें।",
            "**डोमेन/AD:** यदि क्लाइंट प्रमाणीकरण विफल हो जाते हैं, तो DNS फ़ॉरवर्डर कॉन्फ़िगरेशन सत्यापित करें।"
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
    if not db_connected:
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
    except Exception:
        return pd.DataFrame()

df_live = load_data()

TECH_MAP = {"Satish": "TECH-01", "Priyanshu": "TECH-02", "Amit": "TECH-03", "Ranjan": "TECH-04", "Manish": "TECH-05"}
OFFICIAL_LOCATIONS = ["Sector - 136 Vega", "Knitpro 28-29", "Sector - 155 Vega", "Knitpro - Jaipur", "Knitpro 42", "Knitpro 72-73", "Knitpro 75", "Bharat Composite Sector 80", "Vega Sector 80"]
STATUS_OPTIONS = ["Open", "In Progress", "On Hold - User Busy", "Resolved"]

def auto_categorize(complaint):
    text = str(complaint).lower()
    if any(k in text for k in ['cctv', 'camera', 'nvr']): return 'CCTV/Camera'
    elif any(k in text for k in ['laptop', 'desktop', 'keyboard', 'touchpad', 'battery', 'hinge', 'screen', 'power']): return 'Laptop/Hardware'
    elif any(k in text for k in ['outlook', 'email', 'mail', 'pst']): return 'Email/Outlook'
    elif any(k in text for k in ['printer', 'scanner', 'cartridge', 'print']): return 'Printer'
    elif any(k in text for k in ['sap']): return 'SAP'
    elif any(k in text for k in ['network', 'wifi', 'internet', 'vpn', 'ping', 'ip', 'firewall']): return 'Network'
    elif any(k in text for k in ['server', 'ups', 'rack', 'backup']): return 'Server/UPS'
    elif any(k in text for k in ['software', 'windows', 'activation', 'antivirus', 'installation']): return 'Infrastructure/Software'
    else: return 'Other'

if not df_live.empty and 'complaint' in df_live.columns:
    df_live['category'] = df_live['complaint'].apply(auto_categorize)

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
tab_log, tab_view, tab_analysis, tab_monthly = st.tabs([
    "🆕 Enter Ticket Details", 
    "📂 Manage Active Backlog Queue", 
    "📊 Performance Matrix", 
    "📥 Advanced Reporting Center"
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
                    status = st.selectbox("Initial Status State", STATUS_OPTIONS, index=0)
                
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
                
                if status in ["Open", "On Hold - User Busy"]:
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
        
        st.subheader("📋 Master Production Backlog")
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("🔄 Update / Close an Existing Ticket")
        
        ticket_options = {}
        for _, r in df_sorted.iterrows():
            lbl = f"{format_ticket_number(r['id'], r['location'])} — {r['user_name']} [{r['status']}]"
            ticket_options[lbl] = r['id']
            
        if ticket_options:
            selected_ticket_lbl = st.selectbox("🎯 Choose a ticket from the active list to modify:", list(ticket_options.keys()))
            
            if selected_ticket_lbl:
                target_id = ticket_options[selected_ticket_lbl]
                ticket_data = df_sorted[df_sorted['id'] == target_id].iloc[0]
                
                with st.container(border=True):
                    m_col1, m_col2, m_col3 = st.columns(3)
                    m_col1.markdown(f"**Target User:** {ticket_data['user_name']}")
                    m_col2.markdown(f"**Department:** {ticket_data['department']}")
                    m_col3.markdown(f"**Current Status:** `{ticket_data['status']}`")
                    st.info(f"📝 **Original Complaint:** {ticket_data['complaint']}")
                    
                with st.form(f"update_form_{target_id}"):
                    edit_col1, edit_col2 = st.columns(2)
                    
                    with edit_col1:
                        current_status_idx = STATUS_OPTIONS.index(ticket_data['status']) if ticket_data['status'] in STATUS_OPTIONS else 0
                        new_status = st.selectbox("Modify Status state *", options=STATUS_OPTIONS, index=current_status_idx)
                        
                        tech_list = list(TECH_MAP.keys())
                        current_tech_idx = tech_list.index(ticket_data['attended_by']) if ticket_data['attended_by'] in tech_list else 0
                        new_tech = st.selectbox("Reassign Attended By", options=tech_list, index=current_tech_idx)
                        
                    with edit_col2:
                        new_remarks = st.text_area("Update Action/Resolution Remarks", value=str(ticket_data['remarks']))
                        
                    st.caption("⏱️ Duration window calculation (Skip or leave 0 if putting ticket On Hold):")
                    duration_input = st.number_input("Resolution Duration (in Minutes)", min_value=0, value=int(ticket_data['resolution_time']) if pd.notna(ticket_data['resolution_time']) else 0)
                    
                    save_update_btn = st.form_submit_button("Save Changes & Sync Data", type="primary")
                    
                    if save_update_btn:
                        if not db_connected:
                            st.error("❌ Action blocked. Application is disconnected from the cloud database node.")
                        else:
                            # Auto-fill warning remark if marked as On Hold and remarks are left clean
                            final_remarks = str(new_remarks)
                            if new_status == "On Hold - User Busy" and (not final_remarks or final_remarks.strip() == ""):
                                final_remarks = "Technician arrived to resolve, but user requested postponement due to ongoing business task constraints."
                            
                            update_payload = {
                                "status": str(new_status),
                                "attended_by": str(new_tech),
                                "remarks": final_remarks,
                                "resolution_time": int(duration_input)
                            }
                            
                            if new_status == "Resolved" and not ticket_data['close_time']:
                                update_payload["close_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                
                            try:
                                supabase_client.table("tickets").update(update_payload).eq("id", int(target_id)).execute()
                                st.success(f"⚡ Ticket successfully updated to status: {new_status}!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Failed to synchronize database entry: {e}")
    else:
        st.info("No active production records mapped inside cloud nodes or database is empty.")

# -------------------------------------------------------------------------
# TAB 3: PERFORMANCE MATRIX (LIVE DATA ANALYTICS)
# -------------------------------------------------------------------------
with tab_analysis:
    st.write("")
    st.subheader("📊 Operational Analytics & KPI Metrics")
    
    if not df_live.empty:
        total_tickets = len(df_live)
        resolved_tickets = len(df_live[df_live['status'].str.lower() == 'resolved'])
        held_tickets = len(df_live[df_live['status'].str.lower() == 'on hold - user busy'])
        open_tickets = len(df_live[df_live['status'].str.lower().isin(['open', 'in progress'])])
        
        resolved_df = df_live[(df_live['status'].str.lower() == 'resolved') & (df_live['resolution_time'] > 0)]
        avg_res_time = int(resolved_df['resolution_time'].mean()) if not resolved_df.empty else 0
        
        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
        kpi1.metric("Total Logged Volume", total_tickets)
        kpi2.metric("Resolved Queries", resolved_tickets)
        kpi3.metric("On Hold (User Busy)", held_tickets)
        kpi4.metric("Active Backlog Queue", open_tickets)
        kpi5.metric("Avg Resolution Speed", f"{avg_res_time} mins")
        
        st.markdown("---")
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("### 🧑‍💻 Performance Distribution by Technician")
            tech_counts = df_live['attended_by'].value_counts()
            st.bar_chart(tech_counts)
            
        with chart_col2:
            st.markdown("### 🗂️ Breakdown by Current Status State")
            status_counts = df_live['status'].value_counts()
            st.bar_chart(status_counts)
    else:
        st.info("Log your first ticket entries to initialize the live metrics dashboard engine.")

# -------------------------------------------------------------------------
# TAB 4: ADVANCED REPORTING CENTER (DETAILED EXPORTS)
# -------------------------------------------------------------------------
with tab_monthly:
    st.write("")
    st.subheader("📥 Operational Data Export Center")
    st.markdown("Generate full detailed logs for management reviews, weekly slides, or engineer-specific tracking.")
    
    if not df_live.empty:
        df_export = df_live.copy()
        df_export['date_parsed'] = pd.to_datetime(df_export['date'], errors='coerce')
        df_export = df_export.dropna(subset=['date_parsed'])
        
        df_export['Month'] = df_export['date_parsed'].dt.strftime('%Y-%m (%B)')
        df_export['Week_of_Year'] = df_export['date_parsed'].dt.isocalendar().week
        df_export['Week_Label'] = df_export['date_parsed'].dt.strftime('%Y-W') + df_export['Week_of_Year'].astype(str)
        df_export['Ticket_Number'] = df_export.apply(lambda row: format_ticket_number(row['id'], row['location']), axis=1)

        ordered_cols = ['Ticket_Number', 'date', 'user_name', 'department', 'location', 'attended_by', 'category', 'complaint', 'status', 'resolution_time', 'remarks']
        existing_ordered = [c for c in ordered_cols if c in df_export.columns] + [c for c in df_export.columns if c not in ordered_cols]
        df_export = df_export[existing_ordered]

        with st.container(border=True):
            st.markdown("#### 📋 1. Download Entire Master Database Logs")
            st.caption("Exports every single ticket parameter, timeline, and remark from the system.")
            full_master_csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Unfiltered Master Log Sheet (.CSV)", full_master_csv, "it_master_production_log.csv", "text/csv")

        st.markdown("---")
        st.markdown("#### 🔍 2. Filter & Download Filtered Segment Logs")
        st.caption("Select a parameter to view and download full individual ticket details.")

        exp_tab_month, exp_tab_week, exp_tab_tech, exp_tab_loc = st.tabs([
            "📅 Monthly Logs", "📆 Weekly Logs", "🧑‍💻 Technician Logs", "🏢 Location Logs"
        ])

        with exp_tab_month:
            available_months = sorted(df_export['Month'].unique().tolist(), reverse=True)
            selected_month = st.selectbox("Select Target Month:", available_months, key="sel_m")
            
            filtered_m_df = df_export[df_export['Month'] == selected_month].drop(columns=['date_parsed', 'Month', 'Week_of_Year', 'Week_Label'], errors='ignore')
            st.write(f"Showing **{len(filtered_m_df)}** detailed records for `{selected_month}`:")
            st.dataframe(filtered_m_df, use_container_width=True, hide_index=True)
            
            csv_m_detailed = filtered_m_df.to_csv(index=False).encode('utf-8')
            st.download_button(f"📥 Download Detailed Logs for {selected_month} (.CSV)", csv_m_detailed, f"it_detailed_log_{selected_month.replace(' ', '_')}.csv", "text/csv")

        with exp_tab_week:
            available_weeks = sorted(df_export['Week_Label'].unique().tolist(), reverse=True)
            selected_week = st.selectbox("Select Target Week:", available_weeks, key="sel_w")
            
            filtered_w_df = df_export[df_export['Week_Label'] == selected_week].drop(columns=['date_parsed', 'Month', 'Week_of_Year', 'Week_Label'], errors='ignore')
            st.write(f"Showing **{len(filtered_w_df)}** detailed records for `{selected_week}`:")
            st.dataframe(filtered_w_df, use_container_width=True, hide_index=True)
            
            csv_w_detailed = filtered_w_df.to_csv(index=False).encode('utf-8')
            st.download_button(f"📥 Download Detailed Logs for {selected_week} (.CSV)", csv_w_detailed, f"it_detailed_log_{selected_week}.csv", "text/csv")

        with exp_tab_tech:
            available_techs = sorted(df_export['attended_by'].unique().tolist())
            selected_tech = st.selectbox("Select Technician Name:", available_techs, key="sel_t")
            
            filtered_t_df = df_export[df_export['attended_by'] == selected_tech].drop(columns=['date_parsed', 'Month', 'Week_of_Year', 'Week_Label'], errors='ignore')
            st.write(f"Showing **{len(filtered_t_df)}** detailed records managed by `{selected_tech}`:")
            st.dataframe(filtered_t_df, use_container_width=True, hide_index=True)
            
            csv_t_detailed = filtered_t_df.to_csv(index=False).encode('utf-8')
            st.download_button(f"📥 Download Detailed Logs for {selected_tech} (.CSV)", csv_t_detailed, f"it_detailed_log_{selected_tech.lower()}.csv", "text/csv")

        with exp_tab_loc:
            available_locs = sorted(df_export['location'].unique().tolist())
            selected_loc = st.selectbox("Select Operating Site Location:", available_locs, key="sel_l")
            
            filtered_l_df = df_export[df_export['location'] == selected_loc].drop(columns=['date_parsed', 'Month', 'Week_of_Year', 'Week_Label'], errors='ignore')
            st.write(f"Showing **{len(filtered_l_df)}** detailed records for site `{selected_loc}`:")
            st.dataframe(filtered_l_df, use_container_width=True, hide_index=True)
            
            csv_l_detailed = filtered_l_df.to_csv(index=False).encode('utf-8')
            st.download_button(f"📥 Download Detailed Logs for {selected_loc.replace(' ', '_')} (.CSV)", csv_l_detailed, f"it_detailed_log_{selected_loc.replace(' ', '_')}.csv", "text/csv")
            
    else:
        st.info("Operational logs must be active to compute target summaries.")
