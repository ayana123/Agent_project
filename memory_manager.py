import json
from text_prompts import REQUIRED_FIELDS

class MemoryManager:
    def __init__(self, file_path="conversation_memory.json"):
        self.file_path = file_path
        self.load()

    def load(self):
        try:
            with open(self.file_path, "r") as f:
                self.state = json.load(f)
        except FileNotFoundError:
            self.state = {}

    def save(self):
        with open(self.file_path, "w") as f:
            json.dump(self.state, f, indent=2)

    def get_state(self):
        return self.state

    def get_state_for_prompt(self):
        return {k: v for k, v in self.state.items() if k in REQUIRED_FIELDS}

    def update_state(self, key, value):
        self.state[key] = value
        self.save()

    def is_complete(self):
        return all(self.state.get(k) for k in REQUIRED_FIELDS)
        
    def clear_memory(self):
        """Clear the conversation memory"""
        self.state = {}
        self.save() 
    
