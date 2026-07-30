from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# Load Local LLM
llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0.7
)

# Prompt for multi-step reasoning
prompt = ChatPromptTemplate.from_template("""
You are an intelligent AI assistant.

Solve the user's problem using these steps:

Step 1: Understand the problem.
Step 2: Identify important information.
Step 3: Think about the solution.
Step 4: Explain your reasoning.
Step 5: Give the final answer.

Question:
{question}
""")

chain = prompt | llm

question = input("Ask a question: ")

response = chain.invoke(
    {
        "question": question
    }
)

print("\nAnswer:\n")
print(response.content)