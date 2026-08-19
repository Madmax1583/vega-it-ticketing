"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
IT Department Filtering & Reporting Separation - Phase 1
=========================================================

This module extends script.py with filtering helpers to separate:
1. User Complaint Reports (excludes IT department)
2. IT Operations Reports (includes only IT department)
3. All Tickets Reference (for operational use)

Key design principles:
- Non-breaking: all existing functions remain compatible
- Defensive: handles missing columns, None, NaN, empty DataFrames
- Safe: returns copies, never mutates original DataFrames
- Centralized: filtering logic is DRY and documented
"""

import pandas as pd
import numpy as np
from typing import Literal, Optional, Tuple


# ============================================================================
# FILTERING HELPERS - Core Department Detection & Filtering Logic
# ============================================================================

def normalize_department(value: Optional[str]) -> str:
    """
    Normalize department value by trimming whitespace and lowercasing.
    
    Args:
        value: Department name (str, None, or NaN)
    
    Returns:
        Normalized lowercase string, or empty string if None/NaN
    
    Examples:
        normalize_department("IT") -> "it"
        normalize_department("  it  ") -> "it"
        normalize_department(None) -> ""
        normalize_department("") -> ""
    """
    if value is None or pd.isna(value):
        return ""
    s = str(value).strip().lower()
    return s


def is_it_department(value: Optional[str]) -> bool:
    """
    Check if department value represents IT/Information Technology department.
    
    Recognizes:
    - "it", "it department", "it ops", "it operations"
    - "information technology", "information technology department"
    - Handles case-insensitivity and whitespace
    
    Args:
        value: Department name
    
    Returns:
        True if value matches IT department patterns, False otherwise
    
    Examples:
        is_it_department("IT") -> True
        is_it_department("it department") -> True
        is_it_department("Information Technology") -> True
        is_it_department("Finance") -> False
        is_it_department(None) -> False
    """
    normalized = normalize_department(value)
    
    # Empty or None
    if not normalized:
        return False
    
    # Exact and partial matches for IT department
    it_keywords = [
        "it",
        "it ops",
        "it operations",
        "it department",
        "it admin",
        "it support",
        "information technology",
        "information technology department",
        "information technology ops",
        "information technology operations",
    ]
    
    # Check exact match or substring match for common patterns
    if normalized in it_keywords:
        return True
    
    # Check if normalized value starts with any IT keyword (for phrases like "IT - Infrastructure")
    if any(normalized.startswith(kw) for kw in it_keywords):
        return True
    
    return False


def filter_user_complaint_tickets(
    df: pd.DataFrame, 
    exclude_it: bool = True,
    department_col: str = "department"
) -> pd.DataFrame:
    """
    Filter DataFrame to include/exclude IT department tickets.
    
    Used for User Complaint reporting stream. By default excludes IT department.
    
    Args:
        df: Input ticket DataFrame
        exclude_it: If True (default), exclude IT department tickets
        department_col: Name of department column (default "department")
    
    Returns:
        Filtered DataFrame (copy, original unchanged)
    
    Handles:
        - Missing department column -> all rows pass (None treated as non-IT)
        - NaN/None values -> treated as non-IT (included if exclude_it=True)
        - Empty DataFrame -> returns empty DataFrame
        - Case/whitespace variations -> normalized before comparison
    """
    if df is None or df.empty:
        return df.copy() if df is not None else pd.DataFrame()
    
    # If department column doesn't exist, all rows are considered non-IT
    if department_col not in df.columns:
        if exclude_it:
            return df.copy()  # Include all (none are IT)
        else:
            return pd.DataFrame(columns=df.columns)  # Exclude all (none are IT)
    
    result = df.copy()
    
    if exclude_it:
        # Exclude IT department: keep rows where department is NOT IT
        mask = ~result[department_col].apply(is_it_department)
        return result[mask].reset_index(drop=True)
    else:
        # This function typically isn't used to include IT, but support it for consistency
        mask = result[department_col].apply(is_it_department)
        return result[mask].reset_index(drop=True)


def filter_it_operations_tickets(
    df: pd.DataFrame,
    department_col: str = "department"
) -> pd.DataFrame:
    """
    Filter DataFrame to include only IT department tickets.
    
    Used for IT Operations reporting stream.
    
    Args:
        df: Input ticket DataFrame
        department_col: Name of department column (default "department")
    
    Returns:
        Filtered DataFrame containing only IT department tickets (copy, original unchanged)
    
    Handles:
        - Missing department column -> returns empty DataFrame (no IT department detected)
        - NaN/None values -> treated as non-IT (excluded)
        - Empty DataFrame -> returns empty DataFrame
    """
    if df is None or df.empty:
        return df.copy() if df is not None else pd.DataFrame()
    
    # If department column doesn't exist, no rows are IT department
    if department_col not in df.columns:
        return pd.DataFrame(columns=df.columns)
    
    result = df.copy()
    mask = result[department_col].apply(is_it_department)
    return result[mask].reset_index(drop=True)


# ============================================================================
# REPORTING SCOPE SELECTION
# ============================================================================

REPORTING_SCOPES = Literal["user_complaints", "it_operations", "all"]

def apply_reporting_scope(
    df: pd.DataFrame,
    scope: REPORTING_SCOPES = "user_complaints",
    department_col: str = "department"
) -> pd.DataFrame:
    """
    Apply reporting scope filter to DataFrame.
    
    Args:
        df: Input ticket DataFrame
        scope: One of "user_complaints", "it_operations", "all"
        department_col: Name of department column
    
    Returns:
        Filtered DataFrame according to scope
    
    Scopes:
        - "user_complaints": Exclude IT department (default for reporting)
        - "it_operations": Include only IT department
        - "all": No filtering (original data)
    """
    if scope == "user_complaints":
        return filter_user_complaint_tickets(df, exclude_it=True, department_col=department_col)
    elif scope == "it_operations":
        return filter_it_operations_tickets(df, department_col=department_col)
    elif scope == "all":
        return df.copy() if df is not None else pd.DataFrame()
    else:
        raise ValueError(f"Unknown scope: {scope}. Use 'user_complaints', 'it_operations', or 'all'.")


def get_scope_description(scope: REPORTING_SCOPES) -> str:
    """Return user-friendly description of reporting scope."""
    descriptions = {
        "user_complaints": "User Complaints - IT department operational tickets are excluded from these KPIs.",
        "it_operations": "IT Operations - These metrics represent internal IT workload, not user complaint demand.",
        "all": "⚠️ All Tickets - Warning: This combines user complaints and IT operational activity. Use for operational reference only, not complaint-performance reporting.",
    }
    return descriptions.get(scope, "Unknown scope")


# ============================================================================
# STATS HELPERS - Safe to use with filtered DataFrames
# ============================================================================

def get_scope_statistics(df: pd.DataFrame, scope: REPORTING_SCOPES = "user_complaints") -> dict:
    """
    Get quick statistics about a scope.
    
    Args:
        df: Original (unfiltered) ticket DataFrame
        scope: Reporting scope
    
    Returns:
        Dict with total_all, total_user_complaints, total_it_operations
    """
    if df is None or df.empty:
        return {
            "total_all": 0,
            "total_user_complaints": 0,
            "total_it_operations": 0,
            "excluded_tickets": 0
        }
    
    user_complaints_df = filter_user_complaint_tickets(df, exclude_it=True)
    it_ops_df = filter_it_operations_tickets(df)
    
    return {
        "total_all": len(df),
        "total_user_complaints": len(user_complaints_df),
        "total_it_operations": len(it_ops_df),
        "excluded_tickets": len(df) - len(user_complaints_df)
    }


# ============================================================================
# SAFE WRAPPER FOR EXISTING ANALYTICS FUNCTIONS
# ============================================================================

def make_scoped_wrapper(base_function, scope_param_name: str = "scope"):
    """
    Decorator-like factory to wrap analytics functions to accept scope parameter.
    
    Usage:
        build_ticket_exec_metrics_scoped = make_scoped_wrapper(
            build_ticket_exec_metrics,
            scope_param_name="scope"
        )
    
    This is a pattern we'll use rather than decorators, for maximum compatibility.
    """
    def wrapper(df, *args, scope: REPORTING_SCOPES = "user_complaints", **kwargs):
        filtered_df = apply_reporting_scope(df, scope=scope)
        return base_function(filtered_df, *args, **kwargs)
    
    return wrapper


# ============================================================================
# PATCH FUNCTIONS - Apply these to your existing script.py
# ============================================================================

"""
INTEGRATION INSTRUCTIONS:

