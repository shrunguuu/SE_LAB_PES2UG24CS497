
"""Support ticket tracker with basic ticket management and JSON persistence."""

import json
import logging
import os

TICKETS = {}


def create_ticket(
    title,
    description,
    reporter,
    priority="medium",
    category="general",
    audit_log=None,
):
    """Create a support ticket and optionally record its creation."""
    if not title:
        return None

    if audit_log is None:
        audit_log = []

    ticket_id = str(len(TICKETS) + 1)
    ticket = {
        "id": ticket_id,
        "title": title,
        "description": description,
        "priority": priority,
        "category": category,
        "status": "open",
        "reporter": reporter,
        "assignee": None,
    }
    TICKETS[ticket_id] = ticket
    audit_log.append(f"Created ticket {ticket_id} for {reporter}")
    return ticket


def assign_ticket(ticket_id, agent, notify=False):
    """Assign a ticket to an agent; return False if the ticket is missing."""
    del notify
    ticket = TICKETS.get(ticket_id)
    if ticket is None:
        return False

    ticket["assignee"] = agent
    return True


def update_status(ticket_id, status):
    """Update and return a ticket's status."""
    ticket = TICKETS.get(ticket_id)
    if ticket is None:
        return None

    ticket["status"] = status
    return ticket


def search_tickets(status=None, priority=None):
    """Return tickets matching the optional status and priority filters."""
    results = []
    for ticket in TICKETS.values():
        if status is not None and ticket["status"] != status:
            continue
        if priority is not None and ticket["priority"] != priority:
            continue
        results.append(ticket)
    return results


def save_tickets(path="tickets.json"):
    """Save all tickets to a JSON file."""
    with open(path, "w", encoding="utf-8") as ticket_file:
        json.dump(TICKETS, ticket_file, indent=2)


def load_tickets(path="tickets.json"):
    """Load tickets from a JSON file."""
    global TICKETS
    with open(path, "r", encoding="utf-8") as ticket_file:
        TICKETS = json.load(ticket_file)


def print_ticket_report():
    """Print a summary of the current tickets."""
    print("Support Tickets")
    if not TICKETS:
        print("No tickets yet")
        return

    for ticket_id, ticket in TICKETS.items():
        print(ticket_id, ticket["title"], ticket["status"])


def close_ticket(ticket_id):
    """Close a ticket; return False if it does not exist."""
    ticket = TICKETS.get(ticket_id)
    if ticket is None:
        return False

    ticket["status"] = "closed"
    return True


def is_open(ticket_id):
    """Return whether a ticket is open or in progress."""
    ticket = TICKETS.get(ticket_id)
    return ticket is not None and ticket["status"] in {
        "open",
        "in_progress",
    }


def main():
    """Run the support ticket tracker demonstration."""
    logging.basicConfig(level=logging.INFO)
    create_ticket(
        "Cannot sign in",
        "Password reset link fails",
        "alex@example.com",
    )
    create_ticket(
        "Billing question",
        "Charged twice",
        "lee@example.com",
        "high",
    )
    assign_ticket("1", "agent-01")
    update_status("1", "in_progress")
    print_ticket_report()
    logging.info("Tickets created: %s", len(TICKETS))
    print("Ticket 1 open?", is_open("1"))

    ticket_id = input("Ticket id to close (Enter to skip): ")
    if ticket_id:
        if not close_ticket(ticket_id):
            print(f"Ticket {ticket_id} does not exist.")

    save_tickets()

    if os.environ.get("RUN_UNSAFE_DEMO") == "1":
        print("Unsafe demo disabled; arbitrary code execution is not supported.")


if __name__ == "__main__":
    main()
