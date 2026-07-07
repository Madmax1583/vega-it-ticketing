import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Vega IT System", layout="wide")
st.title("🛠️ Vega Group IT Ticketing & Analysis System")

# Database Setup
conn = sqlite3.connect('it_tickets.db', check_same_thread=False)
c = conn.cursor()

# Create table schema
c.execute('''CREATE TABLE IF NOT EXISTS tickets
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              date TEXT,
              user_name TEXT,
              department TEXT,
              complaint TEXT,
              location TEXT,
              attended_by TEXT,
              status TEXT,
              category TEXT,
              resolution_time INTEGER DEFAULT 0)''')
conn.commit()

# --- Database Migration Safeguard ---
# Safely add the resolution_time column if it doesn't exist in an older database
try:
    c.execute("SELECT resolution_time FROM tickets LIMIT 1")
except sqlite3.OperationalError:
    c.execute("ALTER TABLE tickets ADD COLUMN resolution_time INTEGER DEFAULT 0")
    conn.commit()

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
        st.success("🎉 **TICKET SUBMITTED SUCCESSFULLY!**")
        
        with st.container(border=True):
            col_a, col_b, col_c = st.columns(3)
            col_a.markdown(f"**Ticket ID:** #{info['id']}")
            col_b.markdown(f"**Date Assigned:** {info['date']}")
            col_c.markdown(f"**Category:** {info['category']}")
            
            st.markdown(f"**User:** {info['user']} ({info['dept']}) | **Handled By:** {info['tech']} | **Location:** {info['loc']}")
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
            
            complaint = st.text_area("Complaint Description *", height=150)
            
            if st.form_submit_button("Submit Ticket"):
                if not user_name or not complaint or not department or not location:
                    st.error("❌ Please fill out all required fields (*)")
                else:
                    cat = auto_categorize(complaint)
                    formatted_date = ticket_date.strftime("%Y-%m-%d")
                    
                    c.execute("""INSERT INTO tickets (date, user_name, department, complaint, location, attended_by, status, category, resolution_time)
                                 VALUES (?,?,?,?,?,?,?,?,0)""", 
                              (formatted_date, user_name, department, complaint, location, attended_by, status, cat))
                    conn.commit()
                    
                    st.session_state.last_ticket_info = {
                        "id": c.lastrowid,
                        "date": formatted_date,
                        "category": cat,
                        "user": user_name,
                        "dept": department,
                        "tech": attended_by,
                        "loc": location,
                        "desc": complaint
                    }
                    st.session_state.ticket_submitted = True
                    st.rerun()

# ===================== VIEW & EDIT TICKETS =====================
elif page == "View & Edit Tickets":
    st.header("📋 All Tickets")
    df = pd.read_sql_query("SELECT * FROM tickets ORDER BY id DESC", conn)
    
    if not df.empty:
        df_display = df.copy()
        df_display.insert(0, 'S.No.', range(1, len(df_display) + 1))
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        col_edit, col_del = st.columns(2)
        
        with col_edit:
            st.markdown("### 🔄 Update Ticket Status")
            ticket_id = st.selectbox("Select Ticket ID to Update", df['id'].tolist(), key="status_select")
            
            current_status = df[df['id'] == ticket_id]['status'].values[0]
            status_options = ["Open", "In Progress", "Resolved"]
            default_index = status_options.index(current_status) if current_status in status_options else 0
            
            new_status = st.selectbox("New Status", status_options, index=default_index)
            
            # Dynamic form input: only pops up if setting status to Resolved
            res_time = 0
            if new_status == "Resolved":
                res_time = st.number_input("Time spent to resolve (in Minutes)", min_value=1, max_value=1440, value=15)
                
            if st.button("Update Status", type="primary"):
                c.execute("UPDATE tickets SET status = ?, resolution_time = ? WHERE id = ?", (new_status, res_time, ticket_id))
                conn.commit()
                st.success(f"✅ Ticket #{ticket_id} updated to **{new_status}** ({res_time} mins)!")
                st.rerun()
                
        with col_del:
            st.markdown("### 🚨 Delete Mistaken Entry")
            del_ticket_id = st.selectbox("Select Ticket ID to Delete", df['id'].tolist(), key="delete_select")
            target_user = df[df['id'] == del_ticket_id]['user_name'].values[0]
            st.warning(f"Warning: You are selecting Ticket #{del_ticket_id} logged by user: **{target_user}**.")
            
            confirm_delete = st.checkbox("I confirm that I want to delete this ticket permanently.")
            if confirm_delete:
                if st.button("❌ Permanently Delete Ticket", type="secondary"):
                    c.execute("DELETE FROM tickets WHERE id = ?", (del_ticket_id,))
                    conn.commit()
                    st.error(f"🗑️ Ticket #{del_ticket_id} has been permanently deleted.")
                    st.rerun()
    else:
        st.info("No tickets recorded yet.")

