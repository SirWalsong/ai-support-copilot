import json
from pathlib import Path
from google.genai import types

from app.llm_client import LLMClient
from app.agent_tools import load_ticket_state, TICKET_STATE_PATH

CHAT_HISTORY_PATH = Path("logs/chat_history.json")


class ChatManager:
    def __init__(self):
        self.llm_client = LLMClient()
        # Initialize/load active ticket state
        self.ticket_state = load_ticket_state()

    def get_system_instruction(self) -> str:
        """
        Dynamically construct the system prompt based on the latest ticket state.
        This provides the model with complete contextual awareness of the active ticket.
        """
        # Reload latest ticket state from disk
        state = load_ticket_state()

        notes_str = "\n".join([f"- {note}" for note in state.get("internal_notes", [])])
        if not notes_str:
            notes_str = "(No internal notes added yet)"

        instruction = f"""You are a professional customer support copilot at a SaaS company.
Your goal is to assist a human support agent in resolving the active customer support ticket.
You have real-time access to the ticket state and can execute actions/tools on behalf of the agent.

--- ACTIVE TICKET DETAILS ---
Ticket ID: {state.get("ticket_id")}
Customer Name: {state.get("customer_name")}
Customer Email: {state.get("customer_email")}
Subject: {state.get("subject")}
Issue Description: "{state.get("body")}"
Current Status: {state.get("status")}
Customer Sentiment: {state.get("sentiment")}
Urgency Level: {state.get("urgency")}
Is Escalated: {state.get("escalated")}
Escalation Reason: {state.get("escalation_reason") or "None"}

--- INTERNAL NOTES LOG ---
{notes_str}

--- YOUR ROLE & GUIDELINES ---
1. You are talking to a HUMAN SUPPORT AGENT, not the customer directly. Help the agent brainstorm replies, analyze the ticket, and coordinate actions.
2. Be concise, professional, and action-oriented.
3. If the agent asks you to perform an action (e.g., update the status, add a note, escalate), call the appropriate tool.
4. When you call a tool, explain to the agent what you did and summarize the results.
5. If the ticket involves billing anomalies or subscription denials (which this one does), proactively recommend escalating the ticket if it hasn't been done already.
6. The customer is frustrated, so suggest empathetic drafted replies when requested.
"""
        return instruction

    def load_chat_history(self) -> list:
        """
        Load conversation history from disk and convert it into
        types.Content objects suitable for google-genai chat sessions.
        """
        if not CHAT_HISTORY_PATH.exists():
            return []

        try:
            with open(CHAT_HISTORY_PATH, "r", encoding="utf-8") as file:
                raw_history = json.load(file)

            history = []
            for msg in raw_history:
                role = msg.get("role")
                text = msg.get("text", "")
                history.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=text)]
                    )
                )
            return history
        except Exception as e:
            print(f"[Warning] Failed to load chat history: {str(e)}. Starting with empty history.")
            return []

    def save_chat_history(self, chat_session):
        """
        Extract conversational history from the active chat session and save it to disk.
        We filter and persist text-based messages to keep the state clean.
        """
        try:
            CHAT_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)

            history_list = []
            # chat_session.get_history() returns list of types.Content objects
            for content in chat_session.get_history():
                role = content.role
                # Combine all text parts
                text_parts = []
                for part in content.parts:
                    if part.text:
                        text_parts.append(part.text)

                if text_parts:
                    text_content = "\n".join(text_parts)
                    history_list.append({
                        "role": role,
                        "text": text_content
                    })

            with open(CHAT_HISTORY_PATH, "w", encoding="utf-8") as file:
                json.dump(history_list, file, indent=4)

        except Exception as e:
            print(f"[Error] Failed to save chat history: {str(e)}")

    def initialize_session(self):
        """
        Prepare and return an active chat session.
        Uses the latest dynamic system instruction and reloaded history.
        """
        system_instruction = self.get_system_instruction()
        history = self.load_chat_history()
        return self.llm_client.create_chat_session(
            system_instruction=system_instruction,
            history=history
        )

    def reset_session(self):
        """
        Reset the chat history and the ticket state to start fresh.
        """
        if CHAT_HISTORY_PATH.exists():
            CHAT_HISTORY_PATH.unlink()
        if TICKET_STATE_PATH.exists():
            TICKET_STATE_PATH.unlink()
        # Reloading defaults
        self.ticket_state = load_ticket_state()
