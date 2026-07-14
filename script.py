import streamlit as st
import pandas as pd
from datetime import datetime
import io
import urllib.request
from supabase import create_client, Client

# ==========================================
# 1. APPLICATION CONFIGURATION & STYLING
# ==========================================
st.set_page_config(page_title="Vega & Knitpro IT Ticketing", layout="wide")

st.markdown("""
<style>
    .ai-card {
        background-color: #1e293b; 
        border-left: 5px solid #3b82f6; 
        padding: 16px; 
        border-radius: 8px; 
        margin: 10px 0;
    }
    .ai-title {
        color: #60a5fa; 
        font-weight: bold; 
        font-size: 1.15rem;
        margin-bottom: 8px;
    }
    .kpi-container {
        background-color: #0f172a;
        padding: 15px;
        border-radius: 6px;
        text-align: center;
        border: 1px solid #334155;
    }
    .excel-badge {
        background-color: #166534;
        color: #bbf7d0;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Application Header & Branding
col1, col2, col3 = st.columns([1, 1, 4])
with col1: st.caption("🔺 Vega Operations")
with col2: st.caption("🔺 Knitpro Industrial")
with col3: st.title("🛠️ Vega & Knitpro IT Ticketing & Analysis System")


# ==========================================
# 2. DATABASE INITIALIZATION & STATE ENGINES
# ==========================================
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        # Strict 3-second network pre-flight check to prevent screen hang
        urllib.request.urlopen(url, timeout=3)
        return create_client(url, key)
    except Exception as e:
        print(f"Supabase connection skipped (using sandbox). Detail: {e}")
        return None

supabase = init_supabase()
db_connected = supabase is not None

# --- CORE TICKETING DATA ENGINE ---
if "local_db" not in st.session_state:
    st.session_state.local_db = pd.DataFrame([
        {"id": 1, "date": "2026-07-01", "user_name": "Amit Sharma", "department": "Production",
         "complaint": "CCTV camera in main corridor raw materials loading dock is flickering",
         "location": "Sector - 136 Vega", "attended_by": "Satish", "status": "In Progress", "category": "CCTV/Camera",
         "remarks": "Inspecting POE injector port status"},
        {"id": 2, "date": "2026-07-03", "user_name": "Sunita Rao", "department": "Finance",
         "complaint": "Desktop client showing blue screen loops after update patch execution",
         "location": "Knitpro 28-29", "attended_by": "Priyanshu", "status": "Open", "category": "Laptop/Hardware",
         "remarks": ""},
        {"id": 3, "date": "2026-07-05", "user_name": "Rajesh Kumar", "department": "HR",
         "complaint": "HR Shared network office printer offline, print queue showing stuck jobs",
         "location": "Sector - 155 Vega", "attended_by": "Amit", "status": "Resolved", "category": "Printer",
         "remarks": "Flushed local print spooler threads, cleared paper obstruction"},
        {"id": 4, "date": "2026-07-08", "user_name": "Sunita Rao", "department": "Finance",
         "complaint": "Outlook continuously prompting for authentication credentials over corporate Wi-Fi",
         "location": "Knitpro 28-29", "attended_by": "Ranjan", "status": "On Hold - User Busy",
         "category": "Email/Outlook", "remarks": "User in site audit meeting"},
        {"id": 5, "date": "2026-07-11", "user_name": "Vikram Singh", "department": "Logistics",
         "complaint": "Cannot link tracking manifests due to SAP client gateway connection timeout",
         "location": "Knitpro - Jaipur", "attended_by": "Manish", "status": "Resolved", "category": "SAP",
         "remarks": "Updated local SAP GUI connection configurations"}
    ])

def load_data():
    if db_connected:
        try:
            response = supabase.table("tickets").select("*").execute()
            return pd.DataFrame(response.data) if response.data else pd.DataFrame()
        except Exception:
            return st.session_state.local_db
    return st.session_state.local_db

df_live = load_data()

# --- MULTI-SHEET NAS BACKUP INITIALIZATION ---
if "local_nas_db" not in st.session_state:
    st.session_state.local_nas_db = pd.DataFrame([
        # Sheet 1: Sector - 136 Vega
        {"date": "2026-07-11", "location": "Sector - 136 Vega", "status": "Success", "storage_used": 450.0, "remarks": "System backup completed normally."},
        {"date": "2026-07-12", "location": "Sector - 136 Vega", "status": "Success", "storage_used": 455.0, "remarks": "System backup completed normally."},
        {"date": "2026-07-13", "location": "Sector - 136 Vega", "status": "Failed", "storage_used": 460.0, "remarks": "Connection handshake timeout. Re-run scheduled."},
        {"date": "2026-07-14", "location": "Sector - 136 Vega", "status": "Success", "storage_used": 235.4162, "remarks": "Calculated conversion safe sync done."},
        # Sheet 2: Knitpro 28-29
        {"date": "2026-07-11", "location": "Knitpro 28-29", "status": "Success", "storage_used": 310.0, "remarks": "Daily incremental snapshot success."},
        {"date": "2026-07-12", "location": "Knitpro 28-29", "status": "Success", "storage_used": 312.5, "remarks": "Daily incremental snapshot success."},
        {"date": "2026-07-13", "location": "Knitpro 28-29", "status": "Success", "storage_used": 315.0, "remarks": "Daily incremental snapshot success."},
        # Sheet 3: Sector - 155 Vega
        {"date": "2026-07-11", "location": "Sector - 155 Vega", "status": "Success", "storage_used": 890.0, "remarks": "Full weekly node clone completed."},
        {"date": "2026-07-12", "location": "Sector - 155 Vega", "status": "Warning / Partial", "storage_used": 895.0, "remarks": "Partial sync on directory profiles."},
        {"date": "2026-07-13", "location": "Sector - 155 Vega", "status": "Success", "storage_used": 902.0, "remarks": "Full recovery check completed."},
        # Sheet 4: Knitpro - Jaipur
        {"date": "2026-07-13", "location": "Knitpro - Jaipur", "status": "Success", "storage_used": 150.0, "remarks": "Initial cluster sync."},
        # Sheet 5: Knitpro 42
        {"date": "2026-07-13", "location": "Knitpro 42", "status": "Success", "storage_used": 220.0, "remarks": "Manual system backup done."},
        # Sheet 6: Knitpro 72-73
        {"date": "2026-07-13", "location": "Knitpro 72-73", "status": "Success", "storage_used": 180.0, "remarks": "Backup completed."},
        # Sheet 7: Knitpro 75
        {"date": "2026-07-13", "location": "Knitpro 75", "status": "Success", "storage_used": 340.0, "remarks": "Backup completed."},
        # Sheet 8: Bharat Composite Sector 80
        {"date": "2026-07-13", "location": "Bharat Composite Sector 80", "status": "Success", "storage_used": 610.0, "remarks": "Database safe check normal."},
        # Sheet 9: Vega Sector 80
        {"date": "2026-07-13", "location": "Vega Sector 80", "status": "Success", "storage_used": 750.0, "remarks": "Active sync complete."}
    ])

def load_nas_data():
    if db_connected:
        try:
            response = supabase.table("nas_backups").select("*").execute()
            if response.data:
                return pd.DataFrame(response.data)
        except Exception:
            pass
    return st.session_state.local_nas_db

df_nas = load_nas_data()


# ==========================================
# 3. GLOBAL SYSTEM CONSTANTS & HELPERS
# ==========================================
TECH_MAP = {"Satish": "TECH-01", "Priyanshu": "TECH-02", "Amit": "TECH-03", "Ranjan": "TECH-04", "Manish": "TECH-05"}
OFFICIAL_LOCATIONS = ["Sector - 136 Vega", "Knitpro 28-29", "Sector - 155 Vega", "Knitpro - Jaipur", "Knitpro 42",
                      "Knitpro 72-73", "Knitpro 75", "Bharat Composite Sector 80", "Vega Sector 80"]
STATUS_OPTIONS = ["Open", "In Progress", "On Hold - User Busy", "Resolved"]

EXCEL_SHEET_MAP = {
    "Sector - 136 Vega": "Sheet 1 (sheet1.bin)",
    "Knitpro 28-29": "Sheet 2 (sheet2.bin)",
    "Sector - 155 Vega": "Sheet 3 (sheet3.bin)",
    "Knitpro - Jaipur": "Sheet 4 (sheet4.bin)",
    "Knitpro 42": "Sheet 5 (sheet5.bin)",
    "Knitpro 72-73": "Sheet 6 (sheet6.bin)",
    "Knitpro 75": "Sheet 7 (sheet7.bin)",
    "Bharat Composite Sector 80": "Sheet 8 (sheet8.bin)",
    "Vega Sector 80": "Sheet 9 (sheet9.bin)",
}

AI_SUGGESTIONS = {
    "CCTV/Camera": {"title_en": "📷 CCTV Infrastructure Diagnostic Protocol",
                    "title_hi": "📷 सीसीटीवी बुनियादी ढांचा निदान नियम",
                    "English": ["Verify status LEDs on the terminal POE network switch port allocation.",
                                "Run a network ping trace execution targeting the static camera IP path.",
                                "Perform a manual hardware power cycle on the NVR camera routing card assembly."],
                    "Hindi": ["पीओई नेटवर्क स्विच पोर्ट पर स्टेटस एलईडी लाइट इंडिकेटर चेक करें।",
                              "कैमरा आईपी एड्रेस पिंग करके नेटवर्क लाइन कनेक्टिविटी सुनिश्चित करें।",
                              "एनवीआर कैमरा कंट्रोल पैनल यूनिट को मैन्युअल रूप से रीस्टार्ट करें।"]},
    "Laptop/Hardware": {"title_en": "💻 Hardware Diagnostics & Static Clearing",
                        "title_hi": "💻 हार्डवेयर निदान और स्टेटिक समाशोधन", "English": [
            "Unplug host external adapter cords, isolate internal battery links, and hold key for 30s.",
            "Reseat physical RAM channel memory elements within computing host slot channels.",
            "Initiate vendor embedded pre-boot diagnostic array tests (Hold F12/F10 key arrays)."],
                        "Hindi": ["पावर एडॉप्टर केबल्स निकालें, बैटरी अलग करें और पावर बटन 30 सेकंड दबाकर रखें।",
                                  "मदरबोर्ड रैम मॉड्यूल स्लॉट कनेक्शन साफ करके दोबारा लगाएं।",
                                  "बूट सीक्वेंस के दौरान F12 दबाकर हार्डवेयर डायग्नोस्टिक्स चलाएं।"]},
    "Printer": {"title_en": "🖨️ Thermal & Print Asset Infrastructure Solutions",
                "title_hi": "🖨️ प्रिंटर बेड़े समस्या निवारण गाइड", "English": [
            "Access the host services.msc console applet and restart the local Print Spooler framework.",
            "Inspect the internal chassis path components to confirm clearance of torn document fragments.",
            "Verify baseline TCP/IP configuration paths match host drivers exactly."],
                "Hindi": ["विंडोज सर्विसेज (services.msc) खोलें और 'Print Spooler' सर्विस रीस्टार्ट करें।",
                          "प्रिंटर आंतरिक रोलर असेंबली कंपोनेंट्स से फंसे हुए कागज के टुकड़े बाहर निकालें।",
                          "प्रिंटर नेटवर्क इंटरफ़ेस आईपी और ड्राइवर पोर्ट सेटिंग्स की जांच करें।"]},
}

def auto_categorize(text):
    t = str(text).lower()
    if any(k in t for k in ['cctv', 'camera', 'dvr', 'nvr']):
        return 'CCTV/Camera'
    elif any(k in t for k in ['laptop', 'desktop', 'monitor', 'ram', 'ssd', 'hardware']):
        return 'Laptop/Hardware'
    elif any(k in t for k in ['outlook', 'email', 'exchange', 'pop3', 'smtp']):
        return 'Email/Outlook'
    elif any(k in t for k in ['printer', 'scanner', 'xerox', 'print']):
        return 'Printer'
    elif any(k in t for k in ['sap', 'erp', 'tcode']):
        return 'SAP'
    elif any(k in t for k in ['network', 'wifi', 'lan', 'internet', 'switch', 'router']):
        return 'Network'
    else:
        return 'Other'

def format_ticket_number(ticket_id, location_str):
    try:
        clean_id = int(float(ticket_id))
        loc = str(location_str).lower()
        prefix = "VEGA" if "vega" in loc else "KP" if "knitpro" in loc else "IT"
        return f"{prefix}-2026-{clean_id:04d}"
    except Exception:
        return f"IT-2026-{ticket_id}"


# ==========================================
# 4. INTERACTIVE ROUTING VIEW TABS
# ==========================================
tab_log, tab_view, tab_analysis, tab_monthly, tab_nas, tab_recurring = st.tabs([
    "🆕 Log New Ticket",
    "📋 View & Edit Queue",
    "📊 Operational Dashboard",
    "📅 Monthly Audit Reports",
    "💾 NAS Storage Monitoring",
    "🔄 Chronic User Audits"
])

# --- TAB 1: LOG NEW TICKET ---
with tab_log:
    st.subheader("Register New Support Incident Request")
    form_col, ai_col = st.columns([1.1, 0.9])

    with form_col:
        with st.form("ticket_form", clear_on_submit=True):
            col_left, col_right = st.columns(2)
            with col_left:
                user_name = st.text_input("User Name *", placeholder="Employee name")
                department = st.text_input("Department *", placeholder="Department tracking code")
                location = st.selectbox("Office Location / Plant Sector *", OFFICIAL_LOCATIONS)
            with col_right:
                attended_by = st.selectbox("Assigned System Technician", list(TECH_MAP.keys()))
                status = st.selectbox("Initial Ticket Status", STATUS_OPTIONS)

            complaint = st.text_area("Detailed Complaint Description *",
                                     placeholder="Provide explicit logs, hardware behaviors, or asset status error signs...",
                                     height=100)
            remarks = st.text_area("Technician Operational Action Notes / Remarks",
                                   placeholder="Initial troubleshooting or tracking remarks...", height=80)

            if st.form_submit_button("Submit Ticket Request ⚡"):
                if not user_name or not complaint or not department:
                    st.error("❌ Registration Blocked: Core required parameter fields (*) must be completed.")
                else:
                    cat = auto_categorize(complaint)
                    next_id = int(df_live['id'].max() + 1) if not df_live.empty else 1

                    new_row = {
                        "id": next_id,
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
                            st.success(
                                f"🎉 Ticket Logged to Cloud Infrastructure: {format_ticket_number(next_id, location)}")
                        except Exception as e:
                            st.error(f"Cloud write barrier encountered. Defaulting local write backup. Error: {e}")
                    else:
                        st.session_state.local_db = pd.concat([st.session_state.local_db, pd.DataFrame([new_row])],
                                                              ignore_index=True)
                        st.success(f"🎉 Ticket Processed to Session Sandbox: {format_ticket_number(next_id, location)}")
                    st.rerun()

    with ai_col:
        st.markdown('<div style="padding-left: 10px;">', unsafe_allow_html=True)
        st.subheader("🧠 AI Copilot Real-Time Diagnostic Engine")

        complaint_input = st.text_area("Type description details here for live troubleshooting guidance:", height=110,
                                       placeholder="Paste or type issue here (e.g., 'Printer has a paper jam error signal blinking'...)")
        lang = st.radio("Display Guide Language", ["English", "हिंदी"], horizontal=True)

        if complaint_input:
            cat = auto_categorize(complaint_input)
            st.markdown(f"**Automated Categorization Output:** `{cat}`")

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
                    st.markdown(f"🔹 {step}")
            else:
                st.markdown(f"""
                <div class="ai-card">
                    <div class="ai-title">ℹ️ Standard Operational Procedure Checklist</div>
                    <span style="color:#cbd5e1;">No device-specific hardware matrix found. Perform standard diagnostic checks: Verify peripheral cable security, check device IP address responses via ping, and confirm local server user group permissions settings.</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(
                "💡 Type an operational issue above to instantly run an automated technical categorization and generate step-by-step repair checklists.")
        st.markdown('</div>', unsafe_allow_html=True)


# --- TAB 2: VIEW & EDIT QUEUE ---
with tab_view:
    st.subheader("Global Service Incident Queue Manager")

    if df_live.empty:
        st.info("No logs present in the current tracking matrix.")
    else:
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            sel_status = st.multiselect("Filter Status Profiles", STATUS_OPTIONS, default=STATUS_OPTIONS)
        with f_col2:
            sel_loc = st.multiselect("Filter Operating Site Location", OFFICIAL_LOCATIONS, default=OFFICIAL_LOCATIONS)
        with f_col3:
            available_cats = sorted(list(df_live['category'].unique()))
            sel_cat = st.multiselect("Filter Structural Categories", available_cats, default=available_cats)

        df_display = df_live.copy()
        df_display['System Ticket ID'] = df_display.apply(lambda r: format_ticket_number(r['id'], r['location']),
                                                          axis=1)

        filtered_df = df_display[
            (df_display['status'].isin(sel_status)) &
            (df_display['location'].isin(sel_loc)) &
            (df_display['category'].isin(sel_cat))
            ].sort_values(by='id', ascending=False)

        st.dataframe(
            filtered_df[['System Ticket ID', 'date', 'user_name', 'department', 'location', 'category', 'complaint',
                         'attended_by', 'status', 'remarks']],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        st.subheader("✏️ Incident Status Modifier Matrix")

        mod_col1, mod_col2, mod_col3, mod_col4 = st.columns([1, 1, 1, 2])

        with mod_col1:
            ticket_to_update = st.selectbox("Select Target Incident to Update", options=filtered_df[
                'System Ticket ID'].tolist() if not filtered_df.empty else ["No Match Found"])

        if ticket_to_update != "No Match Found":
            target_record = df_display[df_display['System Ticket ID'] == ticket_to_update].iloc[0]
            real_target_id = int(target_record['id'])

            with mod_col2:
                updated_status = st.selectbox("Modify Queue Status", STATUS_OPTIONS,
                                              index=STATUS_OPTIONS.index(target_record['status']))
            with mod_col3:
                updated_tech = st.selectbox("Reassign Technical Asset Owner", list(TECH_MAP.keys()),
                                            index=list(TECH_MAP.keys()).index(target_record['attended_by']))
            with mod_col4:
                updated_remarks = st.text_input("Append Resolution Strategy Remarks",
                                                value=str(target_record['remarks']))

            if st.button("Commit Lifecycle Changes 🔄"):
                if db_connected:
                    try:
                        supabase.table("tickets").update({
                            "status": updated_status,
                            "attended_by": updated_tech,
                            "remarks": updated_remarks
                        }).eq("id", real_target_id).execute()
                        st.success(f"System State Synchronized for record {ticket_to_update}!")
                    except Exception as e:
                        st.error(f"Cloud state synchronization failed: {e}")
                else:
                    st.session_state.local_db.loc[
                        st.session_state.local_db['id'] == real_target_id, ['status', 'attended_by', 'remarks']] = [
                        updated_status, updated_tech, updated_remarks]
                    st.success(f"Local Sandbox Buffer Modified for record {ticket_to_update}!")
                st.rerun()


# --- TAB 3: OPERATIONAL DASHBOARD ---
with tab_analysis:
    st.subheader("Real-Time Operational Infrastructure Core")

    if not df_live.empty:
        total_count = len(df_live)
        backlog_count = len(df_live[df_live['status'] != "Resolved"])
        completed_count = len(df_live[df_live['status'] == "Resolved"])
        resolution_rate = round((completed_count / total_count) * 100, 1) if total_count > 0 else 0.0

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.markdown(
                f'<div class="kpi-container"><span style="color:#94a3b8; font-size:0.9rem;">Total Incident Workload</span><h2 style="color:#f8fafc; margin:5px 0;">{total_count}</h2></div>',
                unsafe_allow_html=True)
        with kpi2:
            st.markdown(
                f'<div class="kpi-container"><span style="color:#f87171; font-size:0.9rem;">Active Open Backlog</span><h2 style="color:#ef4444; margin:5px 0;">{backlog_count}</h2></div>',
                unsafe_allow_html=True)
        with kpi3:
            st.markdown(
                f'<div class="kpi-container"><span style="color:#4ade80; font-size:0.9rem;">Successfully Resolved</span><h2 style="color:#22c55e; margin:5px 0;">{completed_count}</h2></div>',
                unsafe_allow_html=True)
        with kpi4:
            st.markdown(
                f'<div class="kpi-container"><span style="color:#60a5fa; font-size:0.9rem;">Resolution Efficiency</span><h2 style="color:#3b82f6; margin:5px 0;">{resolution_rate}%</h2></div>',
                unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown("##### 📦 Volumetric Ticket Count by Category")
            st.bar_chart(df_live['category'].value_counts())
        with chart_col2:
            st.markdown("##### 📍 Logged Incidents Across Geographical Sites")
            st.bar_chart(df_live['location'].value_counts())

        st.markdown("---")
        st.markdown("##### ⚡ Active Incident Allocations Across Engineering Staff")
        tech_pivot = df_live.groupby(['attended_by', 'status']).size().unstack(fill_value=0)
        st.bar_chart(tech_pivot)
    else:
        st.info("System operational charts will populate when tracking metrics are active.")


# --- TAB 4: MONTHLY AUDIT REPORTS ---
with tab_monthly:
    st.subheader("Data Export & Audit Manifest Portal")

    if not df_live.empty:
        df_live['Month'] = pd.to_datetime(df_live['date']).dt.strftime('%Y-%m')
        selected_month = st.selectbox("Select Reporting Audit Month Target",
                                      sorted(df_live['Month'].unique(), reverse=True))

        filtered_report_df = df_live[df_live['Month'] == selected_month].copy()
        filtered_report_df['System Ticket ID'] = filtered_report_df.apply(
            lambda r: format_ticket_number(r['id'], r['location']), axis=1)

        st.write(f"Target Month Dataset contains **{len(filtered_report_df)}** recorded actions.")
        st.dataframe(filtered_report_df.drop(columns=['Month']), use_container_width=True, hide_index=True)

        csv_buffer = io.StringIO()
        filtered_report_df.to_csv(csv_buffer, index=False)
        csv_data_string = csv_buffer.getvalue()

        st.download_button(
            label=f"📥 Download Structured Audit Report ({selected_month})",
            data=csv_data_string,
            file_name=f"IT_Audit_Manifest_{selected_month}.csv",
            mime="text/csv",
            type="primary"
        )
    else:
        st.info("Export engines will initialize when structural historic data exists.")


# --- TAB 5: NAS MONITORING WITH DELTA ACCELERATION ---
with tab_nas:
    st.header("💾 NAS Backup Monitoring & Excel Worksheet Mapping")
    st.info("💡 **Excel Sheet References:** This page simulates the 9 worksheets found in your corporate IT tracking workbook. Selecting a location filters or logs data directly to that corresponding sheet mapping.")

    log_col, view_col = st.columns([1, 1.5])

    with log_col:
        st.subheader("📝 Log Today's Backup Manually")
        with st.form("nas_log_form", clear_on_submit=True):
            log_date = st.date_input("Backup Date", value=datetime.now())
            log_location = st.selectbox("NAS Site Location *", OFFICIAL_LOCATIONS)
            
            mapped_sheet = EXCEL_SHEET_MAP.get(log_location, "Unknown Sheet")
            st.markdown(f"**Target Worksheet:** <span class='excel-badge'>{mapped_sheet}</span>", unsafe_allow_html=True)
            
            log_status = st.selectbox("Backup Status", ["Success", "Failed", "Warning / Partial"])
            
            log_storage_kb = st.number_input("Storage Used (KB) *", min_value=0.0, step=1024.0,
                                             help="Enter the backup file size in Kilobytes (KB).")
            
            storage_in_gb_live = round(log_storage_kb / (1024 * 1024), 4)
            st.caption(f"ℹ️ **Automatic Conversion Preview:** {storage_in_gb_live:,} GB")
            
            log_remarks = st.text_area("Operational Remarks / Error Logs",
                                       placeholder="Provide context if the backup failed...")

            submit_nas = st.form_submit_button("Submit Backup Log 💾", type="primary")

            if submit_nas:
                storage_in_gb = round(float(log_storage_kb) / (1024 * 1024), 4)

                new_nas_entry = {
                    "date": log_date.strftime("%Y-%m-%d"),
                    "location": log_location,
                    "status": log_status,
                    "storage_used": storage_in_gb,
                    "remarks": log_remarks
                }

                if db_connected:
                    try:
                        supabase.table("nas_backups").insert(new_nas_entry).execute()
                        st.success(f"✅ Backup state successfully saved to Cloud for {mapped_sheet}!")
                    except Exception as e:
                        st.error(f"Cloud write barrier encountered. Saved to local sandbox instead. Error: {e}")
                else:
                    st.session_state.local_nas_db = pd.concat([
                        st.session_state.local_nas_db,
                        pd.DataFrame([new_nas_entry])
                    ], ignore_index=True)
                    st.success(f"✅ Backup state saved to temporary session buffer for {mapped_sheet}!")
                st.rerun()

    with view_col:
        st.subheader("📊 Backup Performance & Storage Growth")
        
        selected_location = st.selectbox("Select Excel Sheet Reference to View", OFFICIAL_LOCATIONS)
        mapped_sheet_view = EXCEL_SHEET_MAP.get(selected_location, "Unknown Sheet")
        
        df_nas_filtered = df_nas[df_nas['location'] == selected_location] if 'location' in df_nas.columns else df_nas
        
        if df_nas_filtered.empty:
            st.info(f"No backup log entries found for {selected_location} ({mapped_sheet_view}). Start by entering data on the left.")
        else:
            # Sort chronological ascending to run accurate sequential diffs
            df_nas_sorted = df_nas_filtered.sort_values(by='date', ascending=True).copy()

            # NEW LOGIC: Calculate dynamic increase/decrease metric data matrices
            df_nas_sorted['Change (GB)'] = df_nas_sorted['storage_used'].diff().round(4)
            df_nas_sorted['Change (%)'] = (df_nas_sorted['storage_used'].pct_change() * 100).round(2)

            latest_status = df_nas_sorted.iloc[-1]['status']
            latest_date = df_nas_sorted.iloc[-1]['date']
            latest_size = df_nas_sorted.iloc[-1]['storage_used']

            # Contextual status alerts depending on filtered sheet state
            if latest_status == 'Failed':
                st.error(f"⚠️ **Critical Alert:** The last logged backup on {latest_date} for {mapped_sheet_view} FAILED. Review hardware integrity logs.")
            elif latest_status == 'Warning / Partial':
                st.warning(f"⚠️ **Attention Required:** The backup on {latest_date} for {mapped_sheet_view} completed with warnings.")
            else:
                st.success(f"💚 **System Healthy:** Last backup on {latest_date} for {mapped_sheet_view} was completely successful.")

            # NEW UX FEATURE: Display live performance delta KPI metrics cards
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                if len(df_nas_sorted) >= 2:
                    last_delta_gb = df_nas_sorted.iloc[-1]['Change (GB)']
                    last_delta_pct = df_nas_sorted.iloc[-1]['Change (%)']
                    delta_label = f"{last_delta_gb:+.4f} GB ({last_delta_pct:+.2f}%)"
                else:
                    delta_label = "Baseline Init"
                
                st.metric(label="📊 Latest Storage Footprint", value=f"{latest_size:,.4f} GB", delta=delta_label)
            
            with metric_col2:
                st.metric(label="🗂️ Mapped Sheet Status Logs", value=str(len(df_nas_sorted)))

            st.markdown(f"**Historical Logs with Growth Matrix: {mapped_sheet_view}**")
            
            # Format row strings neatly inside dataframe view (Newest first)
            df_nas_table = df_nas_sorted.sort_values(by='date', ascending=False).copy()
            df_nas_table['Change (GB)'] = df_nas_table['Change (GB)'].apply(lambda x: f"{x:+.4f} GB" if pd.notnull(x) else "— Baseline")
            df_nas_table['Change (%)'] = df_nas_table['Change (%)'].apply(lambda x: f"{x:+.2f}%" if pd.notnull(x) else "— Baseline")
            
            st.dataframe(df_nas_table, use_container_width=True, hide_index=True)

            st.markdown(f"**Storage Footprint Over Time (GB): {mapped_sheet_view}**")
            st.line_chart(df_nas_sorted.set_index('date')['storage_used'])


# --- TAB 6: CHRONIC USER AUDITS ---
with tab_recurring:
    st.subheader("High-Frequency Request Vulnerability Profile Analysis")
    st.write("Traces user profile activity anomalies to pinpoint system user onboarding gaps or systematic failures in regional device setups.")

    if not df_live.empty:
        user_metrics = df_live.groupby('user_name').agg(
            total_requests=pd.NamedAgg(column='id', aggfunc='count'),
            resolved_count=pd.NamedAgg(column='status', aggfunc=lambda s: (s == "Resolved").sum()),
            pending_backlog=pd.NamedAgg(column='status', aggfunc=lambda s: (s != "Resolved").sum())
        ).reset_index().sort_values(by='total_requests', ascending=False)

        st.dataframe(user_metrics, use_container_width=True, hide_index=True)

        chronic_users = user_metrics[user_metrics['total_requests'] >= 2]
        if not chronic_users.empty:
            st.warning(f"⚠️ **Asset Vulnerability Indicator:** {len(chronic_users)} employee accounts have registered repeating system tickets. Target hardware inspections or device user guidance tracking is advised.")
    else:
        st.info("Behavior analytical profiles require record data population before tracing loops.")


# Sidebar Operational Status Banner
st.sidebar.markdown("---")
if db_connected:
    st.sidebar.success("⚡ Supabase Cloud Connected")
    st.sidebar.caption("System linked with live cloud production architecture.")
else:
    st.sidebar.warning("⚠️ Session Sandbox Active")
    st.sidebar.caption("Modifications are contained within this local session state buffer.")