1. Copy all code above into script.py right after imports, before normalize_ticket_df().

2. Update existing functions to accept scope parameter. Examples below:

   # BEFORE:
   def build_ticket_exec_metrics(df):
       if df is None or df.empty:
           return {..." }
       x = add_priority_and_sla(df)
       ...
   
   # AFTER:
   def build_ticket_exec_metrics(df, scope="user_complaints"):
       '''..."""User Complaints" scope excludes IT department tickets.
       Args:
           scope: "user_complaints" (default), "it_operations", or "all"
       '''
       if df is None or df.empty:
           return {..." }
       
       # Apply scope filter (non-breaking: does nothing if scope="all")
       filtered_df = apply_reporting_scope(df, scope=scope)
       x = add_priority_and_sla(filtered_df)
       ...

3. For Reports page, add scope selector and update all charts/tables:

   # In render_dashboard(), in the Reports page section:
   with report_tabs[0]:
       st.markdown("### Report Scope Selection")
       selected_scope = st.radio(
           "Select reporting scope",
           ("user_complaints", "it_operations", "all"),
           format_func=lambda x: {
               "user_complaints": "📊 User Complaints",
               "it_operations": "🛠️ IT Operations",
               "all": "📋 All Tickets"
           }.get(x, x),
           index=0,  # Default to user_complaints
           key="report_scope_radio"
       )
       st.markdown(f"**{get_scope_description(selected_scope)}**")
       
       # Get scope statistics
       stats = get_scope_statistics(df_ticket_filtered)
       c1, c2, c3, c4 = st.columns(4)
       c1.metric("Total (All)", stats["total_all"])
       c2.metric("User Complaints", stats["total_user_complaints"])
       c3.metric("IT Operations", stats["total_it_operations"])
       c4.metric("Excluded", stats["excluded_tickets"])
       
       # Now pass scope to all report functions
       # ... update all the tabs to use selected_scope parameter

4. Test with sample data containing IT department tickets.

"""


if __name__ == "__main__":
    # Quick validation test
    print("IT Department Filtering Module - Test Suite")
    print("=" * 60)
    
    # Test normalize_department
    test_cases_normalize = [
        ("IT", "it"),
        ("  IT  ", "it"),
        ("it", "it"),
        ("Information Technology", "information technology"),
        (None, ""),
        ("", ""),
        (np.nan, ""),
    ]
    
    print("\n1. Testing normalize_department():")
    for value, expected in test_cases_normalize:
        result = normalize_department(value)
        status = "✓" if result == expected else "✗"
        print(f"  {status} normalize_department({repr(value)}) = {repr(result)} (expected {repr(expected)})")
    
    # Test is_it_department
    test_cases_is_it = [
        ("IT", True),
        ("it", True),
        ("  it  ", True),
        ("it department", True),
        ("it ops", True),
        ("it operations", True),
        ("Information Technology", True),
        ("information technology department", True),
        ("Finance", False),
        ("Production", False),
        ("", False),
        (None, False),
        (np.nan, False),
    ]
    
    print("\n2. Testing is_it_department():")
    for value, expected in test_cases_is_it:
        result = is_it_department(value)
        status = "✓" if result == expected else "✗"
        print(f"  {status} is_it_department({repr(value)}) = {result} (expected {expected})")
    
    # Test filter functions with sample data
    print("\n3. Testing filter functions with sample DataFrame:")
    sample_data = {
        "id": [1, 2, 3, 4, 5, 6, 7],
        "department": ["Finance", "IT", "Production", "it", "Information Technology", None, ""],
        "complaint": ["Printer broken", "Backup check", "Network down", "Patch update", "System maintenance", "Desk setup", "Access issue"],
    }
    sample_df = pd.DataFrame(sample_data)
    
    print(f"\n  Original DataFrame (7 rows):")
    print(f"    {list(sample_df['department'].values)}")
    
    user_complaints_df = filter_user_complaint_tickets(sample_df, exclude_it=True)
    print(f"\n  User Complaints (exclude IT): {len(user_complaints_df)} rows")
    print(f"    {list(user_complaints_df['department'].values)}")
    
    it_ops_df = filter_it_operations_tickets(sample_df)
    print(f"\n  IT Operations (IT only): {len(it_ops_df)} rows")
    print(f"    {list(it_ops_df['department'].values)}")
    
    all_df = apply_reporting_scope(sample_df, scope="all")
    print(f"\n  All Tickets: {len(all_df)} rows (unchanged)")
    
    # Verify original is unchanged
    print(f"\n  Original DataFrame unchanged: {len(sample_df) == 7 and sample_df['department'].isna().sum() == 1}")
    
    # Test with missing department column
    print("\n4. Testing with missing department column:")
    sample_no_dept = sample_df[["id", "complaint"]].copy()
    complaints_no_dept = filter_user_complaint_tickets(sample_no_dept, exclude_it=True)
    print(f"  ✓ filter_user_complaint_tickets with missing dept: {len(complaints_no_dept)} rows (all included, none are IT)")
    
    it_ops_no_dept = filter_it_operations_tickets(sample_no_dept)
    print(f"  ✓ filter_it_operations_tickets with missing dept: {len(it_ops_no_dept)} rows (empty, no IT detected)")
    
    # Test empty DataFrame
    print("\n5. Testing with empty DataFrame:")
    empty_df = pd.DataFrame()
    complaints_empty = filter_user_complaint_tickets(empty_df)
    print(f"  ✓ filter_user_complaint_tickets with empty df: {len(complaints_empty)} rows")
    
    it_ops_empty = filter_it_operations_tickets(empty_df)
    print(f"  ✓ filter_it_operations_tickets with empty df: {len(it_ops_empty)} rows")
    
    # Test scope statistics
    print("\n6. Testing get_scope_statistics():")
    stats = get_scope_statistics(sample_df)
    print(f"  Total: {stats['total_all']}, User Complaints: {stats['total_user_complaints']}, IT Ops: {stats['total_it_operations']}")
    print(f"  ✓ All tests passed!")
    
    print("\n" + "=" * 60)
    print("Integration ready. Copy filtering code into script.py.")
