# Agent_project

# 🤖 Empathetic Agent

An empathetic AI assistant designed to interact gently and supportively with women recently diagnosed with breast cancer. The agent's primary goal is to collect essential information while maintaining a warm, respectful tone (without initiating general conversation or casual dialogue).

---

# 👉 How to Run

You can run this project directly on your machine or easily through Google Colab.

### Google Colab
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ayana123/Agent_project/blob/main/Empathetic_Agent_Colab.ipynb)

1. Open the Colab link.
2. Update the OpenAI key directly in the notebook.
3. Run the cells and start interacting with the Empathetic Agent!

### Local Run

1. Clone the repository.
2. Update the OpenAI key in a `.env` 
3. Install the required packages, use the requirements.txt
4. Run the main Python file:

```bash
python emphatheic_ai_main.py
```

---
## 📚 Project Overview

The Empathetic Agent is focused on gathering the following five pieces of information:
1. **First Name**
2. **Age**
3. **Type of Breast Cancer Diagnosis**
4. **Current Treatment Details**
5. **Support System (Family, Friends, Community)**

The conversation is designed to:
- Ask **one question at a time**.
- **Gently persist** if the user does not respond, rephrasing the question.
- **Move on** if the user doesn't respond after several attempts.
- **Strictly avoid** casual conversation or open-ended discussions outside the required questions.

## implementation Overview:

The agent is deigned to use the power of llm and ai to understand text rather than parse the answer itself
thogh it call to openAI in order to extract or understand the user answers 


# 🛠️ Implementation Details

The Empathetic Agent is designed with a strong reliance on the capabilities of Large Language Models (LLMs) to drive the interaction and decision-making process. Instead of hardcoding the conversation flow, the LLM is empowered to manage key aspects of the dialogue based on its advanced understanding of language and context.

### Key Design Principles

- **LLM-Driven Conversation Flow**:
  - The agent uses the LLM's reasoning capabilities to decide when to persist on a question and when to move on to the next one.
  - There is no strict if/else branching logic dictating the sequence; instead, the LLM naturally determines the conversation progression based on user responses and its understanding of the situation.

- **Dynamic Information Extraction**:
  - The LLM is tasked with parsing user input and extracting the relevant fields (such as name, age, diagnosis) using carefully crafted prompts.
  - Instead of traditional rule based parsing, the agent leverages the LLM’s superior language understanding to handle ambiguous, incomplete, or nuanced answers.

- **Contextual Awareness through Conversation History**:
  - When generating the next question, the LLM uses the full conversation history to decide whether to continue insisting on a missing answer, to rephrase, or to move on to the next topic.
  - By reviewing the interaction history, the LLM also better understands the user's communication style and emotional state, leading to a more sensitive and human-like interaction.
  - **Performance vs. Cost Trade-off**: For better performance, using the conversation history is preferred as it helps maintain rich context. However, there is also an option to disable history usage to save on token usage. When history is disabled, the agent instead provides the LLM with a summary of collected data so far.
- **Prompts used**:
  - Different prompts are used depending on the task:
    - **Question Generation**: Asking empathetic, context-aware questions.
    - **Information Extraction**: Parsing structured information from user responses.
    - **Conversation Completion**: Deciding if the required information has been collected.
    - **Goodbye Message Generation**: Crafting a professional and warm conversation closure.



