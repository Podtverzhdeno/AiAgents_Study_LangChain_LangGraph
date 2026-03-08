from http.client import responses

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

llm = ChatOllama(
    model = "qwen2.5:7b",
    temperature = 0
)

messages = [
    SystemMessage(content = "Ты - ассистент, который должен кратко отвечать на вопросы"),
    HumanMessage(content="Какая погода считается хорошей?")
]

response = llm.invoke(messages)
print(type(response))
print(response.content)
print(response.response_metadata)

# Многоходовой диалог — просто добавляем сообщения
messages.append(response) # добавляем ответ модели
messages.append(HumanMessage(content = "Что такое llm?"))

response2 = llm.invoke(messages)
print(response2.content)