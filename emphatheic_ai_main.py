from memory_manager import MemoryManager
from empathetic_agent import EmpatheticAgent


if __name__ == "__main__":
    memory = MemoryManager()
    memory.clear_memory()
    agent = EmpatheticAgent(memory)

    print("Empathetic chat (type 'exit' to quit)\n")
                  
    user_input = ""
    while not memory.is_complete():

        response = agent.ask(user_input=user_input)
        print(f"\nAgent: {response}\n")
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