# ===================== ANALYTICS DASHBOARD =====================
elif page == "Analysis Dashboard":
    st.header("📊 Executive Analysis Dashboard")
    df = pd.read_sql_query("SELECT * FROM tickets", conn)
    
    if not df.empty:
        # High Level Summary Cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total System Tickets", len(df))
        col2.metric("Active (Open/In Progress)", len(df[df['status'] != 'Resolved']))
        col3.metric("Resolved Tickets", len(df[df['status'] == 'Resolved']))
        
        resolved_df = df[df['status'] == 'Resolved']
        avg_time = int(resolved_df['resolution_time'].mean()) if not resolved_df.empty else 0
        col4.metric("Avg Resolution Time", f"{avg_time} Mins")
        
        st.markdown("---")
        
        # Technician Performance Layout
        st.subheader("👨‍💻 Technician Workload & Efficiency Analysis")
        tech_col1, tech_col2 = st.columns([1, 1])
        
        with tech_col1:
            st.markdown("**Total Ticket Load per Technician**")
            st.bar_chart(df['attended_by'].value_counts())
            
        with tech_col2:
            st.markdown("**Average Resolution Time per Technician (Minutes)**")
            if not resolved_df.empty:
                tech_time = resolved_df.groupby('attended_by')['resolution_time'].mean()
                st.bar_chart(tech_time)
            else:
                st.info("Log dynamic resolution times to reveal speed graphs.")
                
        st.markdown("---")
        
        # Location Wise Layout
        st.subheader("📍 Location & Sector-wise Breakdown")
        loc_col1, loc_col2 = st.columns([2, 1])
        
        with loc_col1:
            st.markdown("**Ticket Volume by Location**")
            st.bar_chart(df['location'].value_counts())
            
        with loc_col2:
            st.markdown("**Data Summary Table**")
            loc_summary = df.groupby(['location', 'status']).size().unstack(fill_value=0)
            st.dataframe(loc_summary, use_container_width=True)
            
    else:
        st.info("No data available to parse metric summaries yet.")

# ===================== MONTHLY REPORT =====================
elif page == "Monthly Report":
    st.header("📅 Monthly Performance Report")
    df = pd.read_sql_query("SELECT * FROM tickets", conn)
    
    if not df.empty:
        df['Month'] = pd.to_datetime(df['date']).dt.strftime('%Y-%B')
        
        st.subheader("Ticket Volume Trend")
        st.bar_chart(df.groupby('Month').size())
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Full Report (CSV)",
                data=csv,
                file_name=f"IT_Report_{datetime.now().strftime('%Y-%m')}.csv",
                mime="text/csv"
            )
        with col2:
            summary_df = df.groupby(['Month', 'category', 'status']).size().reset_index(name='Counts')
            summary_csv = summary_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Summary Report (CSV)",
                data=summary_csv,
                file_name=f"IT_Summary_{datetime.now().strftime('%Y-%m')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No tickets found to build reports.")

# ===================== RECURRING USERS =====================
elif page == "Recurring Users":
    st.header("🔄 Top Recurring Users")
    df = pd.read_sql_query("SELECT * FROM tickets", conn)
    
    if not df.empty:
        user_counts = df['user_name'].value_counts().head(15)
        if not user_counts.empty:
            st.bar_chart(user_counts)
        else:
            st.info("Not enough data to calculate recurring users.")
    else:
        st.info("No data recorded.")

# Footer info
st.sidebar.markdown("---")
st.sidebar.info("💾 Local Database Saved: `it_tickets.db`")
