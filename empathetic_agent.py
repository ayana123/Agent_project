from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from text_prompts import *
import tiktoken
from enum import Enum
from memory_manager import MemoryManager
from history_manager import HistoryManager
import re



class ConversationMode(Enum):
    USE_HISTORY = "use_history"
    NO_HISTORY = "no_history"

class EmpatheticAgent:
    def __init__(self, memory, history_path="conversation_history.json"):
        self.memory = memory
        load_dotenv()
        #TODO might need to extract it in main and pass it to the agent
        self.api_key = os.getenv("OPENAI_API_KEY_2")
        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv("OPENAI_MODEL") or "gpt-4o"
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE")) or 0.9
        self.history_path = history_path
        self.token_limit = int(os.getenv("TOKEN_LIMIT") or 10000)
        self.encoder = tiktoken.encoding_for_model(self.model)
        self.use_conversation_history_mode = ConversationMode.USE_HISTORY
        self.extract_info_temperature = 0
        
        # Initialize history manager
        self.history_manager = HistoryManager(history_path)
    
    def generate_initial_greeting(self):
        return INITIAL_GREETING
    
    def trim_history_to_fit(self, base_prompt):
        system_message = {"role": "system", "content": base_prompt}
        total_tokens = len(self.encoder.encode(base_prompt))
        trimmed_history = []
        history_exceeded_token_limit = False

        if self.use_conversation_history_mode == ConversationMode.USE_HISTORY:
            for msg in reversed(self.history_manager.get_history()):
                tokens = len(self.encoder.encode(msg["content"]))
                if total_tokens + tokens > self.token_limit:
                    history_exceeded_token_limit = True 
                    break
                trimmed_history.insert(0, msg)
                total_tokens += tokens
        
        if history_exceeded_token_limit or self.use_conversation_history_mode == ConversationMode.NO_HISTORY:
            trimmed_history = [{"role": "system", "content": f"the information that is already known about the user is {self.memory.get_state_for_prompt()}"}]
        
        return [system_message] + trimmed_history

    def ask(self, user_input=None):
        if user_input:
            last_message = self.history_manager.get_last_message()
            if last_message and last_message["role"] == "assistant": 
                self.extract_info_with_context(user_input, last_message["content"])
            
            self.history_manager.add_message("user", user_input)

        prompt = SYSTEM_BASE_PROMPT
        messages = self.trim_history_to_fit(prompt)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature
        )

        reply = response.choices[0].message.content
        self.history_manager.add_message("assistant", reply)
        return reply

    def extract_info_with_context(self, user_input: str, current_question: str) -> dict:
        prompt = self._create_extraction_prompt(user_input, current_question)
        content = self._get_extraction_response(prompt)

        # Remove markdown-style triple backticks (with or without "json")
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.DOTALL)

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = {}

        # Update memory state with extracted information
        for field in REQUIRED_FIELDS:
            if field in data and data[field]:
                self.memory.update_state(field, data[field])

        return data

    def _create_extraction_prompt(self, user_input: str, current_question: str) -> str:
        """Create the prompt for information extraction"""
        return EXTRACTION_USER_PROMPT_TEMPLATE.format(
            current_question=current_question,
            user_input=user_input
        )

    def _get_extraction_response(self, prompt: str) -> str:
        """Get the response from OpenAI for information extraction"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip()
   
    