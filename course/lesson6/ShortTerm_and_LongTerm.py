# Полная картина — short-term + long-term вместе

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langgraph.store.memory import InMemoryStore
from langchain_openai import ChatOpenAI

llm   = ChatOpenAI(model="gpt-4o-mini", temperature=0)
store = InMemoryStore()

def build_chain(user_id: str):
    """Строит цепочку с учётом long-term памяти пользователя."""

    # Достаём долгосрочный контекст
    user_data = store.get(("users",), user_id)
    user_context = ""
    if user_data:
        user_context = f"Что известно о пользователе: {user_data.value}"

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"Ты ассистент. {user_context}"),
        MessagesPlaceholder("history"),   # short-term
        ("human", "{input}"),
    ])

    return prompt | llm

# Short-term хранилище сессий
sessions = {}
def get_history(session_id):
    if session_id not in sessions:
        sessions[session_id] = InMemoryChatMessageHistory()
    return sessions[session_id]

# Записываем long-term данные
store.put(("users",), "alex_42", {
    "name":  "Алексей",
    "style": "предпочитает короткие ответы",
})

# Строим цепочку с памятью
chain = RunnableWithMessageHistory(
    build_chain("alex_42"),
    get_history,
    input_messages_key="input",
    history_messages_key="history",
)

cfg = {"configurable": {"session_id": "session_1"}}
print(chain.invoke({"input": "Привет! Как меня зовут?"}, config=cfg))
# "Привет, Алексей! Ты предпочитаешь короткие ответы."
