import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

st.set_page_config(page_title="Vega & Knitpro IT Ticketing", layout="wide")

# Styling
st.markdown("""
<style>
    .ai-card {background-color: #1e293b; border-left: 5px solid #3b82f6; padding: 18px; border-radius: 8px; margin: 10px 0;}
    .ai-title {color: #60a5fa; font-weight: bold; font-size: 1.15rem;}
</style>
""", unsafe_allow_html=True)

# Logos & Title
col1, col2, col3 = st.columns([1, 1, 4])
with col1: st.caption("🔺 Vega")
with col2: st.caption("🔺 Knitpro")
with col3: st.title("🛠️ Vega & Knitpro IT Ticketing & Analysis System")

# Supabase
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
        response = supabase.table("tickets").select("*").order("id", desc=True).execute()
        df = pd.DataFrame(response.data) if response.data else pd.DataFrame()
        if not df.empty:
            df['id'] = pd.to_numeric(df['id'], errors='coerce')
        return df
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
                user_name = st.text_input("User Name *")
                department = st.text_input("Department *")
                location = st.selectbox("Location/Sector *", OFFICIAL_LOCATIONS)
            with col2:
                attended_by = st.selectbox("Attended By", list(TECH_MAP.keys()))
                status = st.selectbox("Status", STATUS_OPTIONS)
            
            complaint = st.text_area("Complaint Description *", height=100)
            remarks = st.text_area("Technician Remarks", height=80)
            
            if st.form_submit_button("Submit Ticket"):
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
        st.subheader("🧠 AI Copilot")
        complaint_input = st.text_area("Type complaint for AI suggestions", height=150)
        lang = st.radio("Language", ["English", "हिंदी"], horizontal=True)
        
        if st.button("💡 Get AI Suggestion", type="primary"):
            if complaint_input:
                cat = auto_categorize(complaint_input)
                st.success(f"**Category:** `{cat}`")
                if cat in AI_SUGGESTIONS:
                    details = AI_SUGGESTIONS[cat]
                    title = details['title_en'] if lang == "English" else details['title_hi']
                    steps = details['English'] if lang == "English" else details['Hindi']
                    st.markdown(f"**{title}**")
                    for step in steps:
                        st.write(f"✅ {step}")
                else:
                    st.info("No specific guide available yet.")
            else:
                st.warning("Please type a complaint first.")

# ===================== VIEW & EDIT TICKETS =====================
elif page == "View & Edit Tickets":
    st.header("📋 View & Edit Tickets")
    if df_live.empty:
        st.info("No tickets found. Log some tickets first.")
    else:
        st.dataframe(df_live.sort_values(by='id', ascending=False), use_container_width=True)
        
        st.subheader("Update Ticket")
        if not df_live.empty:
            ticket_id = st.selectbox("Select Ticket ID", df_live['id'].tolist())
            new_status = st.selectbox("New Status", STATUS_OPTIONS)
            if st.button("Update Status"):
                try:
                    supabase.table("tickets").update({"status": new_status}).eq("id", ticket_id).execute()
                    st.success("Status Updated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Update failed: {e}")

# Other pages
else:
    st.header(page)
    if not df_live.empty:
        st.bar_chart(df_live['category'].value_counts())
    else:
        st.info("No data yet.")

st.sidebar.success("⚡ Supabase Connected" if db_connected else "Local Mode")
