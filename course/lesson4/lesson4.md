Урок 4: Output Parsers + обработка ошибок

Часть 1: Зачем Output Parsers?
LLM всегда возвращает текст. Но вашему коду нужны данные:
LLM ответила:                    Вам нужно:
─────────────                    ──────────
"Результат: 42"              →   42  (int)
"- яблоко\n- груша\n- слива" →   ["яблоко", "груша", "слива"]
"{"score": 8, "ok": true}"   →   {"score": 8, "ok": True}
Output Parser — это последний шаг цепочки, который превращает AIMessage в нужный тип.
prompt | llm | [Output Parser]
↑
AIMessage → ваш тип

Часть 2: Все основные парсеры
StrOutputParser — базовый, самый частый
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()

# Просто извлекает .content из AIMessage
result = parser.invoke(AIMessage(content="Привет!"))
print(result)         # "Привет!"
print(type(result))   # str

# В цепочке:
chain = prompt | llm | StrOutputParser()
JsonOutputParser — парсит JSON из ответа
from langchain_core.output_parsers import JsonOutputParser

parser = JsonOutputParser()

# Умеет извлечь JSON даже если вокруг есть текст
result = parser.invoke(AIMessage(content='Вот результат: {"score": 8, "ok": true}'))
print(result)         # {"score": 8, "ok": True}
print(type(result))   # dict

# Поддерживает стриминг — dict собирается по мере прихода токенов
chain = prompt | llm | JsonOutputParser()
for chunk in chain.stream({"input": "..."}):
print(chunk)  # dict достраивается постепенно
PydanticOutputParser — JSON + валидация схемы
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

class Recipe(BaseModel):
name:        str
ingredients: List[str]
time_min:    int = Field(description="Время приготовления в минутах")

parser = PydanticOutputParser(pydantic_object=Recipe)

# Ключевая фича: генерирует инструкции для промпта
print(parser.get_format_instructions())
# "The output should be formatted as a JSON instance that conforms to..."

# Используем инструкции в промпте
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
("system", "Ты кулинарный ассистент. {format_instructions}"),
("human", "Дай рецепт: {dish}"),
]).partial(format_instructions=parser.get_format_instructions())

chain = prompt | llm | parser
result = chain.invoke({"dish": "борщ"})

print(type(result))          # Recipe (Pydantic объект)
print(result.name)           # "Борщ"
print(result.time_min)       # 90
print(result.ingredients)    # ["свёкла", "капуста", ...]
CommaSeparatedListOutputParser
from langchain_core.output_parsers import CommaSeparatedListOutputParser

parser = CommaSeparatedListOutputParser()

result = parser.invoke(AIMessage(content="яблоко, груша, слива, банан"))
print(result)   # ["яблоко", "груша", "слива", "банан"]

# Тоже генерирует инструкции
print(parser.get_format_instructions())
# "Your response should be a list of comma separated values..."
XMLOutputParser — для структурированных данных
from langchain_core.output_parsers import XMLOutputParser

parser = XMLOutputParser(tags=["person", "name", "age", "city"])

result = parser.invoke(AIMessage(content="""
<person>
<name>Алексей</name>
<age>28</age>
<city>Москва</city>
</person>
"""))

print(result)
# {"person": [{"name": "Алексей"}, {"age": "28"}, {"city": "Москва"}]}
```

---

## Часть 3: Сравнение подходов
```
Способ                      Надёжность   Когда использовать
──────────────────────────  ───────────  ──────────────────────────────
StrOutputParser             ████████░░   Текст пользователю, простые случаи
JsonOutputParser            ██████░░░░   Быстро, без схемы, стриминг dict
PydanticOutputParser        ████████░░   Нужна валидация, известна схема
with_structured_output      ██████████   Всегда предпочтительнее парсеров
(нативный function calling)
```

**Главное правило:** если провайдер поддерживает `with_structured_output` — используйте его. Парсеры нужны когда хотите стримить частичный результат или работаете со старыми провайдерами.

---

## Часть 4: Обработка ошибок

### Типы ошибок в LangChain
```
Ошибки LangChain
│
├── Сетевые / API
│   ├── RateLimitError      — превышен лимит запросов
│   ├── AuthenticationError — неверный API ключ
│   └── APITimeoutError     — таймаут запроса
│
├── Парсинга
│   ├── OutputParserException — не смогли распарсить ответ LLM
│   └── ValidationError       — Pydantic не прошёл валидацию
│
└── Логические
└── LLM вернула не то — нет исключения, но данные неверные
.with_retry() — повтор при сбое
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm   = ChatOpenAI(model="gpt-4o-mini")
chain = ChatPromptTemplate.from_template("{input}") | llm | StrOutputParser()

# Базовый retry
resilient_chain = chain.with_retry(
stop_after_attempt=3,        # максимум попыток
wait_exponential_jitter=True # экспоненциальный backoff + случайность
)

# Retry только на конкретные ошибки
from openai import RateLimitError, APITimeoutError

