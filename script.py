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
            return df
        return pd.DataFrame(columns=[
            'id', 'date', 'user_name', 'department', 'complaint', 
            'location', 'attended_by', 'status', 'category', 
            'start_time', 'close_time', 'resolution_time'
        ])
    except Exception as e:
        st.error(f"⚠️ Failed to fetch live data from Supabase Cloud: {e}")
        return pd.DataFrame()

df_live = load_data()

# Sidebar Navigation
page = st.sidebar.selectbox("Navigation", 
    ["Log New Ticket", "View & Edit Tickets", "Analysis Dashboard", "Monthly Report", "Recurring Users"])

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
            st.markdown(f"**User:** {info['user']} ({info['dept']}) | **Handled By:** {info['tech']} | **Location:** {info['loc']}")
            st.caption(f"**Status:** {info['status']} | **Start:** {info['start']} | **End:** {info['close']} ({info['duration']} mins)")
            st.caption(f"**Description:** {info['desc']}")
            
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
                attended_by = st.selectbox("Attended By", ["Satish", "Priyanshu", "Amit", "Ranjan", "Manish"])
                status = st.selectbox("Status", ["Open", "In Progress", "Resolved"], index=0)
            
            complaint = st.text_area("Complaint Description *", height=100)
            
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
                        if duration_mins < 0:
                            duration_mins = 1
                    
                    new_row = {
                        'date': formatted_date, 'user_name': user_name,
                        'department': department, 'complaint': complaint, 'location': location,
                        'attended_by': attended_by, 'status': status, 'category': cat,
                        'start_time': start_val, 'close_time': close_val, 'resolution_time': duration_mins
                    }
                    
                    response = supabase.table("tickets").insert(new_row).execute()
                    new_id = response.data[0]['id']
                    
                    st.session_state.last_ticket_info = {
                        "id": new_id, "date": formatted_date, "category": cat,
                        "user": user_name, "dept": department, "tech": attended_by,
                        "loc": location, "desc": complaint, "status": status,
                        "start": start_val if start_val else "—", 
                        "close": close_val if close_val else "—", 
                        "duration": duration_mins
                    }
                    st.session_state.ticket_submitted = True
                    st.rerun()

# ===================== VIEW & EDIT TICKETS =====================
elif page == "View & Edit Tickets":
    st.header("📋 All Tickets")
    
    if not df_live.empty:
        df_sorted = df_live.sort_values(by='id', ascending=False).reset_index(drop=True)
        df_display = df_sorted.copy()
        df_display.insert(0, 'S.No.', range(1, len(df_display) + 1))
        
        for col in ['start_time', 'close_time']:
            if col in df_display.columns:
                df_display[col] = pd.to_datetime(df_display[col], errors='coerce').dt.strftime('%d-%m-%Y %H:%M').fillna('—')
                
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        col_edit, col_del = st.columns(2)
        
        with col_edit:
            st.markdown("### 🔄 Update Ticket Status")
            ticket_id = st.selectbox("Select Ticket ID to Update", df_live['id'].astype(int).tolist(), key="status_select")
            
            ticket_row = df_live[df_live['id'] == ticket_id].iloc[0]
            current_status = ticket_row['status']
            db_start_time = ticket_row['start_time']
            
            status_options = ["Open", "In Progress", "Resolved"]
            default_index = status_options.index(current_status) if current_status in status_options else 0
            new_status = st.selectbox("New Status", status_options, index=default_index)
            
            if st.button("Update Status", type="primary"):
                now_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                update_fields = {"status": new_status}
                
                if new_status == "In Progress":
                    update_fields["start_time"] = now_timestamp
                elif new_status == "Resolved":
                    final_start = db_start_time if (pd.notna(db_start_time) and db_start_time != "") else now_timestamp
                    try:
                        t1 = datetime.strptime(final_start, "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        t1 = datetime.now()
                    t2 = datetime.strptime(now_timestamp, "%Y-%m-%d %H:%M:%S")
                    duration_mins = max(1, int((t2 - t1).total_seconds() / 60))
                    
                    update_fields["start_time"] = final_start.split(".")[0]
                    update_fields["close_time"] = now_timestamp
                    update_fields["resolution_time"] = duration_mins
                else:
                    update_fields["start_time"] = ""
                    update_fields["close_time"] = ""
                    update_fields["resolution_time"] = 0
                    
                supabase.table("tickets").update(update_fields).eq("id", ticket_id).execute()
                st.success("✅ Status updated on cloud database successfully!")
                st.rerun()
                
        with col_del:
            st.markdown("### 🚨 Delete Mistaken Entry")
            del_ticket_id = st.selectbox("Select Ticket ID to Delete", df_live['id'].astype(int).tolist(), key="delete_select")
            target_user = df_live[df_live['id'] == del_ticket_id]['user_name'].values[0]
            st.warning(f"Warning: You are selecting Ticket #{del_ticket_id} logged by user: **{target_user}**.")
            
            confirm_delete = st.checkbox("I confirm that I want to delete this ticket permanently.")
            if confirm_delete:
                if st.button("❌ Permanently Delete Ticket", type="secondary"):
                    supabase.table("tickets").delete().eq("id", del_ticket_id).execute()
                    st.error("🗑️ Ticket purged from Supabase.")
                    st.rerun()
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
    st.header("📅 Monthly Performance Report")
    
    if not df_live.empty:
        df_live['Month'] = pd.to_datetime(df_live['date']).dt.strftime('%Y-%B')
        st.bar_chart(df_live.groupby('Month').size())
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            csv = df_live.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Full CSV Report", csv, "IT_Report.csv", "text/csv")
        with col2:
            summary = df_live.groupby(['Month', 'category', 'status']).size().reset_index(name='Counts')
            st.download_button("📥 Download Summary Report", summary.to_csv(index=False).encode('utf-8'), "Summary.csv", "text/csv")
    else:
        st.info("No logs found.")

# ===================== RECURRING USERS =====================
elif page == "Recurring Users":
    st.header("🔄 Top Recurring Users")
    if not df_live.empty:
        st.bar_chart(df_live['user_name'].value_counts().head(15))
    else:
        st.info("No analytical user maps matching criteria.")

st.sidebar.markdown("---")
st.sidebar.success("⚡ Live Cloud Node: Supabase Engine Active")
