💬 Урок 2: Messages и PromptTemplates

Часть 1: Зачем Messages, а не просто строки?
Когда вы общаетесь с GPT в интерфейсе — вы видите чат. Под капотом это список сообщений с ролями. Разные провайдеры форматируют это по-разному:
OpenAI API:                    Anthropic API:
{                              {
"role": "user",                "role": "user",
"content": "Привет"            "content": [{"type": "text", "text": "Привет"}]
}                              }
Проблема: если писать под конкретный формат — код ломается при смене провайдера.
Решение LangChain: объекты Messages. Вы работаете с ними, LangChain сам конвертирует в нужный формат API.
Ваш код          LangChain             API
─────────        ─────────             ─────────────────────
HumanMessage  →  конвертация  →  {"role": "user", ...}     (OpenAI)
AIMessage     →  конвертация  →  {"role": "assistant", ...} (Anthropic)

Часть 2: Типы сообщений
Message (базовый класс)
│
├── SystemMessage     — инструкция для модели (роль: system)
├── HumanMessage      — сообщение пользователя (роль: user)
├── AIMessage         — ответ модели (роль: assistant)
├── ToolMessage       — результат выполнения инструмента
└── AIMessageChunk    — один чанк при стриминге
pythonfrom langchain_core.messages import (
SystemMessage,
HumanMessage,
AIMessage,
ToolMessage,
)

# Создание
system = SystemMessage(content="Ты опытный Python-разработчик")
human  = HumanMessage(content="Что такое декоратор?")
ai     = AIMessage(content="Декоратор — это функция, которая...")

# Базовые атрибуты
print(human.content)          # "Что такое декоратор?"
print(human.type)             # "human"

# AIMessage может содержать tool_calls (разберём в уроке про Tools)
print(ai.tool_calls)          # [] — пока пусто

Часть 3: Как Messages текут через LLM
pythonfrom langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Передаём список Messages напрямую
messages = [
SystemMessage(content="Отвечай только на русском, очень кратко"),
HumanMessage(content="What is Python?"),
]

response = llm.invoke(messages)
print(type(response))         # AIMessage
print(response.content)       # "Python — язык программирования"
print(response.response_metadata)  # токены, модель, причина остановки

# Многоходовой диалог — просто добавляем сообщения
messages.append(response)     # добавляем ответ модели
messages.append(HumanMessage(content="А что такое декоратор?"))

response2 = llm.invoke(messages)
print(response2.content)      # модель помнит контекст разговора
Важно: LLM не имеет памяти сама по себе. "Память" — это просто передача всей истории сообщений при каждом вызове.

Часть 4: PromptTemplate — фабрика сообщений
PromptTemplate — это шаблон, который принимает dict с переменными и возвращает готовые Messages. Это тоже Runnable.
4.1 Базовые способы создания
pythonfrom langchain_core.prompts import ChatPromptTemplate

# Способ 1: from_messages — самый гибкий и частый
prompt = ChatPromptTemplate.from_messages([
("system", "Ты эксперт по {domain}"),
("human",  "Объясни {concept} простыми словами"),
])

# Вызываем как Runnable
result = prompt.invoke({
"domain":  "машинное обучение",
"concept": "градиентный спуск",
})

print(type(result))            # ChatPromptValue
print(result.to_messages())
# [
#   SystemMessage(content="Ты эксперт по машинное обучение"),
#   HumanMessage(content="Объясни градиентный спуск простыми словами"),
# ]

# Способ 2: from_template — только один HumanMessage
from langchain_core.prompts import ChatPromptTemplate

simple = ChatPromptTemplate.from_template("Переведи на английский: {text}")
# Эквивалентно:
# ChatPromptTemplate.from_messages([("human", "Переведи на английский: {text}")])
4.2 MessagesPlaceholder — слот для истории
pythonfrom langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
("system", "Ты ассистент"),
MessagesPlaceholder("history"),   # сюда подставится список Messages
("human", "{input}"),
])

# Подставляем историю
result = prompt.invoke({
"history": [
HumanMessage(content="Меня зовут Алексей"),
AIMessage(content="Приятно познакомиться, Алексей!"),
],
"input": "Как меня зовут?",
})

print(result.to_messages())
# [
#   SystemMessage("Ты ассистент"),
#   HumanMessage("Меня зовут Алексей"),
#   AIMessage("Приятно познакомиться, Алексей!"),
#   HumanMessage("Как меня зовут?"),
# ]
4.3 partial() — зафиксировать часть переменных
python# Фиксируем domain заранее — получаем специализированный промпт
base_prompt = ChatPromptTemplate.from_messages([
("system", "Ты эксперт по {domain}"),
("human", "{question}"),
])

