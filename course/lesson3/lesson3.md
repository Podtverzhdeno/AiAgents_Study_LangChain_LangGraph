Урок 3: Chat Models

Часть 1: Chat Model vs LLM — в чём разница
В LangChain есть два интерфейса для работы с языковыми моделями:
BaseLLM (устаревший)          BaseChatModel (современный)
────────────────────          ───────────────────────────
вход:  строка                 вход:  список Messages
выход: строка                 выход: AIMessage
примеры: text-davinci-003     примеры: GPT-4, Claude, Gemini
Сегодня все актуальные модели — это ChatModel. BaseLLM остался для обратной совместимости. Работаем только с BaseChatModel.

Часть 2: Создание и параметры
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
model="gpt-4o-mini",   # какая модель
temperature=0,          # 0 = детерминированно, 1 = креативно, макс ~2
max_tokens=500,         # максимум токенов в ответе
timeout=30,             # секунд до таймаута запроса
max_retries=2,          # повторов при сбое сети
)
```

### Temperature — самый важный параметр
```
temperature=0.0   → всегда один и тот же ответ (факты, код, классификация)
temperature=0.3   → чуть вариативнее (аналитика, резюме)
temperature=0.7   → баланс (общение, объяснения)
temperature=1.0+  → творческий режим (стихи, истории, brainstorm)

Правило: если нужна воспроизводимость → 0, если нужно разнообразие → выше
Смена провайдера — только импорт меняется
python# OpenAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini")

# Anthropic
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")

# Google
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# Остальной код — без изменений
chain = prompt | llm | parser
Это и есть сила абстракции LangChain.

Часть 3: Метаданные ответа
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
response = llm.invoke([HumanMessage(content="Привет!")])

# Сам ответ
print(response.content)           # "Привет! Чем могу помочь?"

# Метаданные — токены, модель, причина остановки
print(response.response_metadata)
# {
#   "token_usage": {
#     "completion_tokens": 9,
#     "prompt_tokens": 10,
#     "total_tokens": 19
#   },
#   "model_name": "gpt-4o-mini",
#   "finish_reason": "stop"    ← "stop"=норма, "length"=обрезало по max_tokens
# }

# Удобный доступ к токенам
print(response.usage_metadata)
# {"input_tokens": 10, "output_tokens": 9, "total_tokens": 19}
finish_reason важен для отладки: если видите "length" — модель обрезала ответ, увеличьте max_tokens.

Часть 4: Structured Output — главная фича
Это способ получить от LLM не текст, а готовый Python-объект с валидацией.
Почему не просто парсить текст?
python# Хрупко — LLM может ответить по-разному:
response = llm.invoke("Верни JSON с именем и возрастом")
# "Вот JSON: {"name": "Алексей", "age": 25}"  ← лишний текст
# "{"name": "Алексей", "age": "25"}"           ← age как строка
# "Имя: Алексей, Возраст: 25"                  ← вообще не JSON
python# Надёжно — with_structured_output:
# всегда получаете валидный объект нужного типа
Базовый пример
from pydantic import BaseModel, Field
from typing import List
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

class MovieReview(BaseModel):
title:      str              = Field(description="Название фильма")
rating:     int              = Field(ge=1, le=10, description="Оценка от 1 до 10")
pros:       List[str]        = Field(description="Список достоинств")
cons:       List[str]        = Field(description="Список недостатков")
recommend:  bool             = Field(description="Рекомендуешь ли смотреть")

structured_llm = llm.with_structured_output(MovieReview)

result = structured_llm.invoke("Дай рецензию на фильм Inception (Начало)")

# Работаем с объектом напрямую
print(result.title)        # "Inception"
print(result.rating)       # 9
print(result.recommend)    # True
print(result.pros)         # ["Оригинальный сюжет", "Визуальные эффекты", ...]

# Валидация работает автоматически — rating не может быть 11
Вложенные структуры
from pydantic import BaseModel, Field
from typing import List, Optional

class Person(BaseModel):
name: str
age:  int

class ContactInfo(BaseModel):
email:   Optional[str] = None
phone:   Optional[str] = None

class Employee(BaseModel):
person:   Person
contact:  ContactInfo
skills:   List[str]   = Field(description="Список навыков")
level:    str         = Field(description="junior/middle/senior")

structured_llm = llm.with_structured_output(Employee)

result = structured_llm.invoke(
"Алексей Иванов, 28 лет, senior Python разработчик. "
"Email: alex@example.com. Навыки: Python, FastAPI, PostgreSQL"
)

