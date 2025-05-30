import json
import os
from typing import Dict, Any
from enum import Enum
from text_prompts import REQUIRED_FIELDS


# Enum for tracking field status
class FieldStatus(Enum):
    EMPTY = ""
    FILLED = "filled"
    SKIPPED = "skipped"
   
class MemoryManager:
    
     
    def __init__(self, memory_path="patient_data.json"):
        self.memory_path = memory_path
        self.required_fields = REQUIRED_FIELDS
        self.fields_status = {field: FieldStatus.EMPTY.value for field in self.required_fields}
        self.load()


    def load(self):
        """Load patient data from file"""
        try:
            with open(self.memory_path, "r") as f:
                self.fields_data = json.load(f)
        except FileNotFoundError:
            self.fields_data = {}

    def save(self):
        """Save patient data to file"""
        with open(self.memory_path, "w") as f:
            json.dump(self.fields_data, f, indent=2)

    def get_state(self) -> Dict[str, Any]:
        """Get the current patient data"""
        return self.fields_data

    def get_state_for_prompt(self) -> Dict[str, Any]:
        """Get only the required fields for the prompt"""
        return {k: v for k, v in self.fields_data.items() if k in self.required_fields}

    def update_state(self, key: str, value: Any) -> None:
        """Update a specific field in the patient data"""
        self.fields_data[key] = value
        if value == 'skipped':
            self.fields_status[key] = FieldStatus.SKIPPED.value
        else:
            self.fields_status[key] = FieldStatus.FILLED.value
        self.save()

    
    def is_last_filed_skipped(self) -> bool:
        """Check if the last field is skipped"""
        last_field = self.required_fields[-1]
        return self.fields_status.get(last_field) == FieldStatus.SKIPPED.value
    
    def is_complete(self) -> bool:
        """
        Check if all required fields have been filled or skipped (i.e., their status is not EMPTY).
        Returns True if all fields are either FILLED or SKIPPED.
        """
        return all(
            self.fields_status.get(field) != FieldStatus.EMPTY.value
            for field in self.required_fields
        )
    def clear_memory(self) -> None:
        """Clear the patient data"""
        self.fields_data = {}
        self.fields_status = {field: FieldStatus.EMPTY.value for field in self.required_fields}
        self.save()

    def print_memory_state(self) -> None:
        """Print the current patient data"""
        print("\nPatient Information:")
        print("-" * 50)
        for field in self.required_fields:
            value = self.fields_data.get(field, "Not provided")
            print(f"{field}: {value}")
        print("-" * 50) 

    def get_collected_data_summary(self) -> str:
        """Get a formatted summary of the collected patient data"""
        collected_data = []
        for field in self.required_fields:
            if value := self.fields_data.get(field):
                collected_data.append(f"{field}: {value}")
        
        if collected_data:
            return "Collected information:\n" + "\n".join(collected_data)
        return "No information has been collected yet." 
    