python_prompt = base_prompt.partial(domain="Python")
ml_prompt     = base_prompt.partial(domain="машинному обучению")

# Теперь нужно передать только question
python_prompt.invoke({"question": "Что такое GIL?"})
ml_prompt.invoke({"question": "Что такое overfitting?"})
```

---

## Часть 5: Полная картина — типы в цепочке
```
invoke({"domain": "Python", "question": "Что такое GIL?"})
│
▼  dict
ChatPromptTemplate
│
▼  ChatPromptValue (список Messages)
│  [SystemMessage(...), HumanMessage(...)]
ChatOpenAI
│
▼  AIMessage
│  AIMessage(content="GIL — это...")
StrOutputParser
│
▼  str
"GIL — это..."
python# Смотрим типы вживую
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

llm    = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_messages([
("system", "Ты эксперт по {domain}"),
("human",  "{question}"),
])
parser = StrOutputParser()

# Смотрим каждый шаг
inp    = {"domain": "Python", "question": "Что такое GIL?"}
step1  = prompt.invoke(inp)
step2  = llm.invoke(step1)
step3  = parser.invoke(step2)

print(f"Шаг 1: {type(step1).__name__}")   # ChatPromptValue
print(f"Шаг 2: {type(step2).__name__}")   # AIMessage
print(f"Шаг 3: {type(step3).__name__}")   # str

# Цепочкой:
chain = prompt | llm | parser
print(chain.invoke(inp))                   # "GIL — это..."

Часть 6: Практические паттерны
Few-shot — примеры прямо в промпте
pythonprompt = ChatPromptTemplate.from_messages([
("system", "Определяй тональность текста: positive/negative/neutral"),
("human",  "Этот фильм потрясающий!"),
("ai",     "positive"),
("human",  "Ужасный сервис, никогда не вернусь"),
("ai",     "negative"),
("human",  "Сегодня среда"),
("ai",     "neutral"),
("human",  "{text}"),   # реальный вопрос
])

chain = prompt | llm | StrOutputParser()
print(chain.invoke({"text": "Книга была неплохой"}))  # "neutral" или "positive"
Динамический system prompt
pythonfrom langchain_core.prompts import ChatPromptTemplate

# System prompt тоже может быть переменной
prompt = ChatPromptTemplate.from_messages([
("system", "{persona}"),
("human",  "{message}"),
])

personas = {
"pirate":    "Отвечай как пират, используй 'Йо-хо-хо' и морскую тематику",
"scientist": "Отвечай как учёный, используй научную терминологию и точные факты",
"child":     "Отвечай как пятилетний ребёнок, очень просто и наивно",
}

chain = prompt | llm | StrOutputParser()

for role, persona in personas.items():
result = chain.invoke({"persona": persona, "message": "Что такое дождь?"})
print(f"\n[{role}]: {result}")

🏠 Домашнее задание
Задание 1 — лёгкое
Создайте цепочку с многоходовым диалогом без MessagesPlaceholder. Вручную составьте список из 4 сообщений (system + 2 хода диалога + новый human) и передайте в LLM. Убедитесь что модель помнит контекст.

Задание 2 — среднее
Создайте промпт с MessagesPlaceholder и .partial():

Базовый промпт с переменными {role}, {history}, {input}
Сделайте два специализированных промпта через .partial(): один для роли "юрист", второй для "врач"
Соберите цепочку и проверьте что оба работают с разным контекстом в history


Задание 3 — сложное
Реализуйте few-shot классификатор срочности задач:

Промпт с 3-4 примерами (human/ai парами) для классификации на: low / medium / high / critical
Цепочка возвращает только метку без пояснений
Проверьте на 5 разных входах


❓ Вопросы для самопроверки

Зачем LangChain использует объекты Messages вместо обычных строк?
Чем MessagesPlaceholder отличается от обычной переменной {variable} в промпте?
Что возвращает prompt.invoke()? Какой тип?
Что такое partial() и когда он полезен?
Если в промпте есть MessagesPlaceholder("history") и вы передадите пустой список [] — что произойдёт?
В чём разница между ("ai", "текст") и AIMessage(content="текст") при создании промпта?
Почему LLM "помнит" контекст диалога если у неё нет памяти?