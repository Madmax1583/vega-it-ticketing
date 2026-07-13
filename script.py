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

# ===================== HELPER FUNCTIONS =====================

def format_ticket_number(ticket_id, location_str):
    """
    Safely builds standard prefixes and converts IDs to clean integers.
    """
    try:
        clean_id = int(float(ticket_id))
        if pd.isna(location_str) or not location_str:
            return f"IT-2026-{clean_id:04d}"
            
        loc = str(location_str).lower()
        current_year = "2026"
        
        if "vega" in loc or "136" in loc or "155" in loc:
            prefix = "VEGA"
        elif "knitpro" in loc or "jaipur" in loc:
            prefix = "KP"
        else:
            prefix = "IT"
            
        return f"{prefix}-{current_year}-{clean_id:04d}"
    except Exception:
        try:
            fallback_id = int(float(ticket_id))
            return f"IT-2026-{fallback_id:04d}"
        except Exception:
            return f"IT-2026-{ticket_id}"

def load_data():
    try:
        response = supabase.table("tickets").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            # Standardize ID column immediately to integers
            df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
            df['resolution_time'] = pd.to_numeric(df['resolution_time'], errors='coerce').fillna(0).astype(int)
            
            if 'date' in df.columns:
                df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce')
            
            if 'remarks' not in df.columns: df['remarks'] = ""
            else: df['remarks'] = df['remarks'].fillna("")
                
            return df
        return pd.DataFrame(columns=[
            'id', 'date', 'user_name', 'department', 'complaint', 
            'location', 'attended_by', 'status', 'category', 
            'start_time', 'close_time', 'resolution_time', 'remarks'
        ])
    except Exception as e:
        st.error(f"⚠️ Failed to fetch live data from Supabase Cloud: {e}")
        return pd.DataFrame()

# ===================== DATA INITIALIZATION =====================
df_live = load_data()

# Master Configuration Constants
TECH_MAP = {
    "Satish": "TECH-01",
    "Priyanshu": "TECH-02",
    "Amit": "TECH-03",
    "Ranjan": "TECH-04",
    "Manish": "TECH-05"
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
    "Vega Sector 80"
]

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

