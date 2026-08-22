"""Phase 0 smoke tests for V2 router and safety flags."""

def test_v2_write_enabled_default_false():
    from config.settings import V2_WRITE_ENABLED
    assert V2_WRITE_ENABLED is False

def test_page_renderers_registered():
    from v2_pages import PAGE_RENDERERS
    expected = {"Home", "Ticket Operations", "NAS Monitoring", "Reports"}
    assert expected.issubset(set(PAGE_RENDERERS.keys()))
    for name, fn in PAGE_RENDERERS.items():
        assert callable(fn)

def test_v2_pages_import_path():
    import v2_pages.home as home
    import v2_pages.tickets as tickets
    assert callable(home.render_home_page)
    assert callable(tickets.render_tickets_page)
