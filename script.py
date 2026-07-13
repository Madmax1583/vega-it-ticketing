import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

st.set_page_config(page_title="Vega & Knitpro IT Ticketing", layout="wide")

# Custom Styling
st.markdown("""
<style>
    .ai-card {background-color: #1e293b; border-left: 5px solid #3b82f6; padding: 18px; border-radius: 8px; margin: 10px 0;}
    .ai-title {color: #60a5fa; font-weight: bold; font-size: 1.15rem;}
    .report-stat-box {background-color: #0f172a; border: 1px solid #1e293b; padding: 15px; border-radius: 6px; text-align: center;}
</style>
""", unsafe_allow_html=True)

# ===================== LOGOS & HEADER =====================
col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    try:
        st.image("vega_logo.png", width=150)
    except:
        st.caption("🔺 Vega Workspace")
with col2:
    try:
        st.image("knitpro_logo.png", width=150)
    except:
        st.caption("🔺 Knitpro Manufacturing")
with col3:
    st.title("🛠️ Vega & Knitpro IT Ticketing & Analysis System")

# ===================== DATABASE CONFIGURATION =====================
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.sidebar.warning("⚠️ Supabase Credentials Missing. Local Mode Active.")
        return None

supabase = init_supabase()
db_connected = supabase is not None

def load_data():
    if not db_connected: 
        return pd.DataFrame(columns=['id', 'date', 'user_name', 'department', 'complaint', 'location', 'attended_by', 'status', 'category', 'remarks'])
    try:
        response = supabase.table("tickets").select("*").order("id", desc=True).execute()
        df = pd.DataFrame(response.data) if response.data else pd.DataFrame()
        if not df.empty:
            df['id'] = pd.to_numeric(df['id'], errors='coerce')
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        return df
    except Exception as e:
        st.sidebar.error(f"Data Connection Error: {e}")
        return pd.DataFrame()

df_live = load_data()

# ===================== GLOBAL SYSTEM CONSTANTS =====================
TECH_MAP = {"Satish": "TECH-01", "Priyanshu": "TECH-02", "Amit": "TECH-03", "Ranjan": "TECH-04", "Manish": "TECH-05"}
OFFICIAL_LOCATIONS = ["Sector - 136 Vega", "Knitpro 28-29", "Sector - 155 Vega", "Knitpro - Jaipur", "Knitpro 42", "Knitpro 72-73", "Knitpro 75", "Bharat Composite Sector 80", "Vega Sector 80"]
STATUS_OPTIONS = ["Open", "In Progress", "On Hold - User Busy", "Resolved"]

AI_SUGGESTIONS = {
    "CCTV/Camera": {"title_en": "📷 CCTV Fix Guide", "title_hi": "📷 सीसीटीवी फिक्स गाइड", "English": ["Verify main POE switch status", "Power cycle the NVR system", "Ping destination camera network IP"], "Hindi": ["मुख्य POE स्विच चेक करें", "NVR सिस्टम रीस्टार्ट करें", "कैमरा IP नेटवर्क पिंग करें"]},
    "Laptop/Hardware": {"title_en": "💻 Laptop Fix Guide", "title_hi": "💻 लैपटॉप फिक्स गाइड", "English": ["Check adapter power throughput", "Perform static-charge hard reset", "Execute hardware diagnostic engine"], "Hindi": ["चार्जर वोल्टेज चेक करें", "स्टैटिक चार्ज हटाने के लिए हार्ड रीसेट करें", "हार्डवेयर डायग्नोस्टिक चलाएं"]},
    "Printer": {"title_en": "🖨️ Printer Fix Guide", "title_hi": "🖨️ प्रिंटर फिक्स गाइड", "English": ["Confirm data communication cable link", "Clear mechanical paper jams from feeder", "Purge print queue & refresh driver"], "Hindi": ["डेटा केबल कनेक्शन चेक करें", "पेपर फीडर से फंसा कागज निकालें", "प्रिंट कतार क्लियर कर ड्राइवर रीफ्रेश करें"]},
}