# Sidebar Navigation Control
page = st.sidebar.selectbox("Navigation", 
    ["Log New Ticket", "View & Edit Tickets", "Analysis Dashboard", "Monthly Report", "Recurring Users"])

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
        
        formatted_id_string = format_ticket_number(info['id'], info['loc'])
        
        with st.container(border=True):
            col_a, col_b, col_c = st.columns(3)
            col_a.markdown(f"**Ticket Number:** `{formatted_id_string}`")
            col_b.markdown(f"**Date Assigned:** {info['date']}")
            col_c.markdown(f"**Category:** {info['category']}")
            st.markdown(f"**User:** {info['user']} ({info['dept']}) | **Handled By:** {info['tech']} ({info['tech_id']}) | **Location:** {info['loc']}")
            st.caption(f"**Status:** {info['status']} | **Start:** {info['start']} | **End:** {info['close']} ({info['duration']} mins)")
            st.markdown(f"**Action/Remarks:** {info['remarks']}")
            
        if st.button("Log Another Ticket", type="primary"):
            st.session_state.ticket_submitted = False
            st.rerun()
            
    else:
        if not df_live.empty and 'user_name' in df_live.columns:
            existing_users = sorted(df_live['user_name'].dropna().astype(str).unique().tolist())
        else:
            existing_users = []
            
        selected_user = st.selectbox("💡 Search Existing User Name to Auto-Fill Details", ["New User / Type Below"] + existing_users)
        
        default_user_name = ""
        default_dept = ""
        default_loc = ""
        
        if selected_user != "New User / Type Below" and not df_live.empty:
            default_user_name = selected_user
            user_history = df_live[df_live['user_name'] == selected_user].sort_values(by='id', ascending=False)
            if not user_history.empty:
                default_dept = str(user_history.iloc[0]['department'])
                default_loc = str(user_history.iloc[0]['location'])

        with st.form("ticket_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                user_name = st.text_input("User Name *", value=default_user_name)
                department = st.text_input("Department *", value=default_dept)
                
                loc_default = default_loc.lower() if default_loc else ""
                default_index = 0
                
                if "136" in loc_default: default_index = 0
                elif "28" in loc_default or "29" in loc_default: default_index = 1
                elif "155" in loc_default: default_index = 2
                elif "jaipur" in loc_default: default_index = 3
                elif "42" in loc_default: default_index = 4
                elif "72" in loc_default or "73" in loc_default: default_index = 5
                elif "75" in loc_default: default_index = 6
                elif "bharat" in loc_default: default_index = 7
                elif "vega" in loc_default and "80" in loc_default: default_index = 8
                
                location = st.selectbox(
                    "Location/Sector *", 
                    options=OFFICIAL_LOCATIONS, 
                    index=default_index
                )
            
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
                        start_val = None
                        close_val = None
                        duration_mins = None
                    elif status == "In Progress":
                        start_val = f"{formatted_date} {custom_start.strftime('%H:%M:%S')}"
                        close_val = None
                        duration_mins = None
                    elif status == "Resolved":
                        start_val = f"{formatted_date} {custom_start.strftime('%H:%M:%S')}"
                        close_val = f"{formatted_date} {custom_close.strftime('%H:%M:%S')}"
                        
                        t1 = datetime.combine(ticket_date, custom_start)
                        t2 = datetime.combine(ticket_date, custom_close)
                        duration_mins = int((t2 - t1).total_seconds() / 60)
                        if duration_mins < 0: duration_mins = 1
                    
                    new_row = {
                        'date': str(formatted_date), 
                        'user_name': str(user_name),
                        'department': str(department), 
                        'complaint': str(complaint), 
                        'location': str(location),
                        'attended_by': str(attended_by), 
                        'status': str(status), 
                        'category': str(cat),
                        'start_time': start_val, 
                        'close_time': close_val, 
                        'resolution_time': duration_mins,
                        'remarks': str(remarks)
                    }
                    
                    try:
                        response = supabase.table("tickets").insert(new_row).execute()
                        new_id = int(response.data[0]['id'])
                        
                        st.session_state.last_ticket_info = {
                            "id": new_id, "date": formatted_date, "category": cat,
                            "user": user_name, "dept": department, "tech": attended_by, "tech_id": tech_id_val,
                            "loc": location, "desc": complaint, "status": status,
                            "start": start_val if start_val else "—", 
                            "close": close_val if close_val else "—", 
                            "duration": duration_mins if duration_mins is not None else 0, 
                            "remarks": remarks if remarks else "No remarks left."
                        }
                        st.session_state.ticket_submitted = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Database Submission Error: {e}")

# ===================== VIEW & EDIT TICKETS =====================
elif page == "View & Edit Tickets":
    st.header("📋 All Tickets")
    
    if not df_live.empty:
        df_sorted = df_live.sort_values(by='id', ascending=False).reset_index(drop=True)
        df_display = df_sorted.copy()
        df_display.insert(0, 'S.No.', range(1, len(df_display) + 1))
        
        df_display['Ticket Number'] = df_display.apply(lambda row: format_ticket_number(row['id'], row['location']), axis=1)
        
        cols = list(df_display.columns)
        if 'Ticket Number' in cols:
            cols.insert(1, cols.pop(cols.index('Ticket Number')))
            df_display = df_display[cols]
        
        if 'date_parsed' in df_display.columns:
            df_display['date'] = df_display['date_parsed'].dt.strftime('%Y-%m-%d').fillna(df_display['date'])
            df_display.drop(columns=['date_parsed'], errors='ignore', inplace=True)
            
        if 'attended_by' in df_display.columns:
            df_display['Tech ID'] = df_display['attended_by'].map(TECH_MAP).fillna("—")
        
        for col in ['start_time', 'close_time']:
            if col in df_display.columns:
                df_display[col] = df_display[col].fillna('—')
                
        if 'Month_Year' in df_display.columns: df_display.drop(columns=['Month_Year'], errors='ignore', inplace=True)
                
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        col_edit, col_del = st.columns(2)
        
        with col_edit:
            st.markdown("### 🔄 Update Ticket Status & Action Remarks")
            
            # Extract raw integer IDs dynamically 
            valid_ids = sorted([int(x) for x in df_live['id'].dropna().unique()], reverse=True)
            
            if valid_ids:
                # FIXED: We use format_func so the selectbox holds cleaner structural data frames behind the scenes
                def get_edit_label(tid):
                    row = df_live[df_live['id'] == tid].iloc[0]
                    fmt_num = format_ticket_number(row['id'], row['location'])
                    return f"{fmt_num} (User: {row['user_name']})"
                
                ticket_id = st.selectbox(
                    "Select Ticket to Update", 
                    options=valid_ids, 
                    format_func=get_edit_label,
                    key="status_select"
                )
                
                ticket_row = df_live[df_live['id'] == ticket_id].iloc[0]
                current_status = ticket_row['status']
                db_start_time = ticket_row['start_time']
                current_remarks = ticket_row['remarks']
                current_tech = ticket_row['attended_by']
                current_loc = ticket_row.get('location', '')
                
                status_options = ["Open", "In Progress", "Resolved"]
                default_index = status_options.index(current_status) if current_status in status_options else 0
                new_status = st.selectbox("New Status", status_options, index=default_index)
                
                new_tech = st.selectbox("Reassign Technician (Optional)", list(TECH_MAP.keys()), index=list(TECH_MAP.keys()).index(current_tech) if current_tech in TECH_MAP else 0)
                
                default_loc_idx = OFFICIAL_LOCATIONS.index(current_loc) if current_loc in OFFICIAL_LOCATIONS else 0
                new_location = st.selectbox("Update Location/Sector", OFFICIAL_LOCATIONS, index=default_loc_idx)
                
                new_remarks = st.text_area("Update Action Remarks", value=current_remarks, height=80)
                
                if st.button("Update Status & Remarks", type="primary"):
                    now_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    update_fields = {
                        "status": str(new_status), 
                        "remarks": str(new_remarks), 
                        "attended_by": str(new_tech),
                        "location": str(new_location)
                    }
                    
                    if new_status == "In Progress":
                        update_fields["start_time"] = now_timestamp
                    elif new_status == "Resolved":
                        final_start = db_start_time if (pd.notna(db_start_time) and db_start_time != "" and db_start_time != "—") else now_timestamp
                        try:
                            t1 = datetime.strptime(str(final_start).split(".")[0], "%Y-%m-%d %H:%M:%S")
                        except Exception:
                            t1 = datetime.now()
                        t2 = datetime.strptime(now_timestamp, "%Y-%m-%d %H:%M:%S")
                        duration_mins = max(1, int((t2 - t1).total_seconds() / 60))
                        
                        update_fields["start_time"] = str(final_start).split(".")[0]
                        update_fields["close_time"] = now_timestamp
                        update_fields["resolution_time"] = duration_mins
                    
                    supabase.table("tickets").update(update_fields).eq("id", ticket_id).execute()
                    st.success("✅ Ticket metrics updated successfully!")
                    st.rerun()
            else:
                st.info("No options available.")
                
        with col_del:
            st.markdown("### 🚨 Delete Mistaken Entry")
            del_ids = sorted([int(x) for x in df_live['id'].dropna().unique()], reverse=True)
            
            if del_ids:
                def get_del_label(tid):
                    row = df_live[df_live['id'] == tid].iloc[0]
                    fmt_num = format_ticket_number(row['id'], row['location'])
                    return f"{fmt_num} (User: {row['user_name']})"
                
                del_ticket_id = st.selectbox(
                    "Select Ticket to Delete", 
                    options=del_ids, 
                    format_func=get_del_label,
                    key="delete_select"
                )
                
                target_user = df_live[df_live['id'] == del_ticket_id]['user_name'].values[0]
                st.warning(f"Warning: You are selecting Ticket #{del_ticket_id} logged by user: **{target_user}**.")
                
                confirm_delete = st.checkbox("I confirm that I want to delete this ticket permanently.")
                if confirm_delete:
                    if st.button("❌ Permanently Delete Ticket", type="secondary"):
                        supabase.table("tickets").delete().eq("id", del_ticket_id).execute()
                        st.error("🗑️ Ticket purged from Supabase.")
                        st.rerun()
            else:
                st.info("No entries to drop.")
    else:
        st.info("No tickets recorded yet.")

# ===================== ANALYTICS DASHBOARD =====================
elif page == "Analysis Dashboard":
    st.header("📊 Executive Analysis Dashboard")
    
    if not df_live.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total System Tickets", len(df_live))
        col2.metric("Active Tickets", len(df_live[df_live['status'] != 'Resolved']))
        col3.metric("Resolved Tickets", len(df_live[df_live['status'] == 'Resolved']))
        
        resolved_df = df_live[df_live['status'] == 'Resolved']
        avg_time = int(resolved_df['resolution_time'].mean()) if not resolved_df.empty else 0
        col4.metric("Avg Resolution Time", f"{avg_time} Mins")
        
        st.markdown("---")
        st.subheader("👨‍💻 Technician Workload & Efficiency")
        tech_col1, tech_col2 = st.columns(2)
        with tech_col1:
            st.bar_chart(df_live['attended_by'].value_counts())
        with tech_col2:
            if not resolved_df.empty:
                st.bar_chart(resolved_df.groupby('attended_by')['resolution_time'].mean())
            else:
                st.info("No timeline matrix tracked yet.")
                
        st.markdown("---")
        st.subheader("📍 Location Breakdown")
        loc_col1, loc_col2 = st.columns([2, 1])
        with loc_col1:
            st.bar_chart(df_live['location'].value_counts())
        with loc_col2:
            if 'Open' in df_live['status'].values or 'In Progress' in df_live['status'].values or 'Resolved' in df_live['status'].values:
                st.dataframe(df_live.groupby(['location', 'status']).size().unstack(fill_value=0), use_container_width=True)
    else:
        st.info("No metrics mapped yet.")

# ===================== MONTHLY REPORT =====================
elif page == "Monthly Report":
    st.header("📅 Cloud Enhanced Performance Reports")
    
    if not df_live.empty:
        if 'date_parsed' in df_live.columns:
            df_live['Month_Year'] = df_live['date_parsed'].dt.strftime('%Y-%B')
        else:
            df_live['Month_Year'] = "Unknown Month"
            
        unique_months = sorted(df_live['Month_Year'].dropna().unique())
        selected_month = st.selectbox("🎯 Select Reporting Month", ["All Time"] + unique_months)
        
        if selected_month == "All Time":
            report_df = df_live.copy()
        else:
            report_df = df_live[df_live['Month_Year'] == selected_month]
            
        st.markdown("### 📊 Month Summary Key Identifiers")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        
        total_m = len(report_df)
        resolved_m = len(report_df[report_df['status'] == 'Resolved'])
        pending_m = total_m - resolved_m
        avg_res_m = int(report_df[report_df['status'] == 'Resolved']['resolution_time'].mean()) if resolved_m > 0 else 0
        
        m_col1.metric("Tickets Processed", total_m)
        m_col2.metric("Tickets Resolved ✅", resolved_m)
        m_col3.metric("Tickets Pending ⚠️", pending_m)
        m_col4.metric("Avg Closure Velocity", f"{avg_res_m} Mins")
        
        st.markdown("---")
        
        v_col1, v_col2 = st.columns(2)
        with v_col1:
            st.markdown("#### 📁 Volume by Issue Category")
            if not report_df.empty:
                st.bar_chart(report_df['category'].value_counts())
            else:
                st.caption("No data available.")
                
        with v_col2:
            st.markdown("#### 🛠️ Team SLA Breakdown (Avg Mins to Resolve)")
            resolved_subset = report_df[report_df['status'] == 'Resolved']
            if not resolved_subset.empty:
                st.bar_chart(resolved_subset.groupby('attended_by')['resolution_time'].mean())
            else:
                st.info("No resolved items in this timeframe to compute SLA speed.")
                
        st.markdown("---")
        st.markdown("### 📋 Executive Summary Table")
        
        if not report_df.empty:
            summary_table = report_df.groupby(['category', 'status']).size().unstack(fill_value=0)
            st.dataframe(summary_table, use_container_width=True)
        
        st.markdown("#### 📥 Secure Cloud Export")
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            csv_export_df = report_df.copy()
            if 'date_parsed' in csv_export_df.columns:
                csv_export_df.drop(columns=['date_parsed', 'Month_Year'], errors='ignore', inplace=True)
            csv_data = csv_export_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Targeted CSV Data Set",
                data=csv_data,
                file_name=f"IT_Report_{selected_month.replace('-', '_')}.csv",
                mime="text/csv",
                type="primary"
            )
        with col_dl2:
            st.caption("This data set includes automated categories, technician resolution notes, unique user IDs, and timeline metric durations.")
    else:
        st.info("No active production tickets detected on cloud nodes to parse reports from.")

# ===================== RECURRING USERS =====================
elif page == "Recurring Users":
    st.header("🔄 Top Recurring Users")
    if not df_live.empty:
        st.bar_chart(df_live['user_name'].value_counts().head(15))
    else:
        st.info("No analytical user maps matching criteria.")

st.sidebar.markdown("---")
st.sidebar.success("⚡ Live Cloud Node: Supabase Engine Active")
