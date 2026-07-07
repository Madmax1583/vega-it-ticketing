import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Vega IT System", layout="wide")
st.title("🛠️ Vega Group IT Ticketing & Analysis System")

# Database Connection
conn = sqlite3.connect('it_tickets.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS tickets
             (
                 id
                 INTEGER
                 PRIMARY
                 KEY
                 AUTOINCREMENT,
                 date
                 TEXT,
                 user_name
                 TEXT,
                 department
                 TEXT,
                 complaint
                 TEXT,
                 location
                 TEXT,
                 attended_by
                 TEXT,
                 status
                 TEXT,
                 category
                 TEXT
             )''')
conn.commit()

# Navigation
page = st.sidebar.selectbox("Navigation",
                            ["Log New Ticket", "View & Edit Tickets", "Analysis Dashboard", "Monthly Report",
                             "Recurring Users"])


def auto_categorize(complaint):
    text = str(complaint).lower()
    if any(k in text for k in ['cctv', 'camera', 'nvr']):
        return 'CCTV/Camera'
    elif any(k in text for k in ['laptop', 'desktop', 'keyboard', 'touchpad', 'battery', 'hinge', 'screen']):
        return 'Laptop/Hardware'
    elif any(k in text for k in ['outlook', 'email', 'mail', 'pst']):
        return 'Email/Outlook'
    elif any(k in text for k in ['printer', 'scanner', 'cartridge']):
        return 'Printer'
    elif any(k in text for k in ['sap']):
        return 'SAP'
    elif any(k in text for k in ['network', 'wifi', 'internet', 'vpn']):
        return 'Network'
    elif any(k in text for k in ['ups', 'server', 'backup', 'nas']):
        return 'Server/UPS'
    else:
        return 'Other'


# ===================== LOG NEW TICKET =====================
if page == "Log New Ticket":
    st.header("📋 Log New Ticket")
    with st.form("ticket_form"):
        col1, col2 = st.columns(2)
        with col1:
            user_name = st.text_input("User Name *")
            department = st.text_input("Department *")
            location = st.text_input("Location/Sector")
        with col2:
            attended_by = st.selectbox("Attended By", ["Satish", "Priyanshu", "Amit"])
            status = st.selectbox("Status", ["Open", "In Progress", "Resolved"], index=0)

        complaint = st.text_area("Complaint Description *", height=150)
        st.info(f"**Auto Category:** {auto_categorize(complaint) if complaint else '—'}")

        if st.form_submit_button("Submit Ticket") and user_name and complaint:
            cat = auto_categorize(complaint)
            c.execute("""INSERT INTO tickets
                         (date, user_name, department, complaint, location, attended_by, status, category)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                      (datetime.now().strftime("%Y-%m-%d"), user_name, department, complaint,
                       location, attended_by, status, cat))
            conn.commit()
            st.success(f"✅ Ticket Logged Successfully! (Category: **{cat}**)")
            st.rerun()

# ===================== VIEW & EDIT TICKETS =====================
elif page == "View & Edit Tickets":
    st.header("📋 All Tickets")
    df = pd.read_sql_query("SELECT * FROM tickets ORDER BY id DESC", conn)

    if not df.empty:
        st.dataframe(df, use_container_width=True)

        st.subheader("Update Ticket Status")
        col1, col2 = st.columns([1, 2])
        with col1:
            ticket_id = st.selectbox("Select Ticket ID", df['id'].tolist())
        with col2:
            new_status = st.selectbox("New Status", ["Open", "In Progress", "Resolved"])

        if st.button("Update Status", type="primary"):
            c.execute("UPDATE tickets SET status = ? WHERE id = ?", (new_status, ticket_id))
            conn.commit()
            st.success(f"✅ Ticket {ticket_id} updated to **{new_status}**")
            st.rerun()
    else:
        st.info("No tickets yet. Please create some.")

# ===================== MONTHLY REPORT =====================
elif page == "Monthly Report":
    st.header("📊 Monthly Analytical Report")
    df = pd.read_sql_query("SELECT * FROM tickets", conn)

    if not df.empty:
        df['Month'] = pd.to_datetime(df['date']).dt.strftime('%B %Y')
        st.bar_chart(df.groupby('Month').size())

        st.subheader("Department-wise Summary")
        summary = df.groupby('department').agg(
            Total_Tickets=('id', 'count'),
            Resolved=('status', lambda x: (x == 'Resolved').sum())
        ).reset_index()
        st.dataframe(summary, use_container_width=True)

        st.subheader("Download Options")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Download Full Report"):
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download Full CSV", csv, f"IT_Full_Report_{datetime.now().strftime('%Y-%m')}.csv",
                                   "text/csv")
        with col2:
            if st.button("📊 Download Summary"):
                csv_sum = summary.to_csv(index=False).encode('utf-8')
                st.download_button("Download Summary CSV", csv_sum, "IT_Summary_Report.csv", "text/csv")
    else:
        st.info("No data yet.")

# Other Pages
else:
    df = pd.read_sql_query("SELECT * FROM tickets", conn)
    if not df.empty:
        if page == "Analysis Dashboard":
            st.header("Analysis Dashboard")
            st.bar_chart(df['category'].value_counts())
        elif page == "Recurring Users":
            st.header("Recurring Users")
            st.bar_chart(df['user_name'].value_counts().head(15))

st.sidebar.info("✅ Running at: http://172.18.6.105:8501")