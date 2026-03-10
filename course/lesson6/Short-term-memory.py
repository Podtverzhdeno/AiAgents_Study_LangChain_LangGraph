from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

llm = ChatOllama(model = "qwen2.5:7b")

history = [
    SystemMessage(content="Ты дружелюбный ассистент. Отвечай кратко")
]

def chat(user_input: str) -> str:
    history.append(HumanMessage(content=user_input))

    response = llm.invoke(history)

    history.append(response)

    return response.content

print(chat("Меня зовут Алексей")) # "Привет, Алексей!"
print(chat("Я люблю Python")) # "Отлично! Python — отличный выбор"
print(chat("Что ты знаешь обо мне?")) # "Тебя зовут Алексей и ты любишь Python"