import pandas as pd

IT_DEPARTMENT_TOKENS = {
    'it', 'i.t', 'i.t.', 'information technology', 'informationtechnology',
    'it department', 'it dept', 'it support', 'itsupport', 'infra',
    'infrastructure', 'network', 'systems', 'system administration',
    'sysadmin', 'technology', 'tech', 'helpdesk', 'service desk', 'servicedesk',
}
COMPACT_IT_TOKENS = {t.replace(' ', '') for t in IT_DEPARTMENT_TOKENS}

def normalize_department(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ''
    text = str(value).strip().lower()
    return ' '.join(text.split())

def is_it_department(value):
    norm = normalize_department(value)
    if not norm:
        return False
    compact = norm.replace(' ', '')
    return norm in IT_DEPARTMENT_TOKENS or compact in COMPACT_IT_TOKENS

def filter_user_complaints(df):
    if df is None:
        return pd.DataFrame()
    out = df.copy()
    if out.empty or 'department' not in out.columns:
        return out
    return out.loc[~out['department'].apply(is_it_department)].copy()

def filter_it_operations(df):
    if df is None:
        return pd.DataFrame()
    out = df.copy()
    if out.empty:
        return out
    if 'department' not in out.columns:
        return out.iloc[0:0].copy()
    return out.loc[out['department'].apply(is_it_department)].copy()

def filter_tickets_by_scope(df, selected_scope):
    scope = str(selected_scope or 'User Complaints').strip().lower()
    if scope == 'it operations':
        return filter_it_operations(df)
    if scope == 'all tickets':
        return df.copy() if df is not None else pd.DataFrame()
    return filter_user_complaints(df)
