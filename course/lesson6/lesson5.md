Урок 6: Память

Часть 1: Зачем нужна память?
LLM — stateless. Каждый вызов независим. Без памяти каждый запрос — как первый:
Без памяти:                        С памятью:
───────────                        ─────────
User: "Меня зовут Алексей"         User: "Меня зовут Алексей"
AI:   "Привет, Алексей!"           AI:   "Привет, Алексей!"
User: "Как меня зовут?"            User: "Как меня зовут?"
AI:   "Не знаю, вы не говорили"    AI:   "Тебя зовут Алексей"
Память в LangChain — это не магия. Это просто управление списком Messages который передаётся в LLM при каждом вызове.

Часть 2: Два типа памяти
Память
│
├── Short-term (краткосрочная)
│   └── История текущей сессии
│       Хранится в памяти процесса
│       Исчезает при перезапуске
│
└── Long-term (долгосрочная)
└── Факты между сессиями
Хранится в БД / файлах
Переживает перезапуск

Часть 3: Short-term память
Базовый подход — вручную
pythonfrom langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# История — просто список Messages
history = [
SystemMessage(content="Ты дружелюбный ассистент. Отвечай кратко.")
]

def chat(user_input: str) -> str:
# Добавляем сообщение пользователя
history.append(HumanMessage(content=user_input))

    # Передаём ВСЮ историю в LLM
    response = llm.invoke(history)

    # Сохраняем ответ
    history.append(response)

    return response.content

# Тестируем
print(chat("Меня зовут Алексей"))   # "Привет, Алексей!"
print(chat("Я люблю Python"))       # "Отлично! Python — отличный выбор"
print(chat("Что ты знаешь обо мне?"))
# "Тебя зовут Алексей и ты любишь Python"
RunnableWithMessageHistory — автоматизированный подход

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

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
chain_with_memory.invoke({"input": "Я люблю Python"},     config=cfg_user1)

# Диалог второго пользователя — полностью изолирован
chain_with_memory.invoke({"input": "Меня зовут Мария"},   config=cfg_user2)

# Проверяем изоляцию
r1 = chain_with_memory.invoke({"input": "Как меня зовут?"}, config=cfg_user1)
r2 = chain_with_memory.invoke({"input": "Как меня зовут?"}, config=cfg_user2)

print(r1)   # "Тебя зовут Алексей"
print(r2)   # "Тебя зовут Мария"

# Смотрим историю
print(store["user_1"].messages)   # все сообщения первого пользователя
```

---

## Часть 4: Проблема растущего контекста

У каждой LLM есть лимит токенов. Бесконечно накапливать историю нельзя:
```
Сообщение 1:   ~50 токенов
Сообщение 2:   ~80 токенов
...
Сообщение 50:  ~3000 токенов суммарно
Сообщение 100: ~6000 токенов  ← дорого и медленно
Сообщение 200: ~12000 токенов ← может превысить лимит модели
```

Три стратегии решения:
```
┌─────────────────────────────────────────────────────────┐
│              СТРАТЕГИИ УПРАВЛЕНИЯ КОНТЕКСТОМ            │
│                                                         │
│  1. trim_messages   — обрезать старые сообщения         │
│     [1,2,3,4,5] → keep last 3 → [3,4,5]                │
│     Просто. Теряем старый контекст.                     │
│                                                         │
│  2. Суммаризация    — сжать историю через LLM           │
│     [1,2,3,4,5] → summary → ["Краткое резюме", 4, 5]   │
│     Сохраняем суть. Дороже (доп. вызов LLM).            │
│                                                         │
│  3. Векторная память — хранить факты отдельно           │
│     Извлекать релевантные при каждом запросе.           │
│     Сложнее. Разберём в уроке про RAG.                  │
└─────────────────────────────────────────────────────────┘
trim_messages — обрезка истории

from langchain_core.messages import trim_messages, SystemMessage
from langchain_core.messages import HumanMessage, AIMessage

# Создаём триммер
trimmer = trim_messages(
max_tokens=1000,          # максимум токенов
strategy="last",          # оставить последние сообщения
token_counter=llm,        # использовать llm для подсчёта токенов
include_system=True,      # SystemMessage всегда сохраняем
allow_partial=False,      # не обрезать сообщение на середине
start_on="human",         # начинать с HumanMessage (не с AIMessage)
)

# Пример работы
messages = [
SystemMessage(content="Ты ассистент"),
HumanMessage(content="Сообщение 1"),
AIMessage(content="Ответ 1"),
HumanMessage(content="Сообщение 2"),
AIMessage(content="Ответ 2"),
HumanMessage(content="Сообщение 3"),  # последнее
]

trimmed = trimmer.invoke(messages)
# SystemMessage сохранён + последние N сообщений в лимите токенов

# Встраиваем в цепочку
from langchain_core.runnables import RunnablePassthrough

chain_with_trim = (
RunnablePassthrough.assign(
history=lambda x: trimmer.invoke(x["history"])
)
| prompt
| llm
| StrOutputParser()
)
Суммаризация истории

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, RemoveMessage

