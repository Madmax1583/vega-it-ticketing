"""Theme / CSS injection (V2)."""

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

h1, h2, h3, h4, .stMarkdown, .stMarkdown p, .stCaption, label,
[data-testid='stWidgetLabel'] p, [data-testid='stMarkdownContainer'] p {
    color: #F1F5F9 !important;
}
[data-testid='stCaption'], .stCaption, small {
    color: #E2E8F0 !important;
    opacity: 1 !important;
}
[data-testid='stWidgetLabel'] p {
    font-weight: 600 !important;
    color: #F8FAFC !important;
}

/* Sidebar + main buttons: dark surface, light text */
div.stButton > button {
    background-color: #1e293b !important;
    color: #F8FAFC !important;
    border: 1px solid rgba(148,163,184,0.35) !important;
    font-weight: 600 !important;
}
div.stButton > button:hover {
    background-color: #334155 !important;
    border-color: rgba(96,165,250,0.5) !important;
    color: #ffffff !important;
}
div.stButton > button[kind='primary'],
div.stButton > button[data-testid='baseButton-primary'] {
    background-color: #dc2626 !important;
    color: #ffffff !important;
    border: none !important;
}

.sticky-topbar {
    position: sticky; top: .25rem; z-index: 30;
    backdrop-filter: blur(12px);
    background: rgba(2,6,23,.72);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 14px 18px;
    margin-bottom: 16px;
}
.hero-title { font-size: 30px; font-weight: 800; color: white; margin: 4px 0 8px 0; }
.crumb { color: #CBD5E1; font-size: 12px; }
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
</style>
"""


def inject_enterprise_ui_css() -> None:
    st.markdown(ENTERPRISE_CSS, unsafe_allow_html=True)


def inject_scaffold_css() -> None:
    st.markdown(ENTERPRISE_CSS, unsafe_allow_html=True)
