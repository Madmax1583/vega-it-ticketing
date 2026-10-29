"""
Ticket classification and AI Copilot suggestion catalogs (V2).

Extracted from script.py for shared use by services and pages.
"""

CATEGORY_MASTER = {
    "LaptopHardware": [
        "Slow Performance",
        "Boot Issue",
        "Keyboard/Mouse",
        "Display",
        "Battery/Charging",
        "Blue Screen",
        "Upgrade",
        "Peripheral",
    ],
    "Printer": [
        "Print Issue",
        "Scanner Issue",
        "Driver/Install",
        "Cartridge/Toner",
        "Paper Jam",
        "Network Printer",
    ],
    "EmailOutlook": [
        "Login Issue",
        "Configuration",
        "PST/OST",
        "Mail Flow",
        "Migration",
        "Mailbox Access",
    ],
    "Network": [
        "Internet",
        "WiFi",
        "LAN",
        "VPN",
        "Switch/Firewall",
        "Shared Folder Access",
    ],
    "CCTVCamera": [
        "Camera Offline",
        "NVR Issue",
        "Recording Issue",
        "Installation",
        "View Access",
    ],
    "SAP": [
        "Login Issue",
        "Client Error",
        "Access/Role",
        "Transaction Error",
        "Print from SAP",
    ],
    "ServerUPS": [
        "Server Health",
        "Backup",
        "UPS Alarm",
        "Patch/Update",
        "Attendance Server",
        "RDP/DNS",
    ],
    "AVSupport": [
        "Projector",
        "TV/Display",
        "OPS",
        "Meeting Room Setup",
        "Audio Issue",
        "VC Support",
    ],
    "AccessControl": [
        "Biometric",
        "Door Access",
        "Attendance Device",
        "Access Request",
    ],
    "Telephony": [
        "Phone Dead",
        "Intercom",
        "Extension Config",
        "Voice Quality",
    ],
    "SoftwareSupport": [
        "Software Install",
        "License/Renewal",
        "Application Error",
        "Update/Patch",
    ],
    "InstallationSetup": [
        "New Device Setup",
        "OS Install",
        "Desktop/Laptop Delivery",
        "User Handover",
    ],
    "Other": ["Unclassified"],
}

# Keys match normalize/auto_categorize display-style names used by AI_SUGGESTIONS in production
AI_SUGGESTIONS = {
    "CCTV/Camera": {
        "title_en": "📷 AI Video Infrastructure Diagnostics",
        "title_hi": "📷 एआई वीडियो इन्फ्रास्ट्रक्चर डायग्नोस्टिक्स",
        "English": [
            "Check whether the camera POE switch port light is blinking.",
            "Ping the camera IP address through CMD to confirm network continuity.",
            "If NVR shows no video, restart the camera channel or re-login the device.",
        ],
        "Hindi": [
            "जांचें कि कैमरा POE स्विच पोर्ट की लाइट ब्लिंक कर रही है या नहीं।",
            "नेटवर्क कनेक्टिविटी जांचने के लिए कैमरा IP एड्रेस को पिंग करें।",
            "यदि NVR 'No Video' दिखाए, तो कैमरा चैनल रीस्टार्ट या री-लॉगिन करें।",
        ],
    },
    "Laptop/Hardware": {
        "title_en": "💻 AI Endpoint Hardware Diagnostics",
        "title_hi": "💻 एआई एंडपॉइंट हार्डवेयर डायग्नोस्टिक्स",
        "English": [
            "Perform a hard reset by disconnecting power and holding the power button for 30 seconds.",
            "Connect to an external display to isolate panel versus motherboard issues.",
            "Check Device Manager and reinstall chipset or hardware drivers if needed.",
        ],
        "Hindi": [
            "पावर डिस्कनेक्ट करके 30 सेकंड तक पावर बटन दबाकर हार्ड रीसेट करें।",
            "LCD और मदरबोर्ड समस्या अलग करने के लिए बाहरी मॉनिटर लगाएं।",
            "Device Manager जांचें और आवश्यक होने पर ड्राइवर पुनः इंस्टॉल करें।",
        ],
    },
    "Email/Outlook": {
        "title_en": "📧 AI Communication Layer Diagnostics",
        "title_hi": "📧 एआई कम्यूनिकेशन लेयर डायग्नोस्टिक्स",
        "English": [
            "Run outlook.exe /safe to isolate add-in conflicts.",
            "Check PST or OST file size and compact it if very large.",
            "Clear Credential Manager entries if password prompts repeat.",
        ],
        "Hindi": [
            "Add-in conflict जांचने के लिए outlook.exe /safe चलाएं।",
            "PST या OST फ़ाइल का आकार जांचें और जरूरत हो तो compact करें।",
            "बार-बार पासवर्ड आने पर Credential Manager entries साफ करें।",
        ],
    },
    "Printer": {
        "title_en": "🖨️ AI Print Management Diagnostics",
        "title_hi": "🖨️ एआई प्रिंट मैनेजमेंट डायग्नोस्टिक्स",
        "English": [
            "Verify Printer Properties, configured port, and SNMP setting.",
            "Restart Print Spooler and clear stuck jobs in the PRINTERS folder.",
            "Inspect cartridge, rollers, and scanner glass for quality issues.",
        ],
        "Hindi": [
            "Printer Properties, port configuration और SNMP setting जांचें।",
            "Print Spooler restart करें और stuck jobs साफ करें।",
            "कार्ट्रिज, रोलर्स और स्कैनर ग्लास जांचें।",
        ],
    },
    "SAP": {
        "title_en": "🏢 AI Enterprise ERP Diagnostics",
        "title_hi": "🏢 एआई एंटरप्राइज ईआरपी डायग्नोस्टिक्स",
        "English": [
            "Verify SAP logon configuration and network reachability.",
            "Check for locked or hung sessions through SAP tools.",
            "Repair SAP GUI or clear cache if the client is unstable.",
        ],
        "Hindi": [
            "SAP logon configuration और network connectivity जांचें।",
            "Locked या hung sessions जांचें।",
            "Client unstable होने पर SAP GUI repair या cache clear करें।",
        ],
    },
    "Network": {
        "title_en": "🌐 AI Network Routing Diagnostics",
        "title_hi": "🌐 एआई नेटवर्क राउटिंग डायग्नोस्टिक्स",
        "English": [
            "Reset Winsock and inspect the adapter driver for frequent drops.",
            "Release and renew IP configuration if conflict is suspected.",
            "Check the SSID and frequency band being used by the device.",
        ],
        "Hindi": [
            "बार-बार डिस्कनेक्ट होने पर Winsock reset और adapter driver जांचें।",
            "IP conflict शक होने पर release और renew करें।",
            "SSID और frequency band की पुष्टि करें।",
        ],
    },
    "Server/UPS": {
        "title_en": "🖥️ Server & Power Infrastructure Diagnostics",
        "title_hi": "🖥️ सर्वर और पावर इन्फ्रास्ट्रक्चर डायग्नोस्टिक्स",
        "English": [
            "Check UPS load and input power if alarms are active.",
            "Verify rack airflow and server room temperature.",
            "Review DNS and authentication dependencies if logins fail.",
        ],
        "Hindi": [
            "अलार्म आने पर UPS load और input power जांचें।",
            "Rack airflow और server room temperature जांचें।",
            "Login fail होने पर DNS और authentication dependencies देखें।",
        ],
    },
}
