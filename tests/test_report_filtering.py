import pandas as pd
from pandas.testing import assert_frame_equal
from report_filtering import filter_it_operations, filter_tickets_by_scope, filter_user_complaints, is_it_department, normalize_department

def sample_df():
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5, 6],
        'department': ['IT', ' it ', 'Information Technology', 'Finance', None, ''],
        'complaint': ['a', 'b', 'c', 'd', 'e', 'f'],
    })

def test_it_variants():
    for value in ['IT', ' it ', 'I.T.', 'Information Technology', 'it support', 'Service Desk']:
        assert is_it_department(value)
    for value in ['Finance', 'HR', 'Production']:
        assert not is_it_department(value)

def test_whitespace_case_normalization():
    assert normalize_department('  InForMation   Technology  ') == 'information technology'
    assert is_it_department('  iT   ')

def test_none_blank_department_values():
    assert normalize_department(None) == ''
    assert normalize_department('') == ''
    assert not is_it_department(None)
    assert not is_it_department('')

def test_missing_department_column():
    df = pd.DataFrame({'id': [1, 2]})
    assert_frame_equal(filter_user_complaints(df), df)
    assert filter_it_operations(df).empty
    assert list(filter_it_operations(df).columns) == ['id']

def test_empty_dataframe():
    df = pd.DataFrame(columns=['id', 'department'])
    assert filter_user_complaints(df).empty
    assert filter_it_operations(df).empty
    assert filter_tickets_by_scope(df, 'All Tickets').empty

def test_source_dataframe_not_mutated():
    df = sample_df()
    original = df.copy(deep=True)
    _ = filter_user_complaints(df)
    _ = filter_it_operations(df)
    _ = filter_tickets_by_scope(df, 'User Complaints')
    assert_frame_equal(df, original)

def test_scope_filters_expected_rows():
    df = sample_df()
    assert filter_tickets_by_scope(df, 'User Complaints')['id'].tolist() == [4, 5, 6]
    assert filter_tickets_by_scope(df, 'IT Operations')['id'].tolist() == [1, 2, 3]
    assert filter_tickets_by_scope(df, 'All Tickets')['id'].tolist() == [1, 2, 3, 4, 5, 6]
