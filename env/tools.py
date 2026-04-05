def process_refund(ticket_id):
    return {
        "status": "success",
        "message": f"Refund issued for ticket {ticket_id}"
    }


def fix_technical_issue(ticket_id):
    return {
        "status": "success",
        "message": f"Technical issue resolved for ticket {ticket_id}"
    }


def restore_account(ticket_id):
    return {
        "status": "success",
        "message": f"Account access restored for ticket {ticket_id}"
    }