def auto_categorize(text):
    t = str(text).lower()
    if any(k in t for k in ['cctv', 'camera', 'dvr', 'nvr']): return 'CCTV/Camera'
    elif any(k in t for k in ['laptop', 'desktop', 'pc', 'monitor', 'keyboard']): return 'Laptop/Hardware'
    elif any(k in t for k in ['outlook', 'email', 'mail', 'pop3']): return 'Email/Outlook'
    elif any(k in t for k in ['printer', 'print', 'scanner', 'xerox']): return 'Printer'
    elif any(k in t for k in ['sap', 'erp', 'tcode']): return 'SAP'
    elif any(k in t for k in ['network', 'wifi', 'lan', 'internet', 'switch']): return 'Network'
    else: return 'Other'

# ===================== NAVIGATION SYSTEM =====================
tab_log, tab_view, tab_analysis, tab_monthly, tab_recurring = st.tabs([
    "🆕 Log New Ticket",
    "📋 View & Edit Tickets",
    "📊 Analysis Dashboard",
    "📥 Advanced Reporting Center",
    "🔄 Recurring Users"
])

# ===================== TAB 1: LOG NEW TICKET =====================
with tab_log:
    st.header("📋 Log New Operations Ticket")
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
                status = st.selectbox("Initial Status", STATUS_OPTIONS)
            
            complaint = st.text_area("Complaint Description *", height=100)
            remarks = st.text_area("Technician Operational Remarks", height=80)
            
            if st.form_submit_button("Submit Ticket"):
                if not user_name or not complaint:
                    st.error("❌ Please provide input for all required fields (*)")
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
                            st.success("✅ Ticket Synced to Cloud Securely!")
                        except Exception as e:
                            st.error(f"Database sync fault: {e}")
                    else:
                        st.success("✅ Ticket Buffered Locally (Simulation Mode)")
                    st.rerun()
    
    with ai_col:
        st.subheader("🧠 AI Copilot Diagnostics")
        complaint_input = st.text_area("Type complaint scenario details to extract rapid triage steps:", height=150)
        lang = st.radio("Output Language Target", ["English", "हिंदी"], horizontal=True)
        
        if st.button("💡 Parse Issue Parameters", type="primary"):
            if complaint_input:
                cat = auto_categorize(complaint_input)
                st.markdown(f"**Identified Vector Class:** `{cat}`")
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
                    st.info("ℹ️ Standard operating protocol applies. No direct rapid card matches this vector.")
            else:
                st.warning("Please describe the technical breakdown environment first.")

# ===================== TAB 2: VIEW & EDIT TICKETS =====================
with tab_view:
    st.header("📋 Current Ticket Registry Ledger")
    if df_live.empty:
        st.info("No active service events populated inside system memory registry.")
    else:
        st.dataframe(df_live.sort_values(by='id', ascending=False), use_container_width=True)
        st.write("---")
        
        st.subheader("⚙️ Update Active Ticket Status Context")
        
        clean_options = df_live.dropna(subset=['id']).sort_values(by='id', ascending=False)
        ticket_id_list = [int(x) for x in clean_options['id'].tolist()]
        
        def format_selector_dropdown(tid):
            match_row = clean_options[clean_options['id'] == tid].iloc[0]
            return f"Ticket #{tid} — {match_row['user_name']} ({match_row['category']})"
            
        col_select, col_status, col_remarks = st.columns([1.5, 1, 2.5])
        
        with col_select:
            ticket_target = st.selectbox("Select Target Event Identity", options=ticket_id_list, format_func=format_selector_dropdown)
            
        current_state = clean_options[clean_options['id'] == ticket_target].iloc[0]
        
        with col_status:
            default_status_idx = STATUS_OPTIONS.index(current_state['status']) if current_state['status'] in STATUS_OPTIONS else 0
            updated_status = st.selectbox("Change Current Status", STATUS_OPTIONS, index=default_status_idx)
            
        with col_remarks:
            updated_remarks = st.text_input("Modify/Append Operational Notes", value=str(current_state['remarks']) if pd.notna(current_state['remarks']) else "")
            
        if st.button("Commit Ledger Adjustments", type="primary"):
            if db_connected:
                try:
                    supabase.table("tickets").update({
                        "status": updated_status,
                        "remarks": updated_remarks
                    }).eq("id", ticket_target).execute()
                    st.success(f"System modifications successfully saved to Ticket #{ticket_target}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Ledger adjustment failure: {e}")
            else:
                st.warning("Running without remote database backend. Action simulated.")

