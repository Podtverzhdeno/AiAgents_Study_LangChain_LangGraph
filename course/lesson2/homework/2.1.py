# Задание 1 — лёгкое
# Создайте цепочку с многоходовым диалогом без MessagesPlaceholder.
# Вручную составьте список из 4 сообщений (system + 2 хода диалога + новый human) и передайте в LLM.
# Убедитесь, что модель помнит контекст.

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model = "qwen2.5:7b",
    temperature = 0
)

messages = [
    SystemMessage(content = "Ты - ассистент, который кратко отвечает вопросы"),
    HumanMessage(content = "Расскажи про RAG"),
    AIMessage(content = "RAG полезен, когда мы хотим избавиться от галлюцинаций"),
    HumanMessage(content = "Насколько жарко в пустыне?"),
]

response = llm.invoke(messages)
print(response)