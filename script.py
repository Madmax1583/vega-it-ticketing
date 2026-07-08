import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# Page Configuration
st.set_page_config(page_title="Vega & Knitpro IT Ticketing", layout="wide")

# ===================== LOGO & TITLE SECTION =====================
log_col1, log_col2, log_spacer1, log_spacer2 = st.columns([1, 1, 2, 2])

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

# ===================== SUPABASE CONNECTION =====================
@st.cache_resource
def init_supabase() -> Client:
    url: str = st.secrets["supabase"]["url"]
    key: str = st.secrets["supabase"]["key"]
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as e:
    st.error("🔑 Could not connect to Supabase. Please check your Streamlit Secrets configuration.")
    st.stop()

def load_data():
    try:
        response = supabase.table("tickets").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df['id'] = pd.to_numeric(df['id'], errors='coerce')
            df['resolution_time'] = pd.to_numeric(df['resolution_time'], errors='coerce').fillna(0).astype(int)
            
            # Convert text dates into actual datetime objects for advanced reporting
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            # Safeguards for newer tracking columns
            if 'remarks' not in df.columns: df['remarks'] = ""
            else: df['remarks'] = df['remarks'].fillna("")
                
            if 'technician_id' not in df.columns: df['technician_id'] = ""
            else: df['technician_id'] = df['technician_id'].fillna("")
                
            return df
        return pd.DataFrame(columns=[
            'id', 'date', 'user_name', 'department', 'complaint', 
            'location', 'attended_by', 'status', 'category', 
            'start_time', 'close_time', 'resolution_time', 'remarks', 'technician_id'
        ])
    except Exception as e:
        st.error(f"⚠️ Failed to fetch live data from Supabase Cloud: {e}")
        return pd.DataFrame()

# CRITICAL FIX: Explicitly loading global dataframe here so it's accessible everywhere
df_live = load_data()

# Sidebar Navigation
page = st.sidebar.selectbox("Navigation", 
    ["Log New Ticket", "View & Edit Tickets", "Analysis Dashboard", "Monthly Report", "Recurring Users"])

# Technician ID Mapping Dictionary
TECH_MAP = {
    "Satish": "TECH-01",
    "Priyanshu": "TECH-02",
    "Amit": "TECH-03",
    "Ranjan": "TECH-04",
    "Manish": "TECH-05"
}

def auto_categorize(complaint):
    text = str(complaint).lower()
    if any(k in text for k in ['cctv', 'camera', 'nvr']): return 'CCTV/Camera'
    elif any(k in text for k in ['laptop', 'desktop', 'keyboard', 'touchpad', 'battery', 'hinge', 'screen']): return 'Laptop/Hardware'
    elif any(k in text for k in ['outlook', 'email', 'mail', 'pst']): return 'Email/Outlook'
    elif any(k in text for k in ['printer', 'scanner', 'cartridge']): return 'Printer'
    elif any(k in text for k in ['sap']): return 'SAP'
    elif any(k in text for k in ['network', 'wifi', 'internet', 'vpn']): return 'Network'
    elif any(k in text for k in ['ups', 'server', 'backup', 'nas']): return 'Server/UPS'
    else: return 'Other'

# ===================== LOG NEW TICKET =====================
if page == "Log New Ticket":
    st.header("📋 Log New Ticket")
    
    if "ticket_submitted" not in st.session_state:
        st.session_state.ticket_submitted = False
    if "last_ticket_info" not in st.session_state:
        st.session_state.last_ticket_info = {}

    if st.session_state.ticket_submitted:
        info = st.session_state.last_ticket_info
        st.success("🎉 **TICKET SUBMITTED AND SECURED IN SUPABASE CLOUD!**")
        
        with st.container(border=True):
            col_a, col_b, col_c = st.columns(3)
            col_a.markdown(f"**Ticket ID:** #{info['id']}")
            col_b.markdown(f"**Date Assigned:** {info['date']}")
            col_c.markdown(f"**Category:** {info['category']}")
            st.markdown(f"**User:** {info['user']} ({info['dept']}) | **Handled By:** {info['tech']} ({info['tech_id']}) | **Location:** {info['loc']}")
            st.caption(f"**Status:** {info['status']} | **Start:** {info['start']} | **End:** {info['close']} ({info['duration']} mins)")
            st.markdown(f"**Action/Remarks:** {info['remarks']}")
            
        if st.button("Log Another Ticket", type="primary"):
            st.session_state.ticket_submitted = False
            st.rerun()
            
    else:
        with st.form("ticket_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                user_name = st.text_input("User Name *")
                department = st.text_input("Department *")
                location = st.text_input("Location/Sector *")
            with col2:
                ticket_date = st.date_input("Ticket Date *", value=datetime.now().date())
                attended_by = st.selectbox("Attended By", list(TECH_MAP.keys()))
                status = st.selectbox("Status", ["Open", "In Progress", "Resolved"], index=0)
            
            complaint = st.text_area("Complaint Description *", height=100)
            remarks = st.text_area("Technician Action / Resolution Remarks (Optional)", height=80)
            
            st.markdown("🕒 **Time Tracking Options (For back-dated entries):**")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                custom_start = st.time_input("What time did you START working on this?", value=datetime.now().time())
            with col_t2:
                custom_close = st.time_input("What time did you RESOLVE this? (Only applies if status is Resolved)", value=datetime.now().time())
            
            if st.form_submit_button("Submit Ticket"):
                if not user_name or not complaint or not department or not location:
                    st.error("❌ Please fill out all required fields (*)")
                else:
                    cat = auto_categorize(complaint)
                    formatted_date = ticket_date.strftime("%Y-%m-%d")
                    tech_id_val = TECH_MAP.get(attended_by, "")
                    
                    if status == "Open":
                        start_val = ""
                        close_val = ""
                        duration_mins = 0
                    elif status == "In Progress":
                        start_val = f"{formatted_date} {custom_start.strftime('%H:%M:%S')}"
                        close_val = ""
                        duration_mins = 0
                    elif status == "Resolved":
                        start_val = f"{formatted_date} {custom_start.strftime('%H:%M:%S')}"
                        close_val = f"{formatted_date} {custom_close.strftime('%H:%M:%S')}"
                        
                        t1 = datetime.combine(ticket_date, custom_start)
                        t2 = datetime.combine(ticket_date, custom_close)
                        duration_mins = int((t2 - t1).total_seconds() / 60)
                        if duration_mins < 0: duration_mins = 1
                    
                    new_row = {
                        'date': formatted_date, 'user_name': user_name,
                        'department': department, 'complaint': complaint, 'location': location,
                        'attended_by': attended_by, 'status': status, 'category': cat,
                        'start_time': start_val, 'close_time': close_val, 'resolution_time': duration_mins,
                        'remarks': remarks, 'technician_id': tech_id_val
                    }