# ===================== TAB 3: ANALYSIS DASHBOARD =====================
with tab_analysis:
    st.header("📊 High-Level Infrastructure Analytics")
    if df_live.empty:
        st.info("Insufficient metrics available to compute visual breakdown trends.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Infrastructure Logs", len(df_live))
        c2.metric("Open Backlog Requests", len(df_live[df_live['status'] == 'Open']))
        c3.metric("Under Active Triage", len(df_live[df_live['status'] == 'In Progress']))
        c4.metric("Successfully Resolved", len(df_live[df_live['status'] == 'Resolved']))
        st.write("---")
        
        chart_left, chart_right = st.columns(2)
        with chart_left:
            st.markdown("#### **Distribution by Problem Classification**")
            st.bar_chart(df_live['category'].value_counts(), color="#3b82f6")
        with chart_right:
            st.markdown("#### **Volume Map by Plant Location/Office Site**")
            st.bar_chart(df_live['location'].value_counts(), color="#60a5fa")

# ===================== TAB 4: ADVANCED REPORTING CENTER =====================
with tab_monthly:
    st.header("📥 Advanced Operational Data Reporting Center")
    st.write("Filter, evaluate, and extract telemetry datasets grouped by specific parameters.")
    
    if df_live.empty:
        st.info("Ledger records empty. Reporting functions unavailable.")
    else:
        report_type = st.selectbox("Select Target Extraction Layout Strategy", 
            ["Overall Analytics Summary", "Monthly Report View", "Weekly Report View", "Location-Wise Audit", "Technician Performance Profile"])
        st.write("---")

        if report_type == "Overall Analytics Summary":
            st.subheader("Core Site Analytics Summary Matrix")
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("Total Incident Operations Count", len(df_live))
            col_m2.metric("Total System Remediations Completed", len(df_live[df_live['status'] == 'Resolved']))
            col_m3.metric("Remaining Backlog Count", len(df_live[df_live['status'] == 'Open']))
            
            if 'resolution_time' in df_live.columns and not df_live['resolution_time'].dropna().empty:
                avg_res = f"{int(df_live['resolution_time'].mean())} minutes"
            else:
                avg_res = "No runtime logs available"
            col_m4.metric("Avg Remediation Velocity", avg_res)
            
            chart1, chart2 = st.columns(2)
            with chart1:
                st.markdown("##### **Total Issues Logged by Category**")
                st.bar_chart(df_live['category'].value_counts(), color="#2563eb")
            with chart2:
                st.markdown("##### **Tickets Managed per Assignee**")
                st.bar_chart(df_live['attended_by'].value_counts(), color="#1d4ed8")

        elif report_type == "Monthly Report View":
            df_live['Month_Group'] = df_live['date'].dt.strftime('%Y-%m (%B)')
            month_selections = sorted(df_live['Month_Group'].dropna().unique(), reverse=True)
            chosen_month = st.selectbox("Choose Target Evaluation Month", month_selections)
            
            filtered_dataset = df_live[df_live['Month_Group'] == chosen_month].drop(columns=['Month_Group'])
            st.dataframe(filtered_dataset, use_container_width=True)
            
            csv_payload = filtered_dataset.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Selected Monthly Dataset", csv_payload, f"IT_Monthly_Log_{chosen_month}.csv", "text/csv")

        elif report_type == "Weekly Report View":
            df_live['Week_Group'] = df_live['date'].dt.strftime('%Y-W%U')
            week_selections = sorted(df_live['Week_Group'].dropna().unique(), reverse=True)
            chosen_week = st.selectbox("Choose Target Evaluation Week", week_selections)
            
            filtered_dataset = df_live[df_live['Week_Group'] == chosen_week].drop(columns=['Week_Group'])
            st.dataframe(filtered_dataset, use_container_width=True)
            
            csv_payload = filtered_dataset.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Selected Weekly Dataset", csv_payload, f"IT_Weekly_Log_{chosen_week}.csv", "text/csv")

        elif report_type == "Location-Wise Audit":
            chosen_location = st.selectbox("Choose Target Physical Plant/Sector", df_live['location'].unique())
            
            filtered_dataset = df_live[df_live['location'] == chosen_location]
            st.dataframe(filtered_dataset, use_container_width=True)
            
            csv_payload = filtered_dataset.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Location Site Report", csv_payload, f"IT_Location_Log_{chosen_location.replace(' ', '_')}.csv", "text/csv")

        elif report_type == "Technician Performance Profile":
            chosen_tech = st.selectbox("Choose Target Dispatch Staff Identity", df_live['attended_by'].unique())
            
            filtered_dataset = df_live[df_live['attended_by'] == chosen_tech]
            
            col_t1, col_t2 = st.columns([1, 3])
            with col_t1:
                st.markdown(f"##### **Profile: {chosen_tech}**")
                st.write(f"**Total Assigned Calls:** {len(filtered_dataset)}")
                resolved_count = len(filtered_dataset[filtered_dataset['status'] == 'Resolved'])
                st.write(f"**Resolved Tasks Count:** {resolved_count}")
                efficiency_ratio = (resolved_count / len(filtered_dataset) * 100) if len(filtered_dataset) > 0 else 0
                st.write(f"**Operational Resolution Rate:** {efficiency_ratio:.1f}%")
            with col_t2:
                st.dataframe(filtered_dataset, use_container_width=True)
                
            csv_payload = filtered_dataset.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Technician Case History File", csv_payload, f"IT_Tech_Log_{chosen_tech}.csv", "text/csv")

