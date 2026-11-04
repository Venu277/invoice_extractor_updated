from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session

from app.models.invoice import Invoice
from app.models.business import Business
from app.services.fy_service import filter_query_by_period, get_current_fy
from app.services.alerts_service import check_and_create_due_alerts, check_gst_deadline_alerts


def get_dashboard_data(
    db: Session,
    business_id: int,
    fy: int | None = None,
    month: str | None = None
) -> dict:
    biz = db.query(Business).filter(Business.id == business_id).first()
    fy_start = biz.fy_start_month if biz else 4
    if not fy and not month:
        fy = get_current_fy(fy_start)

    # Trigger proactive check for due and GST alerts
    check_and_create_due_alerts(db, business_id)
    check_gst_deadline_alerts(db, business_id)

    # Base query for all non-deleted invoices in tenant
    all_invoices = db.query(Invoice).filter(
        Invoice.business_id == business_id,
        Invoice.deleted_at.is_(None)
    ).all()

    # Filtered invoices for chosen period
    filtered_query = filter_query_by_period(
        db.query(Invoice).filter(Invoice.business_id == business_id, Invoice.deleted_at.is_(None)),
        fy=fy, month=month, fy_start_month=fy_start
    )
    period_invoices = filtered_query.all()

    # Period aggregates (Approved only for revenue/expense)
    approved_period = [i for i in period_invoices if i.review_status == "approved"]
    sales_invoices = [i for i in approved_period if i.direction == "sales"]
    purchase_invoices = [i for i in approved_period if i.direction in ["purchase", "unknown"]]

    sales_total = sum(i.total for i in sales_invoices)
    purchase_total = sum(i.total for i in purchase_invoices)
    output_gst = sum(i.cgst + i.sgst + i.igst + i.cess for i in sales_invoices)
    input_gst = sum(i.cgst + i.sgst + i.igst + i.cess for i in purchase_invoices)

    # Outstanding amounts across all active approved invoices
    active_approved = [i for i in all_invoices if i.review_status == "approved"]
    receivables_outstanding = sum(
        i.total - i.amount_paid for i in active_approved
        if i.direction == "sales" and i.payment_status in ["unpaid", "partial"]
    )
    payables_outstanding = sum(
        i.total - i.amount_paid for i in active_approved
        if i.direction in ["purchase", "unknown"] and i.payment_status in ["unpaid", "partial"]
    )

    pending_review_count = sum(1 for i in all_invoices if i.review_status == "pending_review")
    today_for_balances = date.today()
    overdue_customer_count = sum(
        1 for invoice in active_approved
        if invoice.direction == "sales"
        and invoice.payment_status in ["unpaid", "partial"]
        and invoice.due_date is not None
        and invoice.due_date < today_for_balances
    )
    overdue_customer_30_count = sum(
        1 for invoice in active_approved
        if invoice.direction == "sales"
        and invoice.payment_status in ["unpaid", "partial"]
        and invoice.due_date is not None
        and invoice.due_date < today_for_balances - timedelta(days=30)
    )
    due_this_week_count = sum(
        1 for invoice in active_approved
        if invoice.direction in ["purchase", "unknown"]
        and invoice.payment_status in ["unpaid", "partial"]
        and invoice.due_date is not None
        and today_for_balances <= invoice.due_date <= today_for_balances + timedelta(days=7)
    )
    validation_issue_count = sum(
        1 for invoice in all_invoices
        if invoice.validation_status in ["warnings", "errors"]
    )

    attention_items = []
    if pending_review_count:
        attention_items.append({
            "message": f"{pending_review_count} invoice{'s' if pending_review_count != 1 else ''} need review",
            "action": "Review", "href": "/invoices?status=pending_review", "severity": "warning"
        })
    if validation_issue_count:
        attention_items.append({
            "message": f"{validation_issue_count} invoice{'s' if validation_issue_count != 1 else ''} need tax or total checks",
            "action": "Check", "href": "/invoices", "severity": "warning"
        })
    if overdue_customer_30_count:
        attention_items.append({
            "message": f"{overdue_customer_30_count} customer payment{'s' if overdue_customer_30_count != 1 else ''} more than 30 days late",
            "action": "View", "href": "/reports", "severity": "danger"
        })
    if due_this_week_count and len(attention_items) < 3:
        attention_items.append({
            "message": f"{due_this_week_count} supplier payment{'s' if due_this_week_count != 1 else ''} due this week",
            "action": "View", "href": "/reports", "severity": "warning"
        })

    available_months = {
        invoice.invoice_date.strftime("%Y-%m"): invoice.invoice_date.strftime("%B %Y")
        for invoice in all_invoices if invoice.invoice_date
    }
    current_month_key = date.today().strftime("%Y-%m")
    available_months.setdefault(current_month_key, date.today().strftime("%B %Y"))
    recent_invoices = sorted(
        all_invoices,
        key=lambda invoice: invoice.created_at or datetime.min,
        reverse=True
    )[:5]

    # Month-on-month change calculation
    mom_change_pct = 0.0
    today = date.today()
    if month:
        selected_year, selected_month_num = (int(part) for part in month.split("-", 1))
        cur_month_str = f"{selected_year}-{selected_month_num:02d}"
        last_month_date = date(selected_year, selected_month_num, 1) - date.resolution
    else:
        cur_month_str = f"{today.year}-{today.month:02d}"
        last_month_date = today.replace(day=1) - date.resolution
    prev_month_str = f"{last_month_date.year}-{last_month_date.month:02d}"

    cur_sales = sum(
        i.total for i in all_invoices
        if i.direction == "sales" and i.review_status == "approved"
        and i.invoice_date and f"{i.invoice_date.year}-{i.invoice_date.month:02d}" == cur_month_str
    )
    prev_sales = sum(
        i.total for i in all_invoices
        if i.direction == "sales" and i.review_status == "approved"
        and i.invoice_date and f"{i.invoice_date.year}-{i.invoice_date.month:02d}" == prev_month_str
    )
    if prev_sales > 0:
        mom_change_pct = round(((cur_sales - prev_sales) / prev_sales) * 100.0, 1)

    return {
        "period": {"fy": fy, "month": month},
        "invoice_count": len(all_invoices),
        "approved_invoice_count": len(active_approved),
        "period_invoice_count": len(period_invoices),
        "period_approved_invoice_count": len(approved_period),
        "has_previous_month_sales": month is not None and prev_sales > 0,
        "available_months": [
            {"value": key, "label": available_months[key]}
            for key in sorted(available_months, reverse=True)
        ],
        "recent_invoices": [
            {
                "id": invoice.id,
                "invoice_no": invoice.invoice_no,
                "party_name": invoice.party.name if invoice.party else "Unknown party",
                "total": invoice.total,
                "review_status": invoice.review_status,
                "payment_status": invoice.payment_status,
            }
            for invoice in recent_invoices
        ],
        "overdue_customer_count": overdue_customer_count,
        "overdue_customer_30_count": overdue_customer_30_count,
        "due_this_week_count": due_this_week_count,
        "validation_issue_count": validation_issue_count,
        "attention_items": attention_items,
        "sales_total": sales_total,
        "purchase_total": purchase_total,
        "output_gst": output_gst,
        "input_gst": input_gst,
        "receivables_outstanding": receivables_outstanding,
        "payables_outstanding": payables_outstanding,
        "pending_review_count": pending_review_count,
        "mom_change_pct": mom_change_pct,
    }
