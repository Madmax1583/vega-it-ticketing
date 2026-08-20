"""Central Streamlit styling for the V2 application."""

from __future__ import annotations

import streamlit as st


APP_CSS = """
<style>
:root {
  --vega-navy: #102a43;
  --vega-blue: #1f5f99;
  --vega-green: #17803d;
  --vega-amber: #a15c00;
  --vega-red: #b42318;
  --vega-muted: #5f6c7b;
  --vega-border: #d9e2ec;
  --vega-surface: #f7f9fc;
}
.v2-kpi-card {
  background: var(--vega-surface);
  border: 1px solid var(--vega-border);
  border-left: 4px solid var(--vega-blue);
  border-radius: 8px;
  padding: 0.85rem 1rem;
  min-height: 88px;
}
.v2-kpi-label { color: var(--vega-muted); font-size: 0.82rem; }
.v2-kpi-value { color: var(--vega-navy); font-size: 1.55rem; font-weight: 700; }
.v2-badge { border-radius: 999px; display: inline-block; font-size: 0.76rem; font-weight: 600; padding: 0.18rem 0.55rem; }
.v2-badge-success { background: #dcfae6; color: #086b2d; }
.v2-badge-warning { background: #fff3cd; color: #8a5100; }
.v2-badge-danger { background: #fee4e2; color: #9b1c1c; }
.v2-badge-neutral { background: #e8eef5; color: #334e68; }
.v2-warning-panel { background: #fff9e6; border-left: 4px solid var(--vega-amber); border-radius: 6px; margin: 0.35rem 0; padding: 0.7rem 0.85rem; }
.v2-empty-state { color: var(--vega-muted); border: 1px dashed var(--vega-border); border-radius: 8px; padding: 1rem; text-align: center; }
</style>
"""


def inject_css() -> None:
    """Apply the V2 shared stylesheet to the active Streamlit page."""
    st.markdown(APP_CSS, unsafe_allow_html=True)
