"""Business logic services (Phase 2+)."""

from services.auth import (
    authenticate_user,
    get_all_users,
    get_role_pages,
    get_user_by_username,
    hash_password,
    set_user_password,
    verify_password,
)
from services.nas import (
    compute_nas_changes,
    load_nas_data,
    normalize_nas_df,
    save_nas_log,
    delete_nas_log,
)
from services.reports import (
    build_department_summary,
    build_excel_report,
    build_location_summary,
    build_technician_performance,
    build_ticket_exec_metrics,
)
from services.tickets import (
    auto_categorize,
    format_ticket_number,
    load_tickets,
    normalize_category,
    normalize_ticket_df,
    prepare_ticket_view,
    save_ticket,
    update_ticket,
    delete_ticket,
)

__all__ = [
    "authenticate_user",
    "get_all_users",
    "get_role_pages",
    "get_user_by_username",
    "hash_password",
    "set_user_password",
    "verify_password",
    "auto_categorize",
    "format_ticket_number",
    "load_tickets",
    "normalize_category",
    "normalize_ticket_df",
    "prepare_ticket_view",
    "save_ticket",
    "update_ticket",
    "delete_ticket",
    "compute_nas_changes",
    "load_nas_data",
    "normalize_nas_df",
    "save_nas_log",
    "delete_nas_log",
    "build_department_summary",
    "build_excel_report",
    "build_location_summary",
    "build_technician_performance",
    "build_ticket_exec_metrics",
]
