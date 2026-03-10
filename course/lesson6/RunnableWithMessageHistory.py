from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama

llm = ChatOllama(model = "qwen2.5:7b")

prompt = ChatPromptTemplate.from_messages([
    ("system", "Ты ассистент. Отвечай кратко."),
    MessagesPlaceholder("history"),   # сюда автоматически подставится история
    ("human", "{input}"),
])

chain = prompt | llm | StrOutputParser()

# Хранилище сессий: session_id → история
store = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# Оборачиваем цепочку — теперь она сама читает и пишет историю
chain_with_memory = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# session_id изолирует разные диалоги
cfg_user1 = {"configurable": {"session_id": "user_1"}}
cfg_user2 = {"configurable": {"session_id": "user_2"}}

# Диалог первого пользователя
chain_with_memory.invoke({"input": "Меня зовут Алексей"}, config=cfg_user1)
chain_with_memory.invoke({"input": "Я люблю Python"}, config=cfg_user1)

# Диалог второго пользователя — полностью изолирован
chain_with_memory.invoke({"input": "Меня зовут Мария"},   config=cfg_user2)

# Проверяем изоляцию
r1 = chain_with_memory.invoke({"input": "Как меня зовут?"}, config=cfg_user1)
r2 = chain_with_memory.invoke({"input": "Как меня зовут?"}, config=cfg_user2)

print(r1)   # "Тебя зовут Алексей"
print(r2)   # "Тебя зовут Мария"

# Смотрим историю
print(store["user_1"].messages)   # все сообщения первого пользователя