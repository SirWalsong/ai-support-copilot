import sys

# Reconfigure stdout/stdin to UTF-8 to prevent UnicodeEncodeErrors on Windows terminals when printing emojis
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stdin, 'reconfigure'):
    sys.stdin.reconfigure(encoding='utf-8')

from app.chat_manager import ChatManager
from app.agent_tools import load_ticket_state

def display_ticket_details():
    """
    Format and display the active ticket state in a premium CLI UI.
    """
    state = load_ticket_state()
    print("\n" + "=" * 55)
    print(f"🎫 ACTIVE TICKET ID: {state.get('ticket_id')} ({state.get('status')})")
    print("=" * 55)
    print(f"Customer Name  : {state.get('customer_name')}")
    print(f"Customer Email : {state.get('customer_email')}")
    print(f"Subject        : {state.get('subject')}")
    print(f"Description    : {state.get('body')}")
    print(f"Sentiment      : {state.get('sentiment')}")
    print(f"Urgency        : {state.get('urgency')}")
    print(f"Is Escalated   : {state.get('escalated')}")
    if state.get("escalated"):
        print(f"Escalation Rsn : {state.get('escalation_reason')}")

    print("\nInternal Notes Log:")
    notes = state.get("internal_notes", [])
    if notes:
        for idx, note in enumerate(notes, 1):
            print(f"  {idx}. {note}")
    else:
        print("  (No internal notes added yet)")
    print("=" * 55 + "\n")


def start_chat_loop(chat_manager: ChatManager):
    """
    Run the interactive stateful conversation loop.
    """
    print("\nConnecting to Gemini Support Copilot...")
    try:
        chat = chat_manager.initialize_session()
        print("Session initialized successfully! Loading history...\n")
    except Exception as e:
        print(f"Fatal: Could not initialize chat session. {str(e)}")
        return

    # Check if there is already history
    history = chat_manager.load_chat_history()
    if history:
        print("--- CONVERSATION HISTORY ---")
        for msg in history:
            role_label = "Copilot" if msg.role == "model" else "Agent"
            # Extract text parts
            parts = []
            for part in msg.parts:
                if part.text:
                    parts.append(part.text)
            print(f"💬 {role_label}: {' '.join(parts)}")
        print("----------------------------\n")
    else:
        # Prompt initial greeting
        print("🤖 Copilot: Hello Agent! I am ready to review ticket TCK-1002. How can I assist you today?")

    print("(Type 'exit' or 'back' to return to the main menu)\n")

    while True:
        try:
            user_input = input("👤 You (Agent): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nReturning to menu...")
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "back"]:
            print("Saving session and exiting chat...")
            chat_manager.save_chat_history(chat)
            break

        print("🤖 Copilot is thinking...")
        try:
            # Send message. The SDK executes registered tools automatically if requested!
            response = chat.send_message(user_input)
            print(f"\n🤖 Copilot:\n{response.text}\n")
            # Save history immediately after each turn
            chat_manager.save_chat_history(chat)
        except Exception as e:
            print(f"\n❌ Error communication with Gemini: {str(e)}\n")


def main():
    chat_manager = ChatManager()

    while True:
        print("*" * 55)
        print("      🤖 GEMINI STATEFUL SUPPORT COPILOT CLI 🤖      ")
        print("*" * 55)
        print("  1. 💬 Start / Resume Chat Session")
        print("  2. 🎫 Show Active Ticket State")
        print("  3. 🔄 Reset Session (Start Fresh)")
        print("  4. ❌ Exit")
        print("*" * 55)

        choice = input("Enter option (1-4): ").strip()

        if choice == "1":
            start_chat_loop(chat_manager)
        elif choice == "2":
            display_ticket_details()
        elif choice == "3":
            confirm = input("Are you sure you want to reset the state and history? (y/N): ").strip().lower()
            if confirm == "y":
                chat_manager.reset_session()
                print("Session reset successfully. Ticket state and history cleared!\n")
            else:
                print("Reset cancelled.\n")
        elif choice == "4":
            print("Exiting Copilot CLI. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid selection. Please choose 1, 2, 3, or 4.\n")


if __name__ == "__main__":
    main()