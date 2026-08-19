import pandas as pd


IT_NORMALIZED_SET = {"it", "information technology", "it department", "information technology department"}


def normalize_department(value):
    """Return a normalized string for department matching.

    Safe for None/NaN/empty. Trims and lowercases the input.
    """
    if value is None:
        return ""
    try:
        # pandas NA handling
        if pd.isna(value):
            return ""
    except Exception:
        pass
    try:
        s = str(value).strip().lower()
        return s
    except Exception:
        return ""


def is_it_department(value):
    """Return True if the given department value corresponds to IT (case-insensitive).

    Recognizes: IT, it, Information Technology, IT Department, Information Technology Department
    after trimming and lowercasing.
    """
    s = normalize_department(value)
    return s in IT_NORMALIZED_SET


def _find_department_column(df: pd.DataFrame):
    """Heuristically find the department column name in the dataframe.

    Returns the column name or None if not found.
    """
    if df is None or df.empty:
        return None
    candidates = [
        "department",
        "dept",
        "assigned_department",
        "assigned_dept",
        "user_department",
        "team",
    ]
    cols = [c.lower() for c in df.columns]
    for cand in candidates:
        if cand in cols:
            # return the actual column name with original casing
            return df.columns[cols.index(cand)]
    # fallback: if there's a column literally named like 'department' but with spaces
    for c in df.columns:
        if c.strip().lower() == "department":
            return c
    return None


def filter_user_complaints(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df with IT department rows excluded.

    Handles missing department column, None/NaN/blank values, and empty DataFrames safely.
    Always returns a copy and does not mutate the input.
    """
    if df is None:
        return pd.DataFrame()
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if df.empty:
        return df.copy()
    dep_col = _find_department_column(df)
    if not dep_col:
        # No department column -> nothing to exclude
        return df.copy()
    mask_it = df[dep_col].apply(is_it_department)
    # Keep rows where NOT IT
    return df.loc[~mask_it].copy()


def filter_it_operations(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df containing only IT department rows.

    Safe for missing column/empty DataFrame.
    """
    if df is None:
        return pd.DataFrame()
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if df.empty:
        return df.copy()
    dep_col = _find_department_column(df)
    if not dep_col:
        # No department column -> nothing to include
        return df.iloc[0:0].copy()
    mask_it = df[dep_col].apply(is_it_department)
    return df.loc[mask_it].copy()


def filter_tickets_by_scope(df: pd.DataFrame, scope: str) -> pd.DataFrame:
    """Filter tickets DataFrame by scope.

    scope values:
      - 'user_complaints'
      - 'it_operations'
      - 'all'

    Always returns a copy and does not mutate the input.
    """
    if scope is None:
        scope = "user_complaints"
    scope = str(scope).strip().lower()
    if scope == "user_complaints":
        return filter_user_complaints(df)
    if scope == "it_operations":
        return filter_it_operations(df)
    # 'all' or any other -> return copy of original
    if df is None:
        return pd.DataFrame()
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    return df.copy()