selective_chain = chain.with_retry(
stop_after_attempt=3,
retry_if_exception_type=(RateLimitError, APITimeoutError),
# другие ошибки (AuthenticationError) — не повторять
)

result = resilient_chain.invoke({"input": "Привет"})
.with_fallbacks() — запасной план
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template("Ответь на вопрос: {question}")
parser = StrOutputParser()

# Основная модель — дорогая и умная
primary = prompt | ChatOpenAI(model="gpt-4o") | parser

# Запасная — дешевле
fallback = prompt | ChatOpenAI(model="gpt-4o-mini") | parser

# Если primary упала — автоматически пробуем fallback
safe_chain = primary.with_fallbacks([fallback])

result = safe_chain.invoke({"question": "Что такое квантовая запутанность?"})
try/except — явная обработка
from langchain_core.exceptions import OutputParserException
from pydantic import ValidationError

def safe_invoke(chain, input_data):
try:
return chain.invoke(input_data)

    except OutputParserException as e:
        # LLM ответила, но не в нужном формате
        print(f"Ошибка парсинга: {e}")
        return None

    except ValidationError as e:
        # Pydantic не прошёл валидацию
        print(f"Ошибка валидации: {e}")
        return None

    except Exception as e:
        # Всё остальное (сеть, API)
        print(f"Неизвестная ошибка: {e}")
        raise  # пробрасываем дальше

result = safe_invoke(chain, {"input": "тест"})
if result is None:
print("Используем значение по умолчанию")
Комбинируем retry + fallback + try/except
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

class Analysis(BaseModel):
summary:  str
score:    int   = Field(ge=1, le=10)
tags:     List[str]

llm    = ChatOpenAI(model="gpt-4o-mini", temperature=0)
parser = PydanticOutputParser(pydantic_object=Analysis)
prompt = ChatPromptTemplate.from_messages([
("system", "Анализируй текст. {format_instructions}"),
("human", "{text}"),
]).partial(format_instructions=parser.get_format_instructions())

# Основная цепочка с retry
primary = (prompt | llm | parser).with_retry(stop_after_attempt=2)

# Запасная — более простая модель
fallback_parser = PydanticOutputParser(pydantic_object=Analysis)
fallback = prompt | ChatOpenAI(model="gpt-4o-mini") | fallback_parser

# Собираем надёжную цепочку
robust_chain = primary.with_fallbacks([fallback])

# Запускаем с обработкой
def analyze(text: str) -> Analysis | None:
try:
return robust_chain.invoke({"text": text})
except Exception as e:
print(f"Все попытки исчерпаны: {e}")
return None

result = analyze("Python — отличный язык для ML и веб-разработки")
if result:
print(f"Оценка: {result.score}/10")
print(f"Теги: {result.tags}")

Часть 5: OutputFixingParser — авторемонт ошибок парсинга
Если LLM вернула невалидный JSON — можно попросить другую LLM его починить:
from langchain.output_parsers import OutputFixingParser
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

class Result(BaseModel):
value: int
label: str

base_parser = PydanticOutputParser(pydantic_object=Result)

# Оборачиваем в OutputFixingParser
fixing_parser = OutputFixingParser.from_llm(
parser=base_parser,
llm=ChatOpenAI(model="gpt-4o-mini"),
)

# Если base_parser не справится — fixing_parser попросит LLM исправить ответ
# Автоматически, без вашего участия
chain = prompt | llm | fixing_parser

🏠 Домашнее задание
Задание 1 — лёгкое
Создайте цепочку с CommaSeparatedListOutputParser. Промпт: "Назови 5 {category}". Проверьте на трёх категориях: фрукты, языки программирования, страны. Выведите результат как список Python.

Задание 2 — среднее
Создайте PydanticOutputParser для анализа книги:
pythonclass BookAnalysis(BaseModel):
title:       str
author:      str
genre:       str
themes:      List[str]   # основные темы
difficulty:  str         # easy/medium/hard
rating:      int         = Field(ge=1, le=10)
Используйте get_format_instructions() в промпте. Протестируйте на 2-3 книгах.

Задание 3 — сложное
Постройте надёжную цепочку с тремя уровнями защиты:

.with_retry(stop_after_attempt=3) — на случай сетевых сбоев
.with_fallbacks([fallback_chain]) — запасная цепочка с другой моделью
try/except с разными обработчиками для OutputParserException и общего Exception

Оберните всё в функцию safe_analyze(text: str) -> BookAnalysis | None и продемонстрируйте работу.

❓ Вопросы для самопроверки

В чём ключевое отличие JsonOutputParser от PydanticOutputParser?

Зачем нужен get_format_instructions()? Что будет если его не использовать?

Почему with_structured_output надёжнее чем PydanticOutputParser?

Что делает with_retry() при wait_exponential_jitter=True?

Чем with_fallbacks() отличается от with_retry()? Когда использовать каждый?

В каком порядке правильно комбинировать retry и fallback и почему?

Когда использовать OutputFixingParser? Есть ли у него минусы?