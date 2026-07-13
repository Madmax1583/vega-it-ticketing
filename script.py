import streamlit as st
import pandas as pd
from datetime import datetime

# =========================================================================
# 🎨 PAGE CONFIGURATION & STYLING
# =========================================================================
st.set_page_config(page_title="Vega & Knitpro IT Operations", layout="wide")

st.markdown("""
<style>
    .ai-card { background-color: #1e293b; border-left: 5px solid #3b82f6; padding: 18px; border-radius: 8px; margin-top: 10px; color: #f8fafc; }
    .ai-title { color: #60a5fa; font-weight: bold; font-size: 1.15rem; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }
    .step-item { margin-bottom: 8px; font-size: 0.95rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #1e293b; border-radius: 6px 6px 0px 0px; padding: 10px 20px; color: #cbd5e1; font-weight: 600; }
    .stTabs [aria-selected="true"] { background-color: #3b82f6 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================================
# ⚙️ CORE LOGIC & UTILITIES
# =========================================================================
def format_ticket_number(ticket_id, location_str):
    """Generates standardized ID like VEGA-2026-0001"""
    loc = str(location_str).lower()
    prefix = "VEGA" if ("vega" in loc or "136" in loc) else ("KP" if "knitpro" in loc else "IT")
    return f"{prefix}-2026-{int(ticket_id):04d}"

def auto_categorize(complaint):
    text = str(complaint).lower()
    if any(k in text for k in ['cctv', 'camera']): return 'CCTV/Camera'
    if any(k in text for k in ['laptop', 'power']): return 'Laptop/Hardware'
    if any(k in text for k in ['outlook', 'email']): return 'Email/Outlook'
    if any(k in text for k in ['printer', 'print']): return 'Printer'
    return 'Other'

AI_SUGGESTIONS = {
    "CCTV/Camera": {
        "title_en": "📷 AI Video Diagnostics",
        "title_hi": "📷 एआई वीडियो डायग्नोस्टिक्स",
        "English": ["Check POE switch port light.", "Ping camera IP via CMD.", "NVR 'No Video'? Restart channel."],
        "Hindi": ["POE स्विच पोर्ट लाइट देखें।", "CMD से IP पिंग करें।", "NVR 'No Video' के लिए चैनल रीस्टार्ट करें।"]
    },
    "Laptop/Hardware": {
        "title_en": "💻 AI Hardware Diagnostics",
        "title_hi": "💻 एआई हार्डवेयर डायग्नोस्टिक्स",
        "English": ["Hard reset (30s power hold).", "Verify external monitor.", "Check Device Manager."],
        "Hindi": ["हार्ड रीसेट करें (30 सेकंड पावर होल्ड)।", "एक्सटर्नल मॉनिटर चेक करें।", "डिवाइस मैनेजर देखें।"]
    },
    "Email/Outlook": {
        "title_en": "📧 AI Communication Diagnostics",
        "title_hi": "📧 एआई कम्यूनिकेशन डायग्नोस्टिक्स",
        "English": ["Run `outlook.exe /safe`.", "Check PST/OST size.", "Clear Credential Manager."],
        "Hindi": ["`outlook.exe /safe` चलाएं।", "PST/OST फ़ाइल साइज देखें।", "क्रेडेंशियल मैनेजर साफ़ करें।"]
    },
    "Printer": {
        "title_en": "🖨️ AI Print Diagnostics",
        "title_hi": "🖨️ एआई प्रिंट डायग्नोस्टिक्स",
        "English": ["Uncheck 'SNMP Status'.", "Restart 'Print Spooler'.", "Clean toner."],
        "Hindi": ["'SNMP Status' अनचेक करें।", "'Print Spooler' रीस्टार्ट करें।", "टोनर साफ़ करें।"]
    }
}

# =========================================================================
# 📂 DATA HANDLING
# =========================================================================
@st.cache_data
def load_data():
    try: return pd.read_csv("it_master_production_log.csv")
    except: return pd.DataFrame()

df = load_data()

# =========================================================================
# 🏗️ APP LAYOUT
# =========================================================================
st.title("🛠️ Vega & Knitpro Unified IT Operations")
tab_log, tab_view, tab_matrix, tab_reports = st.tabs(["🆕 Enter Ticket", "📂 Manage Backlog", "📊 Matrix/Reassign", "📥 Reports"])

# TAB 1: ENTER TICKET
with tab_log:
    col_f, col_ai = st.columns([1, 1])
    with col_f:
        with st.form("ticket_form", clear_on_submit=True):
            st.subheader("New Ticket Entry")
            user_name = st.text_input("Employee Name")
            location = st.selectbox("Location", ["Sector - 136 Vega", "Knitpro - Jaipur", "Sector - 155 Vega"])
            remarks = st.text_area("Remarks")
            if st.form_submit_button("Log Ticket"):
                st.success("Ticket Logged & Formatted!")
    with col_ai:
        st.subheader("🧠 Live Copilot Core")
        complaint = st.text_area("🎯 Live Complaint Scan *", height=115, placeholder="e.g., Printer is showing offline...")
        suggestion_lang = st.radio("Language", ["English", "Hindi"], horizontal=True)
        assist_btn = st.button("💡 Assist with Diagnosis", type="secondary")
        
        if assist_btn or complaint:
            cat = auto_categorize(complaint)
            st.markdown(f"**Calculated Category:** ` {cat} `")
            if cat in AI_SUGGESTIONS:
                details = AI_SUGGESTIONS[cat]
                steps = details['English'] if suggestion_lang == "English" else details['Hindi']
                title = details['title_en'] if suggestion_lang == "English" else details['title_hi']
                steps_html = "".join([f"<div class='step-item'>✅ {step}</div>" for step in steps])
                st.markdown(f"<div class='ai-card'><div class='ai-title'>{title}</div>{steps_html}</div>", unsafe_allow_html=True)

# TAB 2: BACKLOG
with tab_view:
    st.subheader("📂 Manage Backlog")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else: st.info("No data found.")

# TAB 3: MATRIX & REASSIGNMENT
with tab_matrix:
    st.subheader("📊 Technician Matrix & Reassignment")
    if not df.empty:
        ticket_to_edit = st.selectbox("Select Ticket to Reassign", df['Formatted_Ticket'].unique())
        new_tech = st.selectbox("Assign to Technician", ["Satish", "Priyanshu", "Amit"])
        if st.button("Apply Reassignment"):
            st.success(f"Ticket {ticket_to_edit} reassigned to {new_tech}")
    else: st.info("Load backlog to manage assignments.")

# TAB 4: REPORTS
with tab_reports:
    st.subheader("📥 Advanced Reporting Center")
    col1, col2 = st.columns(2)
    with col1:
        month_filter = st.selectbox("Select Month", ["July 2026", "August 2026"])
    with col2:
        tech_filter = st.multiselect("Filter by Technician", ["Satish", "Priyanshu", "Amit"])
    
    st.write("---")
    st.write(f"Generating report for: {month_filter}")
    # Placeholder for logic to filter df by selection
    st.bar_chart(df['category'].value_counts() if not df.empty else None)
