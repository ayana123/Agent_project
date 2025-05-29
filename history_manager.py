import os
import json
from typing import List, Dict, Any
from datetime import datetime

class HistoryManager:
    def __init__(self, history_path: str = "conversation_history.json"):
        self.history_path = history_path
        self.conversation_history: List[Dict[str, Any]] = []
        self.clean_history_file()

    def clean_history_file(self) -> None:
        """Clean the conversation history file on startup"""
        try:
            if os.path.exists(self.history_path):
                os.remove(self.history_path)
                print(f"Cleaned conversation history file: {self.history_path}")
        except Exception as e:
            print(f"Error cleaning history file: {e}")

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history"""
        message = {
            "role": role,
            "content": content
           # "timestamp": datetime.now().isoformat()
        }
        self.conversation_history.append(message)
        self.save_history()

    def get_history(self) -> List[Dict[str, Any]]:
        """Get the current conversation history"""
        return self.conversation_history

    def get_last_message(self) -> Dict[str, Any]:
        """Get the last message from the conversation history"""
        return self.conversation_history[-1] if self.conversation_history else None

    def save_history(self) -> None:
        """Save the conversation history to file"""
        try:
            with open(self.history_path, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
        except Exception as e:
            print(f"Failed to save conversation history: {e}")

    def load_history(self) -> List[Dict[str, Any]]:
        """Load the conversation history from file"""
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load conversation history: {e}")
        return []

    def get_history_for_prompt(self, max_messages: int = 5) -> List[Dict[str, Any]]:
        """Get the last N messages for the prompt"""
        return self.conversation_history[-max_messages:] if self.conversation_history else []

    def clear_history(self) -> None:
        """Clear the current conversation history"""
        self.conversation_history = []
        self.clean_history_file() 