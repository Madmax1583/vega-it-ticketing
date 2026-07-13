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
    .metric-box {background-color: #0f172a; padding: 15px; border-radius: 6px; border: 1px solid #334155; text-align: center;}
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
    except Exception as e:
        st.sidebar.warning("⚠️ Supabase not configured. Running in Local Mode.")
        return None

supabase = init_supabase()
db_connected = supabase is not None

def load_data():
    if not db_connected: 
        # Return dummy data schema for local preview mode if DB is missing
        return pd.DataFrame(columns=['id', 'date', 'user_name', 'department', 'complaint', 'location', 'attended_by', 'status', 'category', 'remarks'])
    try:
        response = supabase.table("tickets").select("*").order("id", desc=True).execute()
        df = pd.DataFrame(response.data) if response.data else pd.DataFrame()
        if not df.empty:
            df['id'] = pd.to_numeric(df['id'], errors='coerce')
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        return df
    except Exception as e:
        st.sidebar.error(f"Error loading data: {e}")
        return pd.DataFrame()

df_live = load_data()

# Constants
TECH_MAP = {"Satish": "TECH-01", "Priyanshu": "TECH-02", "Amit": "TECH-03", "Ranjan": "TECH-04", "Manish": "TECH-05"}
OFFICIAL_LOCATIONS = ["Sector - 136 Vega", "Knitpro 28-29", "Sector - 155 Vega", "Knitpro - Jaipur", "Knitpro 42", "Knitpro 72-73", "Knitpro 75", "Bharat Composite Sector 80", "Vega Sector 80"]
STATUS_OPTIONS = ["Open", "In Progress", "On Hold - User Busy", "Resolved"]

# AI Suggestions
AI_SUGGESTIONS = {
    "CCTV/Camera": {"title_en": "📷 CCTV Fix Guide", "title_hi": "📷 सीसीटीवी फिक्स गाइड", "English": ["Check power status/POE Switch.", "Restart NVR system.", "Ping camera IP address."], "Hindi": ["पावर स्विच चेक करें।", "NVR रीस्टार्ट करें।", "IP पिंग करें।"]},
    "Laptop/Hardware": {"title_en": "💻 Laptop Fix Guide", "title_hi": "💻 लैपटॉप फिक्स गाइड", "English": ["Check charger connection.", "Perform a hard power reset.", "Run built-in BIOS diagnostics."], "Hindi": ["चार्जर चेक करें।", "हार्ड रीसेट करें।", "BIOS डायग्नोस्टिक चलाएं।"]},
    "Printer": {"title_en": "🖨️ Printer Fix Guide", "title_hi": "🖨️ प्रिंटर फिक्स गाइड", "English": ["Check power/cable interface.", "Clear jammed papers from tray.", "Reinstall latest print driver."], "Hindi": ["पावर केबल चेक करें।", "फंसा पेपर निकालें।", "ड्राइवर रीइंस्टॉल करें।"]},
}

def auto_categorize(text):
    t = str(text).lower()
    if any(k in t for k in ['cctv', 'camera']): return 'CCTV/Camera'
    elif any(k in t for k in ['laptop', 'desktop', 'pc', 'screen']): return 'Laptop/Hardware'
    elif any(k in t for k in ['outlook', 'email', 'mail']): return 'Email/Outlook'
    elif any(k in t for k in ['printer', 'print', 'xerox']): return 'Printer'
    elif any(k in t for k in ['sap', 'erp']): return 'SAP'
    elif any(k in t for k in ['network', 'wifi', 'internet', 'lan']): return 'Network'
    else: return 'Other'

# ===================== TABBED NAVIGATION =====================
tab_log, tab_view, tab_analysis, tab_monthly, tab_recurring = st.tabs([
    "🆕 Log New Ticket",
    "📋 View & Edit Tickets",
    "📊 Analysis Dashboard",
    "📅 Monthly Report",
    "🔄 Recurring Users"
])

# ===================== TAB 1: LOG NEW TICKET =====================
with tab_log:
    st.header("📋 Log New Ticket")
    form_col, ai_col = st.columns([1.1, 0.9])
    
    with form_col:
        with st.form("ticket_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                user_name = st.text_input("User Name *").strip()
                department = st.text_input("Department *").strip()
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
                    if db_connected:
                        try:
                            supabase.table("tickets").insert(new_row).execute()
                            st.success("✅ Ticket Saved to Supabase Cloud!")
                        except Exception as e:
                            st.error(f"Cloud Save Failed: {e}")
                    else:
                        st.success("✅ Ticket Saved Locally (Simulation Mode)")
                    st.rerun()
    
    with ai_col:
        st.subheader("🧠 AI Copilot Real-Time Assist")
        complaint_input = st.text_area("Type complaint description below to pull rapid fix guides:", height=150)
        lang = st.radio("Language Mode", ["English", "हिंदी"], horizontal=True)
        
        if st.button("💡 Get AI Suggestion", type="primary"):
            if complaint_input:
                cat = auto_categorize(complaint_input)
                st.markdown(f"**Auto-Detected Category:** `{cat}`")
                if cat in AI_SUGGESTIONS:
                    details = AI_SUGGESTIONS[cat]
                    title = details['title_en'] if lang == "English" else details['title_hi']
                    steps = details['English'] if lang == "English" else details['Hindi']
                    
                    st.markdown(f"""
                    <div class="ai-card">
                        <div class="ai-title">{title}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    for step in steps:
                        st.write(f"🔹 {step}")
                else:
                    st.info("ℹ️ Standard support parameters apply for this category. No direct rapid guide mapped.")
            else:
                st.warning("Please type a complaint description first.")

# ===================== TAB 2: VIEW & EDIT TICKETS =====================
with tab_view:
    st.header("📋 Live Ticket Registry")
    if df_live.empty:
        st.info("No logs present in system registry.")
    else:
        # Display clean view of current records
        st.dataframe(df_live.sort_values(by='id', ascending=False), use_container_width=True)
        st.write("---")
        
        st.subheader("⚙️ Update Existing Ticket")
        col_select, col_status, col_remarks = st.columns([1.5, 1, 2])
        
        # Build options mapping for intuitive picking (ID + Context)
        ticket_options = df_live.dropna(subset=['id']).sort_values(by='id', ascending=False)
        ticket_list = [int(x) for x in ticket_options['id'].tolist()]
        
        def get_ticket_label(tid):
            row = ticket_options[ticket_options['id'] == tid].iloc[0]
            return f"ID #{tid} | {row['user_name']} ({row['category']})"

        with col_select:
            selected_id = st.selectbox("Select Ticket Target", options=ticket_list, format_func=get_ticket_label)
        
        # Pull current state of chosen ticket to prepopulate update forms
        current_ticket = ticket_options[ticket_options['id'] == selected_id].iloc[0]
        
        with col_status:
            idx = STATUS_OPTIONS.index(current_ticket['status']) if current_ticket['status'] in STATUS_OPTIONS else 0
            new_status = st.selectbox("Modify Status", STATUS_OPTIONS, index=idx)
            
        with col_remarks:
            new_remarks = st.text_input("Append Remarks", value=str(current_ticket['remarks']) if pd.notna(current_ticket['remarks']) else "")

        if st.button("Update System Record", type="primary"):
            if db_connected:
                try:
                    supabase.table("tickets").update({
                        "status": new_status,
                        "remarks": new_remarks
                    }).eq("id", selected_id).execute()
                    st.success(f"Ticket #{selected_id} updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Database update failure: {e}")
            else:
                st.warning("Running in local mode. Action simulated.")

# ===================== TAB 3: ANALYSIS DASHBOARD =====================
with tab_analysis:
    st.header("📊 IT Operational Diagnostics Dashboard")
    if df_live.empty:
        st.info("Log active infrastructure incidents to populate analysis analytics charts.")
    else:
        # Executive KPI Cards
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        total_tickets = len(df_live)
        open_tickets = len(df_live[df_live['status'] == 'Open'])
        in_progress = len(df_live[df_live['status'] == 'In Progress'])
        resolved = len(df_live[df_live['status'] == 'Resolved'])
        
        kpi1.metric("Total Volumes Logged", total_tickets)
        kpi2.metric("Unassigned / Open", open_tickets, delta="- Action Needed" if open_tickets > 0 else "Clear", delta_color="inverse")
        kpi3.metric("Under Investigation", in_progress)
        kpi4.metric("Resolved Incidents", resolved)
        
        st.write("---")
        
        # Core Analytics Visualizations
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown("### 🏷️ Breakdown by Incident Category")
            st.bar_chart(df_live['category'].value_counts(), color="#3b82f6")
            
        with chart_col2:
            st.markdown("### 📍 Volume Across Operating Sectors / Sites")
            st.bar_chart(df_live['location'].value_counts(), color="#60a5fa")

# ===================== TAB 4: MONTHLY REPORT =====================
with tab_monthly:
    st.header("📅 Monthly Performance Reporting")
    if df_live.empty:
        st.info("Insufficient system transactional context to calculate historical operational cycles.")
    else:
        # Construct proper chronological groupings
        df_live['month_year'] = df_live['date'].dt.strftime('%Y-%m — %B')
        available_months = sorted(df_live['month_year'].dropna().unique().tolist(), reverse=True)
        
        target_month = st.selectbox("Select Target Operational Window", available_months)
        report_df = df_live[df_live['month_year'] == target_month].drop(columns=['month_year'])
        
        # Internal Metrics Breakdown for selected month
        rep_col1, rep_col2 = st.columns([1, 3])
        with rep_col1:
            st.markdown("#### **Quick Performance Stats**")
            st.write(f"**Total Incidents:** {len(report_df)}")
            st.write(f"**Resolution Rate:** {len(report_df[report_df['status'] == 'Resolved']) / len(report_df) * 100:.1f}%" if len(report_df) > 0 else "0%")
            
            # Category sublist
            st.write("**Top Category Issues:**")
            st.dataframe(report_df['category'].value_counts(), use_container_width=True)
            
        with rep_col2:
            st.markdown(f"#### **Incident Register Ledger — {target_month}**")
            st.dataframe(report_df, use_container_width=True)
            
            # Native Export Engine to CSV
            csv_data = report_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Monthly Report to CSV File",
                data=csv_data,
                file_name=f"IT_Incident_Report_{target_month.replace(' ', '')}.csv",
                mime='text/csv'
            )

# ===================== TAB 5: RECURRING USERS =====================
with tab_recurring:
    st.header("🔄 Recurring System Users & Fleet Analysis")
    if df_live.empty:
        st.info("Audit engine requires ongoing operations telemetry to process recurring user risk flags.")
    else:
        st.write("Identifies high-frequency reporters across Vega & Knitpro offices to uncover potential hardware batch degradation or training needs.")
        
        # Count frequencies
        user_aggregates = df_live['user_name'].value_counts().reset_index()
        user_aggregates.columns = ['User Employee Name', 'Total Incidents Logged']
        
        # Separate high risk repeat occurrences
        repeat_offenders = user_aggregates[user_aggregates['Total Incidents Logged'] > 1]
        
        col_list, col_history = st.columns([1, 2])
        
        with col_list:
            st.markdown("### ⚠️ Repeat Incident Callers (>1 Ticket)")
            if repeat_offenders.empty:
                st.success("✅ Clean Slate! No users have opened multiple support incidents yet.")
                user_inspection_list = user_aggregates['User Employee Name'].tolist()
            else:
                st.dataframe(repeat_offenders, use_container_width=True, hide_index=True)
                user_inspection_list = repeat_offenders['User Employee Name'].tolist()
                
        with col_history:
            st.markdown("### 🔍 Historical User Ticket Timeline Audit")
            if user_inspection_list:
                inspected_user = st.selectbox("Select Target Employee Context to Investigate", user_inspection_list)
                
                # Filter down user historical log trace
                user_timeline = df_live[df_live['user_name'] == inspected_user].sort_values(by='date', ascending=False)
                st.dataframe(user_timeline[['date', 'category', 'complaint', 'status', 'location', 'attended_by', 'remarks']], use_container_width=True, hide_index=True)
            else:
                st.info("No active users tracking inside registry.")

# Sidebar Status Display
st.sidebar.write("---")
st.sidebar.success("⚡ Supabase Connected Securely" if db_connected else "⚠️ Local Mode Active (Simulated Storage)")