print(result.person.name)     # "Алексей Иванов"
print(result.person.age)      # 28
print(result.level)           # "senior"
print(result.skills)          # ["Python", "FastAPI", "PostgreSQL"]
print(result.contact.email)   # "alex@example.com"
include_raw — получить и объект и сырой ответ
python# Иногда нужно видеть и распарсенный объект, и оригинальный AIMessage
structured_llm = llm.with_structured_output(MovieReview, include_raw=True)

result = structured_llm.invoke("Рецензия на Матрицу")

print(result["parsed"])        # MovieReview объект
print(result["raw"])           # оригинальный AIMessage
print(result["parsing_error"]) # None если всё ок, иначе ошибка

Часть 5: .bind() — зафиксировать параметры модели
python# Создать специализированную версию модели
json_llm = llm.bind(
response_format={"type": "json_object"}  # OpenAI JSON mode
)

# Зафиксировать стоп-слова
focused_llm = llm.bind(stop=["###", "---"])  # остановится при этих токенах

# Передать инструменты (разберём детально в уроке про Tools)
llm_with_tools = llm.bind_tools([search_tool, calc_tool])

# Всё это — Runnable, встраивается в цепочку как обычно
chain = prompt | json_llm | parser

Часть 6: Стриминг — получаем токены по мере генерации
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm    = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
prompt = ChatPromptTemplate.from_template("Напиши короткое эссе о {topic}")
chain  = prompt | llm | StrOutputParser()

# Стриминг — пользователь видит текст сразу, не ждёт конца генерации
print("Генерация: ", end="")
for chunk in chain.stream({"topic": "квантовые компьютеры"}):
print(chunk, end="", flush=True)
print()

# Async стриминг (для веб-приложений)
import asyncio

async def stream_async():
async for chunk in chain.astream({"topic": "искусственный интеллект"}):
print(chunk, end="", flush=True)

asyncio.run(stream_async())
```

---

## Часть 7: Как работает with_structured_output под капотом
```
Провайдер поддерживает           Провайдер НЕ поддерживает
function calling?                function calling?
│                                │
▼ ДА                             ▼ НЕТ
Использует нативный              Добавляет в промпт инструкции
function calling API             вернуть JSON нужного формата
(надёжно, быстро)                (менее надёжно)
│                                │
└──────────────┬─────────────────┘
▼
Парсит ответ в Pydantic-объект
Валидирует поля
Возвращает объект
Поэтому with_structured_output надёжнее чем парсить текст вручную — провайдеры типа OpenAI и Anthropic гарантируют формат на уровне API.

🏠 Домашнее задание
Задание 1 — лёгкое
Создайте две цепочки с одним промптом но разными temperature:

temperature=0 — запустите 3 раза, проверьте одинаковые ли ответы
temperature=1.2 — запустите 3 раза, проверьте разные ли ответы

Промпт: "Придумай одно случайное русское имя"

Задание 2 — среднее
Создайте structured_output для анализа вакансии:
pythonclass JobAnalysis(BaseModel):
position:        str        # название должности
required_skills: List[str]  # обязательные навыки
nice_to_have:    List[str]  # желательные навыки
experience_years: int       # лет опыта
is_remote:       bool       # удалённая ли работа
seniority:       str        # junior/middle/senior/lead
Протестируйте на реальном тексте вакансии (возьмите любую с hh.ru).

Задание 3 — сложное
Постройте цепочку с двумя structured_output последовательно:

Первый LLM: принимает текст новости → возвращает:

pythonclass NewsAnalysis(BaseModel):
topic:     str        # тема новости
sentiment: str        # positive/negative/neutral
key_facts: List[str]  # 3 ключевых факта

Второй LLM: принимает NewsAnalysis → генерирует заголовок и твит:

pythonclass NewsOutput(BaseModel):
headline: str   # заголовок до 10 слов
tweet:    str   # твит до 280 символов
Соедините в одну цепочку str → NewsAnalysis → NewsOutput.

❓ Вопросы для самопроверки

В чём разница между BaseLLM и BaseChatModel? Какой использовать?

Что означает finish_reason: "length" в метаданных ответа?

Как with_structured_output работает под капотом у провайдеров без function calling?

Зачем нужен include_raw=True?

Если temperature=0 — гарантирован ли абсолютно одинаковый ответ при каждом вызове?

Чем llm.bind() отличается от создания нового ChatOpenAI(...) с другими параметрами?

Почему стриминг важен для пользовательского опыта? В каких случаях он не нужен?