"""Reusable Streamlit display components for V2 pages."""

from __future__ import annotations

from html import escape
from typing import Iterable

import streamlit as st


BADGE_CLASSES = {
    "success": "v2-badge-success",
    "warning": "v2-badge-warning",
    "danger": "v2-badge-danger",
    "neutral": "v2-badge-neutral",
}


def badge_class(tone: str) -> str:
    """Return a safe CSS class for a semantic badge tone."""
    return BADGE_CLASSES.get(str(tone).lower(), BADGE_CLASSES["neutral"])


def status_tone(value: object) -> str:
    """Classify common status values for consistent presentation."""
    text = str(value or "").strip().lower()
    if text in {"resolved", "closed", "completed", "success", "active", "fresh", "ok"}:
        return "success"
    if text in {"failed", "error", "breach", "overdue", "inactive", "stale"}:
        return "danger"
    if text in {"open", "in progress", "on hold", "warning", "medium", "low"}:
        return "warning"
    return "neutral"


def format_metric(value: object, suffix: str = "") -> str:
    """Format a dashboard metric while preserving missing values explicitly."""
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:,.1f}{suffix}"
    if isinstance(value, int):
        return f"{value:,}{suffix}"
    text = str(value).strip()
    return f"{text}{suffix}" if text else "—"


def render_kpi(label: str, value: object, suffix: str = "") -> None:
    """Render a compact KPI card."""
    st.markdown(
        "<div class='v2-kpi-card'>"
        f"<div class='v2-kpi-label'>{escape(str(label))}</div>"
        f"<div class='v2-kpi-value'>{escape(format_metric(value, suffix))}</div>"
        "</div>",
        unsafe_allow_html=True,
    )


def render_status_badge(value: object, tone: str | None = None) -> None:
    """Render a semantic badge without exposing unescaped input to HTML."""
    label = str(value or "Not available")
    resolved_tone = tone or status_tone(label)
    st.markdown(
        f"<span class='v2-badge {badge_class(resolved_tone)}'>{escape(label)}</span>",
        unsafe_allow_html=True,
    )


def render_warnings(warnings: Iterable[object]) -> None:
    """Render zero or more data-quality warnings."""
    for warning in warnings:
        text = str(warning or "").strip()
        if text:
            st.markdown(
                f"<div class='v2-warning-panel'>{escape(text)}</div>",
                unsafe_allow_html=True,
            )


def render_empty_state(message: str = "No data available.") -> None:
    """Render a consistent empty-state panel."""
    st.markdown(
        f"<div class='v2-empty-state'>{escape(str(message))}</div>",
        unsafe_allow_html=True,
    )
