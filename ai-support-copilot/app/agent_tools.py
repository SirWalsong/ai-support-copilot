import json
from pathlib import Path

TICKET_STATE_PATH = Path("sample_data/ticket_state.json")


def load_ticket_state() -> dict:
    """
    Load the support ticket state from disk.
    If the file doesn't exist, a default template is returned.
    """
    if not TICKET_STATE_PATH.exists():
        # Ensure parent directory exists
        TICKET_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        default_state = {
            "ticket_id": "TCK-1002",
            "customer_name": "Alex Mercer",
            "customer_email": "alex.mercer@gmail.com",
            "subject": "Charged twice for subscription",
            "body": "I upgraded to the premium plan yesterday. My card was charged twice, but my account still shows free tier access. This is extremely frustrating and I need this fixed immediately.",
            "status": "Open",
            "sentiment": "Negative",
            "urgency": "High",
            "internal_notes": [],
            "escalated": False,
            "escalation_reason": None
        }
        save_ticket_state(default_state)
        return default_state

    try:
        with open(TICKET_STATE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        # Fallback to empty/default if file is corrupted
        return {}


def save_ticket_state(state: dict):
    """
    Save the support ticket state to disk.
    """
    TICKET_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(TICKET_STATE_PATH, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=4)


# --- EXECUTABLE AGENT TOOLS FOR GEMINI ---

def update_ticket_status(status: str) -> str:
    """
    Update the current status of the customer support ticket.
    Use this tool when the customer or an agent requests to change the ticket status.

    Args:
        status: The new status. Must be one of 'Open', 'Pending', 'Resolved'.
    """
    # Normalize status case
    status_lower = status.strip().capitalize()
    if status_lower not in ["Open", "Pending", "Resolved"]:
        return f"Error: Invalid status '{status}'. Allowed statuses are 'Open', 'Pending', or 'Resolved'."

    state = load_ticket_state()
    old_status = state.get("status", "Open")
    state["status"] = status_lower
    save_ticket_state(state)

    print(f"\n[TOOL CALLED] update_ticket_status(status='{status_lower}')")
    print(f"       State change: {old_status} -> {status_lower}\n")

    return f"Ticket status successfully updated from '{old_status}' to '{status_lower}'."


def add_internal_note(note: str) -> str:
    """
    Add an internal operational note or summary update to the support ticket.
    Use this tool when you want to log details for internal reference without presenting it directly as a reply.

    Args:
        note: The note content to append to the ticket's history.
    """
    if not note or not note.strip():
        return "Error: Note content cannot be empty."

    state = load_ticket_state()
    if "internal_notes" not in state:
        state["internal_notes"] = []

    clean_note = note.strip()
    state["internal_notes"].append(clean_note)
    save_ticket_state(state)

    print(f"\n[TOOL CALLED] add_internal_note()")
    print(f"       Added note: '{clean_note}'\n")

    return f"Successfully added internal note: '{clean_note}'."


def escalate_ticket(reason: str) -> str:
    """
    Escalate the support ticket to high-priority human engineering support.
    Use this tool if the customer issue involves billing anomalies, service access denial, or is high urgency.

    Args:
        reason: The reason for escalating this ticket.
    """
    if not reason or not reason.strip():
        return "Error: Escalation reason must be provided."

    state = load_ticket_state()
    state["status"] = "Escalated"
    state["escalated"] = True
    state["escalation_reason"] = reason.strip()
    save_ticket_state(state)

    print(f"\n[TOOL CALLED] escalate_ticket()")
    print(f"       Reason: '{reason.strip()}'\n")

    return f"Ticket TCK-1002 has been successfully escalated to tier-2 human engineering. Reason: {reason.strip()}."
