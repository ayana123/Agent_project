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


class EmpatheticAgent:
    def __init__(self, memory, history_path="conversation_history.json"):

        self.memory = memory
        self.history_path = history_path

        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Missing OpenAI API Key. Please set 'OPENAI_API_KEY' in your environment.")
        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv("OPENAI_MODEL") or "gpt-4o"
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE")) or 0.8
        self.strict_temperature = float(os.getenv("STRICT_TEMPERATURE")) or 0.2
        self.token_limit = int(os.getenv("TOKEN_LIMIT") or 10000)
        self.use_conversation_history= bool(os.getenv("USE_HISTORY") or True) 
        
        # Initialize history manager
        self.history_manager = HistoryManager(history_path)
        self.encoder = tiktoken.encoding_for_model(self.model)
    
       
    def trim_history_to_fit(self, base_prompt):
        """
        Read and trim the conversation history to fit within the token limit 
        and prepare it to be sent as part of the prompt to the language model.
        - If conversation history is enabled, it includes as much recent history as possible.
        - If history is disabled (USE_HISTORY=False) or exceeds the token limit, 
        it includes a summary of the data collected so far from the user.
        """
        system_message = {"role": "system", "content": base_prompt}
        total_tokens = len(self.encoder.encode(base_prompt))
        trimmed_history = []
        history_exceeded_token_limit = False

        if self.use_conversation_history:
            for msg in reversed(self.history_manager.get_history()):
                tokens = len(self.encoder.encode(msg["content"]))
                if total_tokens + tokens > self.token_limit:
                    history_exceeded_token_limit = True 
                    break
                trimmed_history.insert(0, msg)
                total_tokens += tokens
        
        if history_exceeded_token_limit or not self.use_conversation_history:
            trimmed_history = [{"role": "system", "content": f"the information that is already known about the user is {self.memory.get_state_for_prompt()}"}]
        
        return [system_message] + trimmed_history

    def ask(self, user_input=None):
        """
        This function processes the user's input by performing the following steps:
        1. Extracts relevant information based on the user's response and the agent's last question.
        2. Sends the updated conversation history to the agent to generate the next appropriate question.
        """

        if user_input is None:
            user_input = ""
    
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
        """
        Extracts structured information from the user's response using OpenAI.
    
        Args:
        user_input: The user's response text
        current_question: The last question asked by the agent
    
        Returns:
        dict: Extracted information about name, age, diagnosis, treatment, and support system.
        """
        prompt = self._create_extraction_prompt(user_input, current_question)
        content = self._get_extraction_response(prompt)

        # Remove markdown-style triple backticks (with or without "json")
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.DOTALL)

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = {}
        updated_key = None

        # Update memory state with extracted information
        for field in REQUIRED_FIELDS:
            if field in data and data[field]:
                self.memory.update_state(field, data[field])

        return data, updated_key

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
            temperature=self.strict_temperature
        )
        return response.choices[0].message.content.strip()

    def generate_goodbye_message(self, reason: str = "exit") -> str:
        """
        Generate a polite goodbye message using OpenAI based on the reason for ending the conversation
        
        Args:
            reason (str): The reason for ending the conversation ('exit', 'complete', or 'max_questions')
        """
        collected_data = self.memory.get_collected_data_summary()
        
        prompt = GOODBYE_USER_PROMPT_TEMPLATE.format(
            reason=EXIT_REASONS.get(reason, "the conversation is ending"),
            collected_data=collected_data
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": GOODBYE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature = 0.2 #todo change to take from enviorment
        )
        
        return response.choices[0].message.content.strip()
    
     

    def check_if_question_is_about_field(self, last_assistant_message, field_name=REQUIRED_FIELDS[-1]):
        """
        Checks if the agent's last message is still asking about a specific field.
    
        Args:
        last_assistant_message: The last message sent by the agent
        field_name: The field to check for (defaults to last required field)
    
        Returns:
        bool: True if the message is still asking about the specified field, False otherwise
        """
        prompt = FIELD_CHECK_USER_TEMPLATE.format(
            last_assistant_message = last_assistant_message,
            field_name = field_name
        )
        
        response = self.client.chat.completions.create(
            model = self.model,
            messages = [
                {"role": "system", "content": FIELD_CHECK_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature = self.strict_temperature,
            max_tokens = 5
        )

        answer = response.choices[0].message.content.strip().lower()
        return answer == "yes"


   
    