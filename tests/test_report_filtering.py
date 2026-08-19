import pandas as pd
from report_filtering import filter_tickets_by_scope, filter_user_complaints, filter_it_operations


def _make_df(dept_values):
    rows = []
    for i, d in enumerate(dept_values, start=1):
        rows.append({"id": i, "date": "2026-07-01", "user_name": f"User{i}", "department": d, "complaint": "Issue", "location": "Sector - 136 Vega", "attended_by": "Amit", "status": "Open", "category": "Other", "resolution_time": 0})
    return pd.DataFrame(rows)


def test_it_variants():
    df = _make_df(["IT", " it ", "Information Technology", "IT Department", "Finance", "Production", None, "", "HR"]) 
    original = df.copy()
    # User Complaints should exclude IT rows
    uc = filter_tickets_by_scope(df, "user_complaints")
    assert "IT" not in uc['department'].astype(str).str.strip().tolist()
    assert "Information Technology" not in uc['department'].astype(str).tolist()
    # IT Operations includes only IT
    it_ops = filter_tickets_by_scope(df, "it_operations")
    assert all([str(d).strip().lower() in {"it","information technology","it department","information technology department"} for d in it_ops['department'].astype(str).tolist()])
    # All preserves all rows
    all_df = filter_tickets_by_scope(df, "all")
    assert len(all_df) == len(df)
    # Original not mutated
    pd.testing.assert_frame_equal(df.reset_index(drop=True), original.reset_index(drop=True))


def test_missing_and_empty():
    # Missing department column
    df2 = pd.DataFrame([{"id":1, "date":"2026-07-01", "user_name":"A", "complaint":"x"}])
    uc = filter_tickets_by_scope(df2, "user_complaints")
    assert len(uc) == 1
    it_ops = filter_tickets_by_scope(df2, "it_operations")
    assert it_ops.empty
    # Empty dataframe
    empty = pd.DataFrame(columns=["id","department"]) 
    assert filter_tickets_by_scope(empty, "user_complaints").empty
    assert filter_tickets_by_scope(empty, "it_operations").empty
