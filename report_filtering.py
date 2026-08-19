# report_filtering.py
"""
Small reusable module for ticket reporting scope filtering.
Provides case-insensitive IT department detection and safe DataFrame filters.
"""
from typing import Optional
import pandas as pd

# Recognized IT department labels (after trimming and lowercasing)
_IT_NAMES = {
    "it",
    "information technology",
    "it department",
    "information technology department",
}


def normalize_department(value: Optional[str]) -> str:
    """Return a normalized department string (trimmed, lowercased).

    Handles None, NaN, and non-string values safely.
    """
    try:
        if value is None:
            return ""
        # pandas NA handling
        if pd.isna(value):
            return ""
    except Exception:
        pass
    try:
        s = str(value).strip()
        return s
    except Exception:
        return ""


def is_it_department(value: Optional[str]) -> bool:
    """Return True if the given department value identifies an IT department.

    Matching is case-insensitive and tolerant of leading/trailing whitespace.
    """
    s = normalize_department(value)
    if not s:
        return False
    return s.lower() in _IT_NAMES or s.lower() == "it"


def _ensure_dataframe(df: Optional[pd.DataFrame]) -> pd.DataFrame:
    """Return an empty DataFrame if df is None, otherwise return df as-is.
    This helper does NOT return a copy; callers should copy when needed.
    """
    if df is None:
        return pd.DataFrame()
    if not isinstance(df, pd.DataFrame):
        return pd.DataFrame(df)
    return df


def filter_user_complaints(df: Optional[pd.DataFrame]) -> pd.DataFrame:
    """Return a copy of df excluding rows where department is an IT department.

    Safe for None, empty DataFrames, missing department column, and NaNs.
    Always returns a copy and does not mutate the original DataFrame.
    """
    orig = _ensure_dataframe(df)
    out = orig.copy()
    if out.empty:
        return out
    if "department" not in out.columns:
        # No department column -> assume all are user complaints
        return out.copy()
    # create normalized flag without mutating original
    dept_series = out["department"].apply(lambda v: normalize_department(v))
    mask_it = dept_series.apply(lambda v: is_it_department(v))
    result = out.loc[~mask_it].copy()
    return result


def filter_it_operations(df: Optional[pd.DataFrame]) -> pd.DataFrame:
    """Return a copy of df including only rows where department is an IT department.

    Safe for None, empty DataFrames, missing department column, and NaNs.
    Always returns a copy and does not mutate the original DataFrame.
    """
    orig = _ensure_dataframe(df)
    out = orig.copy()
    if out.empty:
        return out
    if "department" not in out.columns:
        # No department column -> cannot identify IT rows, return empty
        return out.iloc[0:0].copy()
    dept_series = out["department"].apply(lambda v: normalize_department(v))
    mask_it = dept_series.apply(lambda v: is_it_department(v))
    result = out.loc[mask_it].copy()
    return result


def filter_tickets_by_scope(df: Optional[pd.DataFrame], scope: str) -> pd.DataFrame:
    """Filter tickets by scope.

    scope values:
      - "user_complaints" -> exclude IT department tickets
      - "it_operations" -> include only IT department tickets
      - "all" -> return a copy of the original DataFrame

    Always returns a copy and never mutates the input.
    """
    key = (scope or "").strip().lower()
    if key not in {"user_complaints", "it_operations", "all"}:
        # tolerate UI labels passed through
        if key == "user complaints":
            key = "user_complaints"
        elif key == "it operations":
            key = "it_operations"
        elif key in {"all tickets", "all"}:
            key = "all"
    if key == "user_complaints":
        return filter_user_complaints(df)
    if key == "it_operations":
        return filter_it_operations(df)
    # default: all
    orig = _ensure_dataframe(df)
    return orig.copy()