# ===================== TAB 5: RECURRING USERS =====================
with tab_recurring:
    st.header("🔄 Repeated Incident call Profiles & Deep Diagnostics")
    if df_live.empty:
        st.info("No network event data available to extract caller correlation maps.")
    else:
        st.write("Identifies employees filing recurring support requests. This highlights training needs or faulty hardware.")
        
        user_metrics_summary = df_live['user_name'].value_counts().reset_index()
        user_metrics_summary.columns = ['Employee Identity', 'Total Logged Call Incidents']
        
        repeat_callers_df = user_metrics_summary[user_metrics_summary['Total Logged Call Incidents'] > 1]
        
        layout_left, layout_right = st.columns([1, 2])
        
        with layout_left:
            st.markdown("##### **Repeat Call Profiling Flag Registry (>1 Ticket)**")
            if repeat_callers_df.empty:
                st.success("✅ Excellent! No users have raised multiple support tickets.")
                active_investigation_list = user_metrics_summary['Employee Identity'].tolist()
            else:
                st.dataframe(repeat_callers_df, use_container_width=True, hide_index=True)
                active_investigation_list = repeat_callers_df['Employee Identity'].tolist()
                
        with layout_right:
            st.markdown("##### 🔍 Historic Timeline Diagnostics Engine")
            if active_investigation_list:
                selected_audit_target = st.selectbox("Select Target Employee Context to Investigate Profile History", active_investigation_list)
                user_case_history = df_live[df_live['user_name'] == selected_audit_target].sort_values(by='date', ascending=False)
                st.dataframe(user_case_history[['date', 'category', 'complaint', 'status', 'location', 'remarks']], use_container_width=True, hide_index=True)
            else:
                st.info("No operational user signatures recognized in system record logs.")

# Sync Confirmation Sidebar Monitor
st.sidebar.write("---")
st.sidebar.success("⚡ Supabase Remote Datastore Online" if db_connected else "⚠️ Local Storage Runtime Emulation Mode Active")
