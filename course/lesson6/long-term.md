Long-term память: современный подход через LangGraph Store

Часть 1: Архитектура хранилища
LangGraph Store — это key-value хранилище с поддержкой:
├── Namespace  — папка для группировки данных
├── Key        — уникальный ключ внутри namespace
├── Value      — любой JSON-совместимый dict
└── Search     — векторный поиск + фильтрация
Аналогия с файловой системой:

Store
├── ("users",)                    ← namespace (папка)
│   ├── "user_123" → {name: ...}  ← key → value
│   └── "user_456" → {name: ...}
├── ("users", "preferences")      ← вложенный namespace
│   ├── "user_123" → {theme: ...}
│   └── "user_456" → {theme: ...}
└── ("sessions",)
└── "session_1" → {summary: ...}

Часть 2: Базовый CRUD
pythonfrom langgraph.store.memory import InMemoryStore

store = InMemoryStore()

# ── CREATE / UPDATE ───────────────────────────────────────
store.put(
("users",),       # namespace — кортеж строк
"user_123",       # key
{                 # value — любой dict
"name":     "Алексей",
"language": "Python",
"age":      28,
}
)

# ── READ ──────────────────────────────────────────────────
item = store.get(("users",), "user_123")

print(item.value)      # {"name": "Алексей", "language": "Python", "age": 28}
print(item.key)        # "user_123"
print(item.namespace)  # ("users",)

# Если ключ не существует — возвращает None
missing = store.get(("users",), "unknown")
print(missing)         # None

# ── DELETE ────────────────────────────────────────────────
store.delete(("users",), "user_123")

# ── LIST — все ключи в namespace ─────────────────────────
items = store.search(("users",))
for item in items:
print(item.key, item.value)

Часть 3: Поиск — фильтрация и векторный поиск
pythonfrom langgraph.store.memory import InMemoryStore

# Для векторного поиска нужна функция эмбеддингов
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

def embed(texts: list[str]) -> list[list[float]]:
return embeddings.embed_documents(texts)

# Store с поддержкой векторного поиска
store = InMemoryStore(index={
"embed": embed,
"dims":  1536,   # размерность text-embedding-3-small
})

# Заполняем данными
store.put(("memories", "user_123"), "fact_1", {
"content": "Пользователь любит Python и машинное обучение",
"type":    "preference"
})
store.put(("memories", "user_123"), "fact_2", {
"content": "Пользователь работает в стартапе",
"type":    "work"
})
store.put(("memories", "user_123"), "fact_3", {
"content": "Пользователь предпочитает короткие ответы",
"type":    "preference"
})

# ── Фильтрация по полю ────────────────────────────────────
prefs = store.search(
("memories", "user_123"),
filter={"type": "preference"}   # только preferences
)
for p in prefs:
print(p.value["content"])
# "Пользователь любит Python и машинное обучение"
# "Пользователь предпочитает короткие ответы"

# ── Векторный поиск по смыслу ─────────────────────────────
results = store.search(
("memories", "user_123"),
query="Что пользователь любит делать?",   # семантический поиск
limit=2,                                   # топ-2 результата
)
for r in results:
print(r.value["content"], "| score:", r.score)

Часть 4: Интеграция с агентом
Чтение памяти в Tool
pythonfrom dataclasses import dataclass
from langchain_core.tools import tool
from langchain.tools import ToolRuntime
from langchain.agents import create_agent
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

@dataclass
class Context:
user_id: str   # передаётся при каждом вызове агента

@tool
def get_user_info(runtime: ToolRuntime[Context]) -> str:
"""Получает информацию о текущем пользователе.
Используй когда нужно узнать имя, предпочтения или историю пользователя."""
user_info = runtime.store.get(("users",), runtime.context.user_id)
if user_info:
return str(user_info.value)
return "Информация о пользователе не найдена"

agent = create_agent(
model="gpt-4o-mini",
tools=[get_user_info],
store=store,
context_schema=Context,
)

# Записываем данные заранее
store.put(("users",), "user_42", {
"name":        "Алексей",
"preferences": ["Python", "ML"],
"style":       "краткие ответы",
})

# Запускаем агента
result = agent.invoke(
{"messages": [{"role": "user", "content": "Что ты знаешь обо мне?"}]},
context=Context(user_id="user_42"),
)
print(result["messages"][-1].content)
# "Тебя зовут Алексей, ты любишь Python и ML, предпочитаешь краткие ответы"
Запись памяти в Tool
pythonfrom typing_extensions import TypedDict

class UserInfo(TypedDict):
name:        str
preferences: list[str]
style:       str

@tool
def save_user_info(user_info: UserInfo, runtime: ToolRuntime[Context]) -> str:
"""Сохраняет информацию о пользователе для будущих сессий.
Используй когда пользователь сообщает своё имя, предпочтения или стиль общения."""
runtime.store.put(
("users",),
runtime.context.user_id,
user_info,
)
return f"Информация сохранена: {user_info}"

@tool
def add_memory(content: str, memory_type: str, runtime: ToolRuntime[Context]) -> str:
"""Добавляет факт в долгосрочную память о пользователе.
memory_type: preference / work / personal / other"""
import time
key = f"memory_{int(time.time())}"   # уникальный ключ по времени
runtime.store.put(
("memories", runtime.context.user_id),
key,
{"content": content, "type": memory_type},
)
return f"Запомнил: {content}"

agent = create_agent(
model="gpt-4o-mini",
tools=[get_user_info, save_user_info, add_memory],
store=store,
context_schema=Context,
)

# Агент сам решает когда сохранять
result = agent.invoke(
{"messages": [{"role": "user", "content": "Меня зовут Мария, я люблю кошек"}]},
context=Context(user_id="user_99"),
)

# Проверяем что сохранилось
saved = store.get(("users",), "user_99")
print(saved.value)   # {"name": "Мария", "preferences": [...], ...}

Часть 5: Production — замена InMemoryStore на БД
InMemoryStore — только для разработки. В продакшене данные теряются при перезапуске.
python# ── PostgreSQL ────────────────────────────────────────────
from langgraph.store.postgres import PostgresStore

store = PostgresStore.from_conn_string(
"postgresql://user:password@localhost/dbname"
)

# ── Redis ─────────────────────────────────────────────────
from langgraph.store.redis import RedisStore

store = RedisStore.from_conn_string("redis://localhost:6379")

# Интерфейс одинаковый для всех — код агента не меняется!
store.put(("users",), "user_123", {"name": "Алексей"})
item = store.get(("users",), "user_123")

Часть 6: Паттерны организации namespace
python# ── По пользователю ───────────────────────────────────────
("users",)                        # базовые данные
("users", "preferences")          # предпочтения
("users", "history")              # история действий

# ── По пользователю + контексту ───────────────────────────
(user_id, "memories")             # личные воспоминания
(user_id, "work")                 # рабочий контекст
(user_id, "chitchat")             # неформальное общение

# ── По организации ────────────────────────────────────────
("org", org_id, "knowledge")      # база знаний организации
("org", org_id, "users")          # пользователи организации

# Правило: namespace = (кто_владеет, что_хранит)

Часть 7: Полная картина — short-term + long-term вместе
pythonfrom langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
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
```

---

## Итоговая карта памяти
```
Тип памяти        Хранилище              Переживает перезапуск?
──────────────    ─────────────────────  ──────────────────────
Short-term        InMemoryChatHistory    ❌ Нет
Short-term        SQLChatMessageHistory  ✅ Да
Long-term         InMemoryStore          ❌ Нет (только dev)
Long-term         PostgresStore          ✅ Да
Long-term         RedisStore             ✅ Да