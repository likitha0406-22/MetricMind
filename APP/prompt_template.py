from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0.7
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful AI assistant."),
        ("user", "{question}")
    ]
)

chain = prompt | llm

response = chain.invoke(
    {
        "question": "Explain RAG architecture"
    }
)

print(response.content)