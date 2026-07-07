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

c.execute('''CREATE TABLE IF NOT EXISTS tickets
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              date TEXT,
              user_name TEXT,
              department TEXT,
              complaint TEXT,
              location TEXT,
              attended_by TEXT,
              status TEXT,
              category TEXT)''')
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
            
            st.markdown(f"**User:** {info['user']} ({info['dept']}) | **Handled By:** {info['tech']}")
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
                location = st.text_input("Location/Sector")
            with col2:
                ticket_date = st.date_input("Ticket Date *", value=datetime.now().date())
                attended_by = st.selectbox("Attended By", ["Satish", "Priyanshu", "Amit", "Ranjan", "Manish"])
                status = st.selectbox("Status", ["Open", "In Progress", "Resolved"], index=0)
            
            complaint = st.text_area("Complaint Description *", height=150)
            
            if st.form_submit_button("Submit Ticket"):
                if not user_name or not complaint or not department:
                    st.error("❌ Please fill out all required fields (*)")
                else:
                    cat = auto_categorize(complaint)
                    formatted_date = ticket_date.strftime("%Y-%m-%d")
                    
                    c.execute("""INSERT INTO tickets (date, user_name, department, complaint, location, attended_by, status, category)
                                 VALUES (?,?,?,?,?,?,?,?)""", 
                              (formatted_date, user_name, department, complaint, location, attended_by, status, cat))
                    conn.commit()
                    
                    st.session_state.last_ticket_info = {
                        "id": c.lastrowid,
                        "date": formatted_date,
                        "category": cat,
                        "user": user_name,
                        "dept": department,
                        "tech": attended_by,
                        "desc": complaint
                    }
                    st.session_state.ticket_submitted = True
                    st.rerun()

# ===================== VIEW & EDIT TICKETS =====================
elif page == "View & Edit Tickets":
    st.header("📋 All Tickets")
    df = pd.read_sql_query("SELECT * FROM tickets ORDER BY id DESC", conn)
    
    if not df.empty:
        # Create a clean visual copy and insert a dynamic visual counter (S.No.)
        df_display = df.copy()
        df_display.insert(0, 'S.No.', range(1, len(df_display) + 1))
        
        # Display the modified table and hide the messy Pandas index (0, 1, 2...)
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # UI Split columns for Managing Status vs Deleting Tickets
        col_edit, col_del = st.columns(2)
        
        with col_edit:
            st.markdown("### 🔄 Update Ticket Status")
            # We still use the real database 'id' here behind the scenes for accuracy
            ticket_id = st.selectbox("Select Ticket ID to Update", df['id'].tolist(), key="status_select")
            
            current_status = df[df['id'] == ticket_id]['status'].values[0]
            status_options = ["Open", "In Progress", "Resolved"]
            default_index = status_options.index(current_status) if current_status in status_options else 0
            
            new_status = st.selectbox("New Status", status_options, index=default_index)
                
            if st.button("Update Status", type="primary"):
                c.execute("UPDATE tickets SET status = ? WHERE id = ?", (new_status, ticket_id))
                conn.commit()
                st.success(f"✅ Ticket #{ticket_id} updated to **{new_status}**!")
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

# ===================== ANALYTICS PAGES =====================
else:
    df = pd.read_sql_query("SELECT * FROM tickets", conn)
    if not df.empty:
        if page == "Analysis Dashboard":
            st.header("📊 Analysis Dashboard")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Tickets", len(df))
            col2.metric("Open Tickets", len(df[df['status'] == 'Open']))
            col3.metric("Resolved Tickets", len(df[df['status'] == 'Resolved']))
            
            st.subheader("Tickets by Category")
            st.bar_chart(df['category'].value_counts())

        elif page == "Monthly Report":
            st.header("📅 Monthly Report")
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

        elif page == "Recurring Users":
            st.header("🔄 Top Recurring Users")
            user_counts = df['user_name'].value_counts().head(15)
            if not user_counts.empty:
                st.bar_chart(user_counts)
            else:
                st.info("Not enough data to calculate recurring users.")
    else:
        st.info("No data available to show. Please log some tickets first.")

# Footer info
st.sidebar.markdown("---")
st.sidebar.info("💾 Local Database Saved: `it_tickets.db`")
