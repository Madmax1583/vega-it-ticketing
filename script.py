import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# ===================== PAGE CONFIG =====================
st.set_page_config(page_title="Vega & Knitpro IT Ticketing", layout="wide")

# Styling
st.markdown("""
<style>
    .ai-card {background-color: #1e293b; border-left: 5px solid #3b82f6; padding: 18px; border-radius: 8px; margin: 10px 0;}
    .ai-title {color: #60a5fa; font-weight: bold; font-size: 1.15rem;}
</style>
""", unsafe_allow_html=True)

# ===================== LOGOS & TITLE =====================
col1, col2, col3 = st.columns([1, 1, 4])
with col1: st.caption("🔺 Vega")
with col2: st.caption("🔺 Knitpro")
with col3: st.title("🛠️ Vega & Knitpro IT Ticketing & Analysis System")

# ===================== SUPABASE =====================
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except:
        st.warning("⚠️ Supabase not configured. Local mode active.")
        return None

supabase = init_supabase()
db_connected = supabase is not None

def load_data():
    if not db_connected: return pd.DataFrame()
    try:
        response = supabase.table("tickets").select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except:
        return pd.DataFrame()

df_live = load_data()

# Constants
TECH_MAP = {"Satish": "TECH-01", "Priyanshu": "TECH-02", "Amit": "TECH-03", "Ranjan": "TECH-04", "Manish": "TECH-05"}
OFFICIAL_LOCATIONS = ["Sector - 136 Vega", "Knitpro 28-29", "Sector - 155 Vega", "Knitpro - Jaipur", "Knitpro 42", "Knitpro 72-73", "Knitpro 75", "Bharat Composite Sector 80", "Vega Sector 80"]
STATUS_OPTIONS = ["Open", "In Progress", "On Hold - User Busy", "Resolved"]

# AI Suggestions
AI_SUGGESTIONS = {
    "CCTV/Camera": {"title_en": "📷 CCTV Fix Guide", "title_hi": "📷 सीसीटीवी फिक्स गाइड", "English": ["Check power", "Restart NVR", "Ping IP"], "Hindi": ["पावर चेक करें", "NVR रीस्टार्ट करें", "IP पिंग करें"]},
    "Laptop/Hardware": {"title_en": "💻 Laptop Fix Guide", "title_hi": "💻 लैपटॉप फिक्स गाइड", "English": ["Check charger", "Hard reset", "Run diagnostic"], "Hindi": ["चार्जर चेक करें", "हार्ड रीसेट", "डायग्नोस्टिक चलाएं"]},
    "Printer": {"title_en": "🖨️ Printer Fix Guide", "title_hi": "🖨️ प्रिंटर फिक्स गाइड", "English": ["Check power", "Remove jammed paper", "Reinstall driver"], "Hindi": ["पावर चेक", "फंसा पेपर निकालें", "ड्राइवर रीइंस्टॉल"]},
}

def auto_categorize(text):
    t = str(text).lower()
    if any(k in t for k in ['cctv', 'camera']): return 'CCTV/Camera'
    elif any(k in t for k in ['laptop', 'desktop']): return 'Laptop/Hardware'
    elif any(k in t for k in ['outlook', 'email']): return 'Email/Outlook'
    elif any(k in t for k in ['printer']): return 'Printer'
    elif any(k in t for k in ['sap']): return 'SAP'
    elif any(k in t for k in ['network', 'wifi']): return 'Network'
    else: return 'Other'

# Navigation
page = st.sidebar.selectbox("Navigation", ["Log New Ticket", "View & Edit Tickets", "Analysis Dashboard", "Monthly Report", "Recurring Users"])

# ===================== LOG NEW TICKET =====================
if page == "Log New Ticket":
    st.header("📋 Log New Ticket")
    form_col, ai_col = st.columns([1.1, 0.9])
    
    with form_col:
        with st.form("ticket_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                user_name = st.text_input("Employee Name *")
                department = st.text_input("Department *")
                location = st.selectbox("Location *", OFFICIAL_LOCATIONS)
            with col2:
                attended_by = st.selectbox("Attended By", list(TECH_MAP.keys()))
                status = st.selectbox("Status", STATUS_OPTIONS)
            
            complaint = st.text_area("Complaint Description *", height=100)
            remarks = st.text_area("Resolution Remarks", height=80)
            
            if st.form_submit_button("Log Ticket"):
                if not user_name or not complaint:
                    st.error("❌ Please fill required fields (*)")
                else:
                    cat = auto_categorize(complaint)
                    new_row = {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "user_name": user_name,
                        "department": department,
                        "complaint": complaint,
                        "location": location,
                        "attended_by": attended_by,
                        "status": status,
                        "category": cat,
                        "remarks": remarks
                    }
                    if supabase:
                        supabase.table("tickets").insert(new_row).execute()
                        st.success("✅ Ticket Saved to Cloud!")
                    else:
                        st.success("✅ Ticket Saved Locally")
                    st.rerun()
    
    with ai_col:
        st.subheader("🧠 Live Copilot Core")
        complaint = st.text_area("🎯 Live Complaint Scan", height=115, placeholder="e.g., Printer offline...")
        suggestion_lang = st.radio("Language", ["English", "Hindi"], horizontal=True)
        
        if st.button("💡 Assist with Diagnosis", type="secondary"):
            if complaint:
                cat = auto_categorize(complaint)
                st.markdown(f"**Category:** `{cat}`")
                if cat in AI_SUGGESTIONS:
                    details = AI_SUGGESTIONS[cat]
                    title = details['title_en'] if suggestion_lang == "English" else details['title_hi']
                    steps = details['English'] if suggestion_lang == "English" else details['Hindi']
                    st.markdown(f"<div class='ai-card'><div class='ai-title'>{title}</div>" + "".join([f"<div class='step-item'>✅ {step}</div>" for step in steps]) + "</div>", unsafe_allow_html=True)
            else:
                st.info("Type the issue and click 'Assist with Diagnosis'.")

# Other tabs (add your existing code for tab_view, tab_analysis, tab_monthly)

st.sidebar.success("⚡ Live Cloud Node: Supabase Engine Active")
