"""Theme / CSS injection (V2 Phase 3)."""

from __future__ import annotations

import streamlit as st

ENTERPRISE_CSS = """
<style>
:root {
    --bg: #020617;
    --surface: #0F172A;
    --border: rgba(148,163,184,0.22);
    --text: #F1F5F9;
    --muted: #CBD5E1;
    --primary: #3B82F6;
    --success: #10B981;
    --warning: #F59E0B;
    --danger: #EF4444;
    --shadow-soft: 0 8px 24px rgba(15,23,42,.22);
    --radius: 18px;
}
.stApp, [data-testid='stAppViewContainer'], [data-testid='stHeader'] {
    background: radial-gradient(circle at top right, rgba(59,130,246,0.10), transparent 25%),
                linear-gradient(180deg, #020617 0%, #071122 100%);
    color: var(--text);
}
[data-testid='stSidebar'] {
    background: linear-gradient(180deg, #0b1220 0%, #111827 100%) !important;
    border-right: 1px solid var(--border);
}
.block-container { padding-top: 1rem !important; max-width: 1500px; }

/* High-contrast text for headings, labels, captions */
h1, h2, h3, h4, .stMarkdown, .stMarkdown p, .stCaption, label,
[data-testid='stWidgetLabel'] p, [data-testid='stMarkdownContainer'] p {
    color: #F1F5F9 !important;
}
[data-testid='stCaption'], .stCaption, small {
    color: #E2E8F0 !important;
    opacity: 1 !important;
}
[data-testid='stWidgetLabel'] {
    color: #F8FAFC !important;
}
[data-testid='stWidgetLabel'] p {
    font-weight: 600 !important;
    color: #F8FAFC !important;
}

/* Inputs readable on dark bg */
.stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb='select'] {
    color: #0F172A !important;
}

.sticky-topbar {
    position: sticky; top: .25rem; z-index: 30;
    backdrop-filter: blur(12px);
    background: rgba(2,6,23,.72);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 14px 18px;
    margin-bottom: 16px;
    box-shadow: var(--shadow-soft);
}
.hero-title { font-size: 30px; font-weight: 800; color: white; margin: 4px 0 8px 0; }
.crumb, .kpi-title, .kpi-sub, .feed-meta, .panel-sub { color: #CBD5E1; font-size: 12px; }
.kpi-card {
    background: linear-gradient(180deg, rgba(15,23,42,.98), rgba(18,32,51,.96));
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px;
    box-shadow: var(--shadow-soft);
    min-height: 120px;
}
.kpi-top { display:flex; justify-content:space-between; align-items:center; margin-bottom: 12px; }
.kpi-icon {
    width: 38px; height: 38px; border-radius: 12px;
    display:flex; align-items:center; justify-content:center;
    background: rgba(59,130,246,.14); color:#93C5FD; font-size:18px;
}
.kpi-value { color:#fff; font-size: 28px; font-weight: 800; line-height:1.1; }
.trend-up { color: var(--success); }
.trend-warn { color: var(--warning); }
.trend-down { color: var(--danger); }
.panel {
    background: linear-gradient(180deg, rgba(15,23,42,.95), rgba(15,23,42,.88));
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 16px;
}
.panel-title, .feed-title { color:#fff; font-size:18px; font-weight:700; margin-bottom:10px; }
.status-chip {
    display: inline-block; padding: 4px 10px; border-radius: 999px;
    font-size: 0.78rem; font-weight: 700; border: 1px solid transparent; white-space: nowrap;
}
.status-open { color: #fecaca; background: rgba(239,68,68,0.15); border-color: rgba(239,68,68,0.3); }
.status-progress { color: #bfdbfe; background: rgba(59,130,246,0.15); border-color: rgba(59,130,246,0.3); }
.status-hold { color: #fde68a; background: rgba(245,158,11,0.15); border-color: rgba(245,158,11,0.3); }
.status-resolved { color: #bbf7d0; background: rgba(34,197,94,0.15); border-color: rgba(34,197,94,0.3); }
.table-scroll {
    width: 100%; overflow-x: auto; border: 1px solid var(--border);
    border-radius: 12px; background: var(--surface);
}
.table-scroll table { width: 100%; min-width: 640px; border-collapse: collapse; }
.table-scroll th, .table-scroll td {
    padding: 10px 12px; border-bottom: 1px solid rgba(39, 52, 73, 0.8);
    text-align: left; font-size: 0.86rem; vertical-align: top; color: #E2E8F0;
}
.table-scroll th { background: #162033; color: #e5eefc; font-size: 0.78rem; text-transform: uppercase; }
.feed-item { padding: 12px 0; border-bottom:1px solid rgba(148,163,184,.12); }
.feed-item:last-child { border-bottom:none; }
</style>
"""


def inject_enterprise_ui_css() -> None:
    st.markdown(ENTERPRISE_CSS, unsafe_allow_html=True)


def inject_scaffold_css() -> None:
    st.markdown(ENTERPRISE_CSS, unsafe_allow_html=True)
