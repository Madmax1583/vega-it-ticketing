"""Phase 0 smoke tests for V2 router and safety flags."""

from pathlib import Path


def test_v2_write_enabled_default_false():
    from config.settings import V2_WRITE_ENABLED
    assert V2_WRITE_ENABLED is False


def test_page_renderers_registered():
    from v2_pages import PAGE_RENDERERS
    expected = {"Home", "Ticket Operations", "NAS Monitoring", "Reports", "Data Quality"}
    assert expected.issubset(set(PAGE_RENDERERS.keys()))
    for name, fn in PAGE_RENDERERS.items():
        assert callable(fn)


def test_v2_pages_import_path():
    import v2_pages.home as home
    import v2_pages.tickets as tickets
    import v2_pages.nas as nas
    import v2_pages.reports as reports
    import v2_pages.data_quality as dq
    assert callable(home.render_home_page)
    assert callable(tickets.render_tickets_page)
    assert callable(nas.render_nas_page)
    assert callable(reports.render_reports_page)
    assert callable(dq.render_data_quality_page)


def test_no_streamlit_pages_directory():
    """Ensure Streamlit auto-discovery cannot bypass the custom router."""
    assert not Path("pages").exists(), "pages/ directory must be removed to prevent auto-discovery"


def test_safe_load_tickets_returns_tuple_on_error(monkeypatch):
    """Verify _safe_load_tickets returns (DataFrame, error_string) on failure."""
    import pandas as pd
    from app import _safe_load_tickets

    def _raise(*args, **kwargs):
        raise RuntimeError("Simulated load failure")

    monkeypatch.setattr("services.tickets.load_tickets", _raise)
    tickets, err = _safe_load_tickets()
    assert isinstance(tickets, pd.DataFrame)
    assert tickets.empty
    assert isinstance(err, str)
    assert "Simulated load failure" in err


def test_safe_load_nas_returns_tuple_on_error(monkeypatch):
    """Verify _safe_load_nas returns (DataFrame, error_string) on failure."""
    import pandas as pd
    from app import _safe_load_nas

    def _raise(*args, **kwargs):
        raise RuntimeError("Simulated NAS load failure")

    monkeypatch.setattr("services.nas.load_nas_data", _raise)
    nas, err = _safe_load_nas()
    assert isinstance(nas, pd.DataFrame)
    assert nas.empty
    assert isinstance(err, str)
    assert "Simulated NAS load failure" in err
