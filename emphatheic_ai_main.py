from memory_manager import MemoryManager
from empathetic_agent import EmpatheticAgent
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    max_questions = int(os.getenv("MAX_QUESTIONS", "20"))  # Default to 20 if not set
    
    memory = MemoryManager()
    memory.clear_memory()
    agent = EmpatheticAgent(memory)

    print("Empathetic chat (type 'exit' to quit)\n")
                  
    user_input = ""
    question_count = 0
    check_if_to_finish = False

    try:
        while question_count < max_questions:
            response = agent.ask(user_input = user_input)
             
            if memory.is_complete():
                if not memory.is_last_filed_skipped():
                    break
                else:
                    #handle the special case where the agent is still trying 
                    #to extract data from the user about the last field
                    if not agent.check_if_question_is_about_field(response):
                        break

            print(f"\nAgent: {response}\n")
            user_input = input("You: ")
            if user_input.lower() == "exit":
                # Generate goodbye message for user exit
                break
          
            question_count += 1
            
        goodbye = agent.generate_goodbye_message("complete")
        print(f"\nAgent: {goodbye}\n")
            
    finally:
        memory.print_memory_state()

