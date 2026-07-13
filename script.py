Ah, it looks like my text explanation from the last reply accidentally got copied and pasted directly into your Python file (`script.py`)!

Because Python is trying to read that explanation as code, it's throwing a `SyntaxError`.

### How to Fix:

1. Open your `script.py` file.
2. **Delete everything** currently inside the file.
3. Copy **only the code block below** and paste it into the file. Make sure none of the conversational text outside the code block gets copied into your code editor.

Here is the clean, pure Python script ready to go:

```python
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
        border-left: 5px solid #ef4444; 
        padding: 18px;
        border-radius: 8px;
        margin-top: 15px;
        margin-bottom: 15px;
        color: #f8fafc;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .ai-title {
        color: #f87171;
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
        background-color: #ef4444 !important; 
        color: white !important;
    }
    div.stButton > button:first-child {
        background-color: #ef4444;
        color: white;
        border: none;
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

st.sidebar.header("⚙️ Node Connection Frame")
if db_connected:
    st.sidebar.success("⚡ Live Cloud Node: Connected")
else:
    st.sidebar.error("🛑 Cloud Node: Disconnected")

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
    else: return 'Other'

# =========================================================================
# 🗂️ TABBED WORKSPACE ARRANGEMENT
# =========================================================================
tab_log, tab_view, tab_analysis, tab_monthly, tab_recurring = st.tabs([
    "🆕 Log New Ticket", 
    "📑 View & Edit Tickets", 
    "📊 Analysis Dashboard", 
    "📥 Advanced Reporting Center",
    "🔄 Recurring Users"
])

# -------------------------------------------------------------------------
# TAB 1: LOG NEW TICKET WORKSPACE
# -------------------------------------------------------------------------
with tab_log:
    st.write("")
    st.header("📋 Log New Operations Ticket")
    
    if "form_default_start" not in st.session_state:
        st.session_state.form_default_start = datetime.now().time()
    if "form_default_close" not in st.session_state:
        st.session_state.form_default_close = datetime.now().time()
        
    if "ticket_submitted" not in st.session_state: st.session_state.ticket_submitted = False
    if "last_ticket_info" not in st.session_state: st.session_state.last_ticket_info = {}
    
    if st.session_state.ticket_submitted:
        info = st.session_state.last_ticket_info
        st.success("🎉 TICKET RECORD SECURED IN SUPABASE CLOUD SYSTEM!")
        formatted_id_string = format_ticket_number(info['id'], info['loc'])
        
        with st.container(border=True):
            col_a, col_b, col_c = st.columns(3)
            col_a.markdown(f"**Generated ID:** `{formatted_id_string}`")
            col_b.markdown(f"**Date:** {info['date']}")
            col_c.markdown(f"**Category:** {info['category']}")
            st.markdown(f"**User Details:** {info['user']} ({info['dept']}) | **Technician:** {info['tech']} | **Site:** {info['loc']}")
            st.caption(f"**Status:** {info['status']} | **Computed Time:** {info['duration']} mins")
            st.markdown(f"**Operational Action:** {info['remarks']}")
            
        if st.button("Log Another Ticket", type="primary"):
            st.session_state.ticket_submitted = False
            st.session_state.form_default_start = datetime.now().time()
            st.session_state.form_default_close = datetime.now().time()
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
                r1_left, r1_right = st.columns(2)
                user_name = r1_left.text_input("User Name *", value=default_user_name)
                attended_by = r1_right.selectbox("Attended By", list(TECH_MAP.keys()))
                
                r2_left, r2_right = st.columns(2)
                department = r2_left.text_input("Department *", value=default_dept)
                status = r2_right.selectbox("Initial Status", STATUS_OPTIONS, index=0)
                
                loc_default = default_loc.lower() if default_loc else ""
                default_index = 0
                for idx, loc_name in enumerate(OFFICIAL_LOCATIONS):
                    if any(token in loc_default for token in loc_name.lower().split()):
                        default_index = idx
                        break
                location = st.selectbox("Location/Sector *", options=OFFICIAL_LOCATIONS, index=default_index)
                
                complaint_desc = st.text_area("Complaint Description *", height=100)
                tech_remarks = st.text_area("Technician Operational Remarks", height=100)
                
                col_t1, col_t2 = st.columns(2)
                custom_start = col_t1.time_input("START Time", value=st.session_state.form_default_start, key="widget_start_time")
                custom_close = col_t2.time_input("RESOLVE Time", value=st.session_state.form_default_close, key="widget_close_time")
                
                submit_btn = st.form_submit_button("Submit Ticket")
                
                if submit_btn:
                    if not user_name or not complaint_desc or not department:
                        st.error("❌ Please populate all required fields (*).")
                    elif not db_connected:
                        st.error("❌ Database connection missing.")
                    else:
                        cat_final = auto_categorize(complaint_desc)
                        formatted_date = datetime.now().strftime("%Y-%m-%d")
                        
                        if status in ["Open", "On Hold - User Busy"]:
                            start_val, close_val, duration_mins = None, None, 0
                        else:
                            start_val = f"{formatted_date} {custom_start.strftime('%H:%M:%S')}"
                            close_val = f"{formatted_date} {custom_close.strftime('%H:%M:%S')}" if status == "Resolved" else None
                            duration_mins = max(1, int((datetime.combine(datetime.now().date(), custom_close) - datetime.combine(datetime.now().date(), custom_start)).total_seconds() / 60)) if status == "Resolved" else 0
                        
                        new_row = {
                            'date': formatted_date, 'user_name': user_name, 'department': department,
                            'complaint': complaint_desc, 'location': location, 'attended_by': attended_by,
                            'status': status, 'category': cat_final, 'remarks': tech_remarks, 
                            'start_time': start_val, 'close_time': close_val, 'resolution_time': duration_mins
                        }
                        try:
                            response = supabase_client.table("tickets").insert(new_row).execute()
                            st.session_state.last_ticket_info = {
                                "id": int(response.data[0]['id']), "date": formatted_date, "category": cat_final,
                                "user": user_name, "dept": department, "tech": attended_by, "loc": location,
                                "status": status, "duration": duration_mins, "remarks": tech_remarks
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
                placeholder="e.g., Printer is showing offline state..."
            )
            
            lang_choice = st.radio("Output Language Target", ["English", "हिंदी"], index=0, horizontal=True)
            parse_btn = st.button("💡 AI Assistance", use_container_width=True)
            
            if parse_btn:
                text_to_analyze = ai_input if ai_input.strip() else complaint_desc
                if text_to_analyze.strip():
                    cat = auto_categorize(text_to_analyze)
                    if cat in AI_SUGGESTIONS:
                        details = AI_SUGGESTIONS[cat]
                        title = details['title_en'] if lang_choice == "English" else details['title_hi']
                        steps = details['English'] if lang_choice == "English" else details['Hindi']
                        
                        steps_html = "".join([f"<div class='step-item'>🔹 {step}</div>" for step in steps])
                        st.markdown(f"<div class='ai-card'><div class='ai-title'>{title}</div>{steps_html}</div>", unsafe_allow_html=True)
                    else:
                        st.info("🔍 General diagnostic categorizer: Proceeding with standard hardware verification loops.")
                else:
                    st.warning("⚠️ Please provide complaint parameters in the text fields first.")

# -------------------------------------------------------------------------
# TAB 2: VIEW & EDIT WORKSPACE
# -------------------------------------------------------------------------
with tab_view:
    st.write("")
    if not df_live.empty:
        df_display = df_live.copy().sort_values(by='id', ascending=False)
        st.subheader("📋 Master Operational Backlog Log")
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("🔄 Update / Close an Existing Ticket")
        ticket_options = {
            f"{format_ticket_number(r['id'], r['location'])} — {r['user_name']} [{r['status']}]": r['id']
            for _, r in df_display.iterrows()
        }
        
        selected_ticket_lbl = st.selectbox("🎯 Choose a ticket from the active list to modify:", list(ticket_options.keys()))
        if selected_ticket_lbl:
            target_id = ticket_options[selected_ticket_lbl]
            ticket_data = df_display[df_display['id'] == target_id].iloc[0]
            
            with st.container(border=True):
                m_col1, m_col2, m_col3 = st.columns(3)
                m_col1.markdown(f"**Target User:** {ticket_data['user_name']}")
                m_col2.markdown(f"**Department:** {ticket_data['department']}")
                m_col3.markdown(f"**Current Status:** `{ticket_data['status']}`")
                st.info(f"📝 **Original Complaint:** {ticket_data['complaint']}")
                
                with st.form(f"update_form_{target_id}"):
                    edit_col1, edit_col2 = st.columns(2)
                    with edit_col1:
                        c_idx = STATUS_OPTIONS.index(ticket_data['status']) if ticket_data['status'] in STATUS_OPTIONS else 0
                        new_status = st.selectbox("Modify Status state *", options=STATUS_OPTIONS, index=c_idx)
                        
                        t_list = list(TECH_MAP.keys())
                        t_idx = t_list.index(ticket_data['attended_by']) if ticket_data['attended_by'] in t_list else 0
                        new_tech = st.selectbox("Reassign Attended By", options=t_list, index=t_idx)
                        
                    with edit_col2:
                        new_remarks = st.text_area("Update Action/Resolution Remarks", value=str(ticket_data['remarks']))
                        duration_input = st.number_input("Resolution Duration (in Minutes)", min_value=0, value=int(ticket_data['resolution_time']) if pd.notna(ticket_data['resolution_time']) else 0)
                        
                    save_update_btn = st.form_submit_button("Save Changes & Sync Data")
                    if save_update_btn:
                        final_remarks = str(new_remarks)
                        if new_status == "On Hold - User Busy" and not final_remarks.strip():
                            final_remarks = "Technician arrived to resolve, but user requested postponement due to ongoing business task constraints."
                            
                        update_payload = {
                            "status": str(new_status), "attended_by": str(new_tech),
                            "remarks": final_remarks, "resolution_time": int(duration_input)
                        }
                        if new_status == "Resolved" and not ticket_data['close_time']:
                            update_payload["close_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                        try:
                            supabase_client.table("tickets").update(update_payload).eq("id", int(target_id)).execute()
                            st.success(f"⚡ Ticket successfully synchronized to status: {new_status}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Update Sync Error: {e}")
    else:
        st.info("No active tickets found.")

# -------------------------------------------------------------------------
# TAB 3: ANALYSIS DASHBOARD
# -------------------------------------------------------------------------
with tab_analysis:
    st.write("")
    if not df_live.empty:
        total_tickets = len(df_live)
        resolved_tickets = len(df_live[df_live['status'].str.lower() == 'resolved'])
        held_tickets = len(df_live[df_live['status'].str.lower() == 'on hold - user busy'])
        open_tickets = len(df_live[df_live['status'].str.lower().isin(['open', 'in progress'])])
        
        resolved_df = df_live[(df_live['status'].str.lower() == 'resolved') & (df_live['resolution_time'] > 0)]
        avg_res_time = int(resolved_df['resolution_time'].mean()) if not resolved_df.empty else 0
        
        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
        kpi1.metric("Logged Volume", total_tickets)
        kpi2.metric("Resolved Queries", resolved_tickets)
        kpi3.metric("On Hold (User Busy)", held_tickets)
        kpi4.metric("Active Backlog Queue", open_tickets)
        kpi5.metric("Avg Resolution Speed", f"{avg_res_time} mins")
        
        st.markdown("---")
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown("### 🧑‍💻 Performance Distribution by Technician")
            st.bar_chart(df_live['attended_by'].value_counts())
        with chart_col2:
            st.markdown("### 🗂️ Breakdown by Current Status State")
            st.bar_chart(df_live['status'].value_counts())
    else:
        st.info("Log ticket entries to initialize the dashboard engine.")

# -------------------------------------------------------------------------
# TAB 4: ADVANCED REPORTING CENTER
# -------------------------------------------------------------------------
with tab_monthly:
    st.write("")
    st.header("📥 Advanced Operational Data Export Center")
    
    if not df_live.empty:
        df_export = df_live.copy()
        df_export['date_parsed'] = pd.to_datetime(df_export['date'], errors='coerce')
        df_export = df_export.dropna(subset=['date_parsed'])
        
        df_export['Month'] = df_export['date_parsed'].dt.strftime('%Y-%m (%B)')
        df_export['Week_of_Year'] = df_export['date_parsed'].dt.isocalendar().week
        df_export['Week_Label'] = df_export['date_parsed'].dt.strftime('%Y-W') + df_export['Week_of_Year'].astype(str)
        
        full_csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Unfiltered Master Log Sheet (.CSV)", full_csv, "it_master_production_log.csv", "text/csv")
        
        st.markdown("---")
        st.subheader("🔍 Target Filter Segment Logs")
        
        exp_tab_month, exp_tab_week, exp_tab_tech, exp_tab_loc = st.tabs([
            "📅 Monthly Logs", "📆 Weekly Logs", "🧑‍💻 Technician Logs", "🏢 Location Logs"
        ])
        
        with exp_tab_month:
            selected_month = st.selectbox("Select Target Month:", sorted(df_export['Month'].unique().tolist(), reverse=True), key="m_sel")
            f_m_df = df_export[df_export['Month'] == selected_month].drop(columns=['date_parsed','Month','Week_of_Year','Week_Label'], errors='ignore')
            st.dataframe(f_m_df, use_container_width=True, hide_index=True)
            st.download_button(f"📥 Download {selected_month} Logs (.CSV)", f_m_df.to_csv(index=False).encode('utf-8'), f"monthly_{selected_month}.csv", "text/csv")
            
        with exp_tab_week:
            selected_week = st.selectbox("Select Target Week:", sorted(df_export['Week_Label'].unique().tolist(), reverse=True), key="w_sel")
            f_w_df = df_export[df_export['Week_Label'] == selected_week].drop(columns=['date_parsed','Month','Week_of_Year','Week_Label'], errors='ignore')
            st.dataframe(f_w_df, use_container_width=True, hide_index=True)
            st.download_button(f"📥 Download {selected_week} Logs (.CSV)", f_w_df.to_csv(index=False).encode('utf-8'), f"weekly_{selected_week}.csv", "text/csv")
            
        with exp_tab_tech:
            selected_tech = st.selectbox("Select Technician:", sorted(df_export['attended_by'].unique().tolist()), key="t_sel")
            f_t_df = df_export[df_export['attended_by'] == selected_tech].drop(columns=['date_parsed','Month','Week_of_Year','Week_Label'], errors='ignore')
            st.dataframe(f_t_df, use_container_width=True, hide_index=True)
            st.download_button(f"📥 Download {selected_tech} Logs (.CSV)", f_t_df.to_csv(index=False).encode('utf-8'), f"tech_{selected_tech.lower()}.csv", "text/csv")
            
        with exp_tab_loc:
            selected_loc = st.selectbox("Select Site Location:", sorted(df_export['location'].unique().tolist()), key="l_sel")
            f_l_df = df_export[df_export['location'] == selected_loc].drop(columns=['date_parsed','Month','Week_of_Year','Week_Label'], errors='ignore')
            st.dataframe(f_l_df, use_container_width=True, hide_index=True)
            st.download_button(f"📥 Download Site Logs (.CSV)", f_l_df.to_csv(index=False).encode('utf-8'), f"location_report.csv", "text/csv")
    else:
        st.info("No logs present for targeted segment reporting splits.")

# -------------------------------------------------------------------------
# TAB 5: RECURRING USERS TRACKING WORKSPACE
# -------------------------------------------------------------------------
with tab_recurring:
    st.write("")
    st.subheader("🔄 Repeated Incident Mapping Matrix")
    if not df_live.empty:
        user_counts = df_live['user_name'].value_counts().reset_index()
        user_counts.columns = ['User Name', 'Total Incidents Raised']
        st.write("Track users requiring foundational hardware replacements or recurring operational oversight:")
        st.dataframe(user_counts, use_container_width=True, hide_index=True)
    else:
        st.info("User activity log mapping system operational.")