def summarize_history(messages: list, llm) -> list:
"""Суммаризирует старые сообщения, оставляет последние 4."""

    # Оставляем последние 4 сообщения как есть
    if len(messages) <= 6:
        return messages

    # Берём все кроме последних 4 на суммаризацию
    to_summarize = messages[:-4]
    recent       = messages[-4:]

    # Просим LLM сделать краткое резюме
    summary_prompt = [
        SystemMessage(content="Сделай краткое резюме диалога в 2-3 предложениях."),
        *to_summarize,
    ]
    summary = llm.invoke(summary_prompt)

    # Возвращаем: системное сообщение с резюме + последние сообщения
    return [
        SystemMessage(content=f"Краткое резюме предыдущего диалога: {summary.content}"),
        *recent,
    ]

# Используем в цепочке
def chat_with_summary(user_input: str, history: list) -> tuple[str, list]:
history.append(HumanMessage(content=user_input))

    # Суммаризируем если нужно
    history = summarize_history(history, llm)

    response = llm.invoke(history)
    history.append(response)

    return response.content, history

Часть 5: Long-term память
Хранит данные между сессиями — в файле или БД.
SQLite — простое персистентное хранилище

from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

def get_session_history(session_id: str):
return SQLChatMessageHistory(
session_id=session_id,
connection="sqlite:///chat_history.db",  # файл на диске
)

chain_with_memory = RunnableWithMessageHistory(
chain,
get_session_history,
input_messages_key="input",
history_messages_key="history",
)

cfg = {"configurable": {"session_id": "user_1"}}

# Первый запуск
chain_with_memory.invoke({"input": "Меня зовут Алексей"}, config=cfg)

# Перезапускаем программу... история сохранилась в БД
# Второй запуск — память восстановлена
result = chain_with_memory.invoke({"input": "Как меня зовут?"}, config=cfg)
print(result)   # "Тебя зовут Алексей" — даже после перезапуска!
Ручное управление long-term памятью

from langchain_core.messages import HumanMessage, AIMessage
import json

# Простая "долгосрочная память" — факты о пользователе
class SimpleMemory:
def __init__(self, filepath: str):
self.filepath = filepath
self.facts    = self._load()

    def _load(self) -> dict:
        try:
            with open(self.filepath) as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_fact(self, key: str, value: str):
        self.facts[key] = value
        with open(self.filepath, "w") as f:
            json.dump(self.facts, f, ensure_ascii=False)

    def get_context(self) -> str:
        if not self.facts:
            return ""
        facts_str = ", ".join(f"{k}: {v}" for k, v in self.facts.items())
        return f"Известные факты о пользователе: {facts_str}"

memory = SimpleMemory("user_memory.json")
memory.save_fact("name", "Алексей")
memory.save_fact("hobby", "Python")

# Используем факты в системном промпте
prompt = ChatPromptTemplate.from_messages([
("system", f"Ты ассистент. {memory.get_context()}"),
MessagesPlaceholder("history"),
("human", "{input}"),
])
```

---

## Часть 6: Полная картина — когда что использовать
```
Сценарий                              Решение
──────────────────────────────────    ──────────────────────────────
Простой чат-бот                   →  Ручной список Messages
Несколько пользователей           →  RunnableWithMessageHistory
+ session_id
Долгие диалоги (100+ сообщений)   →  trim_messages или суммаризация
Память между сессиями             →  SQLChatMessageHistory
Персонализация                    →  Long-term факты в системном промпте
Сложная агентная память           →  LangGraph (следующий уровень)

🏠 Домашнее задание
Задание 1 — лёгкое
Реализуйте чат через ручной список Messages:

Храните историю в списке
SystemMessage с любой персоной (повар, тренер, учитель)
Минимум 5 ходов диалога
После каждого ответа выводите количество сообщений в истории


Задание 2 — среднее
Реализуйте два изолированных диалога через RunnableWithMessageHistory:

session_id = "alice" и session_id = "bob"
Алиса говорит что любит кошек, Боб — что любит собак
В конце оба спрашивают "Какое животное я люблю?"
Докажите что ответы разные и сессии изолированы
Выведите историю обеих сессий


Задание 3 — сложное
Реализуйте чат с автоматической суммаризацией:

При накоплении более 6 сообщений — автосуммаризация старых
Последние 4 сообщения всегда остаются нетронутыми
Выводите в консоль когда происходит суммаризация и что получилось
Проведите диалог из 10+ ходов и убедитесь что контекст сохраняется


❓ Вопросы для самопроверки

Почему LLM stateless и что это означает на практике?
Зачем нужен session_id в RunnableWithMessageHistory?
В чём разница между trim_messages и суммаризацией? Когда каждый подход лучше?
Что произойдёт если передавать всю историю без ограничений в длинном диалоге?
Зачем include_system=True в trim_messages?
Чем InMemoryChatMessageHistory отличается от SQLChatMessageHistory?
Почему long-term память обычно хранят в системном промпте, а не в истории сообщений?