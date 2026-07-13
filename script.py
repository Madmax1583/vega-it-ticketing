import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# =========================================================================
# 🎛️ PAGE CONFIGURATION & INTERACTIVE STYLING
# =========================================================================
st.set_page_config(page_title="Vega & Knitpro IT Ticketing", layout="wide")

# Enhanced Custom CSS for a modern, scannable dark-mode experience
st.markdown("""
<style>
    /* Styling the dynamic AI feedback card */
    .ai-card {
        background-color: #1e293b;
        border-left: 5px solid #3b82f6;
        padding: 18px;
        border-radius: 8px;
        margin-top: 10px;
        margin-bottom: 15px;
        color: #f8fafc;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .ai-title {
        color: #60a5fa;
        font-weight: bold;
        font-size: 1.15rem;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .step-item {
        margin-bottom: 8px;
        font-size: 0.95rem;
        line-height: 1.4;
    }
    
    /* Global layout enhancements */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        color: #max(1, 1);
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================================
# 🏢 BRANDING & TITLES
# =========================================================================
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
st.markdown("---")

# =========================================================================
# 🔑 SUPABASE INITIALIZATION
# =========================================================================
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

# =========================================================================
# 🤖 AI DIAGNOSTIC KNOWLEDGE BASE (ENGLISH & HINDI)
# =========================================================================
AI_SUGGESTIONS = {
    "CCTV/Camera": {
        "title_en": "📷 AI Video Infrastructure Diagnostics",
        "title_hi": "📷 एआई वीडियो इन्फ्रास्ट्रक्चर डायग्नोस्टिक्स",
        "English": [
            "Check if the camera POE switch port light is blinking. If not, swap ports or check the patch cord.",
            "Ping the camera IP address via CMD to check network dropouts.",
            "If NVR shows 'No Video', check if the camera channel needs a firmware restart or re-login."
        ],
        "Hindi": [
            "जांचें कि कैमरा POE स्विच पोर्ट की लाइट ब्लिंक कर रही है या नहीं। यदि नहीं, तो पोर्ट बदलें या पैच कॉर्ड चेक करें।",
            "नेटवर्क ड्रॉपआउट चेक करने के लिए CMD के माध्यम से कैमरा IP एड्रेस को पिंग करें।",
            "यदि NVR 'No Video' दिखाता है, तो जांचें कि कैमरा चैनल को फर्मवेयर रीस्टार्ट या री-लॉगिन की आवश्यकता है या नहीं।"
        ]
    },
    "Laptop/Hardware": {
        "title_en": "💻 AI Endpoint Hardware Diagnostics",
        "title_hi": "💻 एआई एंडपॉइंट हार्डवेयर डायग्नोस्टिक्स",
        "English": [
            "**No Power:** Perform a hard reset (unplug battery, hold down power button for 30 seconds, reconnect).",
            "**Display Black:** Connect to an external monitor to verify if it's a motherboard issue or LCD panel failure.",
            "**Keyboard/Touchpad:** Check Device Manager for driver error codes (Yellow triangle) and reinstall I2C drivers."
        ],
        "Hindi": [
            "**पावर नहीं आ रही:** हार्ड रीसेट करें (बैटरी निकालें, पावर बटन को 30 सेकंड तक दबाकर रखें, फिर फिर से कनेक्ट करें)।",
            "**डिस्प्ले ब्लैक है:** बाहरी मॉनिटर से कनेक्ट करके जांचें कि यह मदरबोर्ड की समस्या है या LCD पैनल खराब है।",
            "**कीबोर्ड/टचपैड:** ड्राइवर त्रुटि कोड (पीला त्रिकोण) के लिए डिवाइस मैनेजर की जांच करें और I2C ड्राइवरों को रीइन्स्टॉल करें।"
        ]
    },
    "Email/Outlook": {
        "title_en": "📧 AI Communication Layer Diagnostics",
        "title_hi": "📧 एआई कम्यूनिकेशन लेयर डायग्नोस्टिक्स",
        "English": [
            "**Outlook Crashing/Freezing:** Run `outlook.exe /safe` to see if a third-party add-in is causing the crash.",
            "**Send/Receive Error:** Check if the PST/OST file size has reached its limit (usually 50GB). Compact the data file.",
            "**Password Prompt:** Clear Windows Credential Manager cached passwords under 'Generic Credentials'."
        ],
        "Hindi": [
            "**आउटलुक क्रैश/फ्रीज:** यह देखने के लिए कि क्या कोई थर्ड-पार्टी ऐड-इन क्रैश का कारण बन रहा है, `outlook.exe /safe` चलाएं।",
            "**सेंड/रिसीव एरर:** जांचें कि क्या PST/OST फ़ाइल का आकार अपनी सीमा (आमतौर पर 50GB) तक पहुंच गया है। डेटा फ़ाइल को कॉम्पैक्ट करें।",
            "**पासवर्ड प्रॉम्प्ट:** 'Generic Credentials' के तहत विंडोज क्रेडेंशियल मैनेजर में कैश्ड पासवर्ड साफ़ करें।"
        ]
    },
    "Printer": {
        "title_en": "🖨️ AI Print Management Diagnostics",
        "title_hi": "🖨️ एआई प्रिंट मैनेजमेंट डायग्नोस्टिक्स",
        "English": [
            "**Offline Mismatch:** Go to Printer Properties -> Ports -> Uncheck 'SNMP Status Enabled'.",
            "**Spooler Stuck:** Open `services.msc`, stop 'Print Spooler', clear `C:\\Windows\\System32\\spool\\PRINTERS`, restart Spooler.",
            "**Faded Print:** Check toner cartridge level or clean the scanner glass mirror element inside the printer cover assembly."
        ],
        "Hindi": [
            "**ऑफलाइन मिसमैच:** प्रिंटर प्रॉपर्टीज -> पोर्ट्स पर जाएं -> 'SNMP Status Enabled' को अनचेक करें।",
            "**स्पूलर अटक गया:** `services.msc` खोलें, 'Print Spooler' को रोकें, `C:\\Windows\\System32\\spool\\PRINTERS` को खाली करें, फिर स्पूलर को रीस्टार्ट करें।",
            "**हल्की प्रिंटिंग:** टोनर कार्ट्रिज लेवल की जांच करें या प्रिंटर कवर के अंदर स्कैनर ग्लास मिरर को साफ करें।"
        ]
    },
    "SAP": {
        "title_en": "🏢 AI Enterprise ERP Diagnostics",
        "title_hi": "🏢 एआई एंटरप्राइज ईआरपी डायग्नोस्टिक्स",
        "English": [
            "**Connection Timeout:** Verify `saplogon.ini` settings or check if the user is connected to the local office gateway/VPN.",
            "**Locked Session:** Go to transaction code `SM04` or `SM12` to clear old hung sessions for the user's client profile.",
            "**GUI Error:** Clear the local SAP cache or reinstall SAP GUI patch level updates."
        ],
        "Hindi": [
            "**कनेक्शन टाइमआउट:** `saplogon.ini` सेटिंग्स को सत्यापित करें या जांचें कि उपयोगकर्ता स्थानीय कार्यालय गेटवे/VPN से जुड़ा है या नहीं।",
            "**लॉक्ड सेशन:** उपयोगकर्ता के क्लाइंट प्रोफ़ाइल के लिए पुराने अटके हुए सेशन को हटाने के लिए ट्रांजेक्शन कोड `SM04` या `SM12` पर जाएं।",
            "**GUI एरर:** लोकल SAP कैश साफ़ करें या SAP GUI पैच लेवल अपडेट को रीइन्स्टॉल करें।"
        ]
    },
    "Network": {
        "title_en": "🌐 AI Network Routing Diagnostics",
        "title_hi": "🌐 एआई नेटवर्क राउटिंग डायग्नोस्टिक्स",
        "English": [
            "**Wi-Fi Dropping:** Run `netsh winsock reset` and update network adapter drivers.",
            "**IP Conflict:** Run `ipconfig /release` followed by `ipconfig /renew` to lease a fresh dynamic address.",
            "**Slow Speed:** Check if the user is connected to the 2.4GHz band instead of the faster 5GHz corporate network layer."
        ],
        "Hindi": [
            "**वाई-फाई का बार-बार कटना:** `netsh winsock reset` चलाएं और नेटवर्क एडाप्टर ड्राइवरों को अपडेट करें।",
            "**आईपी संघर्ष (Conflict):** एक नया डायनेमिक एड्रेस प्राप्त करने के लिए `ipconfig /release` के बाद `ipconfig /renew` चलाएं।",
            "**धीमी गति:** जांचें कि क्या उपयोगकर्ता तेज 5GHz कॉर्पोरेट नेटवर्क के बजाय 2.4GHz बैंड से जुड़ा हुआ है।"
        ]
    }
}

# =========================================================================
# ⚙️ DATA AND CORE PROCESSING ENGINE
# =========================================================================
def format_ticket_number(ticket_id, location_str):
    try:
        clean_id = int(float(ticket_id))
        if pd.isna(location_str) or not location_str:
            return f"IT-2026-{clean_id:04d}"
        loc = str(location_str).lower()
        if "vega" in loc or "136" in loc or "155" in loc:
            prefix = "VEGA"
        elif "knitpro" in loc or "jaipur" in loc:
            prefix = "KP"
        else:
            prefix = "IT"
        return f"{prefix}-2026-{clean_id:04d}"
    except Exception:
        return f"IT-2026-{ticket_id}"

def load_data():
    try:
        response = supabase.table("tickets").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df['id'] = pd.to_numeric(df['id'], errors
