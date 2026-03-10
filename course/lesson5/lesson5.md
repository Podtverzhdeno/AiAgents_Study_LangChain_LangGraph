Урок 5: Tools — инструменты

Часть 1: Зачем нужны Tools?
LLM умеет только генерировать текст. Но что если нужно:

узнать актуальный курс валют
выполнить точные вычисления
сохранить данные в БД
сделать HTTP-запрос

Всё это LLM сама не может. Tools — это мост между LLM и реальным миром.
Без Tools:                        С Tools:
──────────                        ────────
"Сколько будет 1847 * 293?"       LLM видит инструмент calculator
→ LLM считает сама                → вызывает calculator(1847 * 293)
→ может ошибиться                 → получает точный результат 541171
→ отвечает пользователю

Часть 2: Как LLM работает с Tools
Важнейшая концепция: LLM не выполняет инструмент — она возвращает намерение.
┌─────────────────────────────────────────────────────────┐
│                    ЦИКЛ РАБОТЫ С TOOLS                  │
│                                                         │
│  1. Пользователь: "Сколько будет 23 * 47?"              │
│            │                                            │
│            ▼                                            │
│  2. LLM получает вопрос + описания инструментов         │
│     Решает: нужен calculator                            │
│     Возвращает: tool_call {name: "calc", args: {..}}    │
│            │                                            │
│            ▼                                            │
│  3. ВАШ КОД выполняет calculator(23 * 47) = 1081        │
│            │                                            │
│            ▼                                            │
│  4. Результат → обратно в LLM как ToolMessage           │
│            │                                            │
│            ▼                                            │
│  5. LLM формирует финальный ответ: "23 * 47 = 1081"     │
└─────────────────────────────────────────────────────────┘

Часть 3: Три способа создать Tool
Способ 1: декоратор @tool — быстро и просто
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
"""Возвращает текущую погоду в городе.

    Используй этот инструмент когда пользователь спрашивает о погоде
    в конкретном городе. Возвращает температуру и описание погоды.
    """
    # имитация API запроса
    weather_data = {
        "Москва":       "−5°C, снег",
        "Санкт-Петербург": "−2°C, облачно",
        "Сочи":         "+15°C, солнечно",
    }
    return weather_data.get(city, f"Данные для {city} недоступны")

# Tool — это тоже Runnable
print(get_weather.name)          # "get_weather"
print(get_weather.description)   # текст docstring
print(get_weather.args)          # {"city": {"type": "string"}}

# Вызов напрямую
print(get_weather.invoke({"city": "Москва"}))   # "−5°C, снег"
print(get_weather.invoke("Москва"))             # тоже работает
Способ 2: декоратор + Pydantic схема — для сложных входов
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional

class SearchInput(BaseModel):
query:       str            = Field(description="Поисковый запрос")
max_results: int            = Field(default=5, ge=1, le=20,
description="Количество результатов")
language:    Optional[str]  = Field(default="ru",
description="Язык результатов: ru, en")

@tool(args_schema=SearchInput)
def search_database(query: str, max_results: int = 5, language: str = "ru") -> list:
"""Поиск в корпоративной базе знаний компании.

    Используй когда нужно найти информацию о продуктах, политиках
    или внутренних процессах компании. НЕ используй для поиска
    в интернете или получения актуальных новостей.
    """
    # имитация поиска
    return [f"Результат {i} для '{query}'" for i in range(max_results)]

print(search_database.args)
# {
#   "query":       {"type": "string", "description": "Поисковый запрос"},
#   "max_results": {"type": "integer", ...},
#   "language":    {"type": "string", ...}
# }
Способ 3: класс BaseTool — максимальный контроль
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
import httpx

class WeatherInput(BaseModel):
city:    str
units:   str = Field(default="celsius", description="celsius или fahrenheit")

class WeatherTool(BaseTool):
name:        str = "get_weather"
description: str = """Получает реальную погоду через API.
Используй для получения актуальной погоды в любом городе мира."""
args_schema: Type[BaseModel] = WeatherInput

    # Можно добавлять свои поля
    api_key: str = ""

    def _run(self, city: str, units: str = "celsius") -> str:
        """Синхронное выполнение."""
        # здесь реальный API запрос
        return f"Погода в {city}: +20°C"  # упрощённо

    async def _arun(self, city: str, units: str = "celsius") -> str:
        """Асинхронное выполнение."""
        async with httpx.AsyncClient() as client:
            # реальный async запрос
            return f"Погода в {city}: +20°C"

weather_tool = WeatherTool(api_key="your-key")

Часть 4: Docstring — это промпт для LLM
Docstring — не документация для разработчика. Это инструкция для LLM когда и как использовать инструмент. От качества docstring зависит правильность вызова.
python# ❌ ПЛОХО — слишком размыто
@tool
def calculate(expression: str) -> float:
"""Calculates."""
return eval(expression)

# ❌ ПЛОХО — слишком длинно, LLM теряет суть
@tool
def calculate(expression: str) -> float:
"""Этот инструмент предназначен для выполнения различных
математических вычислений и операций с числами, включая
сложение, вычитание, умножение и деление..."""
return eval(expression)

# ✅ ХОРОШО — чётко, конкретно, указаны границы применения
@tool
def calculate(expression: str) -> float:
"""Вычисляет математическое выражение. Принимает строку вида '2+2', '15*7', '100/4'.
Используй для точных арифметических вычислений.
НЕ используй для текстовых операций или работы с датами."""
return eval(expression)
Правила хорошего docstring:

Одно чёткое предложение — что делает
Когда использовать
Когда НЕ использовать (если есть похожие инструменты)
Формат входных данных если неочевидно


Часть 5: Полный цикл выполнения Tools
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

@tool
def calculate(expression: str) -> float:
"""Вычисляет математическое выражение вида '2+2', '15*7'.
Используй для точных арифметических вычислений."""
return eval(expression)

@tool
def get_weather(city: str) -> str:
"""Возвращает погоду в городе. Используй когда спрашивают о погоде."""
return f"В {city} сейчас +20°C, солнечно"

# Регистрируем инструменты в модели
tools     = [calculate, get_weather]
tools_map = {t.name: t for t in tools}
llm_with_tools = llm.bind_tools(tools)

# Полный цикл
def run_with_tools(user_message: str) -> str:
messages = [HumanMessage(content=user_message)]

    while True:
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        # Нет tool_calls → LLM дала финальный ответ
        if not response.tool_calls:
            return response.content

        # Есть tool_calls → выполняем каждый
        for tool_call in response.tool_calls:
            print(f"  → Вызов: {tool_call['name']}({tool_call['args']})")

            tool_result = tools_map[tool_call["name"]].invoke(tool_call["args"])
            print(f"  ← Результат: {tool_result}")

            # Важно: tool_call_id связывает результат с вызовом
            messages.append(ToolMessage(
                content=str(tool_result),
                tool_call_id=tool_call["id"],
            ))

        # Продолжаем цикл — LLM смотрит на результаты

# Тестируем
print(run_with_tools("Сколько будет 1847 умножить на 293?"))
print(run_with_tools("Какая погода в Москве?"))
print(run_with_tools("Какая погода в Сочи и сколько будет 100 / 4?"))

Часть 6: Управление поведением Tools
Принудительный вызов конкретного инструмента
python# Заставить LLM всегда использовать конкретный инструмент
llm_forced = llm.bind_tools(tools, tool_choice="calculate")

# Заставить использовать хоть какой-то инструмент
llm_any = llm.bind_tools(tools, tool_choice="any")

# Поведение по умолчанию — LLM сама решает
llm_auto = llm.bind_tools(tools, tool_choice="auto")
Параллельный вызов инструментов
python# Современные модели умеют вызывать несколько Tools за один раз
response = llm_with_tools.invoke(
"Какая погода в Москве и в Сочи?"
)

print(len(response.tool_calls))  # 2 — оба вызова сразу!
for tc in response.tool_calls:
print(tc["name"], tc["args"])
# get_weather {"city": "Москва"}
# get_weather {"city": "Сочи"}
Обработка ошибок в Tools
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage

@tool
def divide(a: float, b: float) -> str:
"""Делит a на b. Используй для деления чисел."""
try:
if b == 0:
return "Ошибка: деление на ноль невозможно"
return str(a / b)
except Exception as e:
return f"Ошибка вычисления: {e}"

# Правило: Tool должен возвращать строку с описанием ошибки
# а не бросать исключение — LLM получит ошибку и сможет отреагировать

Часть 7: ToolMessage — правила заполнения
python# tool_call_id — обязательный! Связывает результат с вызовом
# Без него модель не поймёт какой результат к какому вызову относится

ToolMessage(
content=str(result),           # всегда строка
tool_call_id=tool_call["id"],  # берём из tool_call объекта
name=tool_call["name"],        # опционально, но хорошая практика
)

🏠 Домашнее задание
Задание 1 — лёгкое
Создайте три инструмента через @tool:

get_current_time() — возвращает текущее время
calculate(expression: str) — вычисляет выражение
reverse_string(text: str) — переворачивает строку

Напишите для каждого хороший docstring. Вызовите каждый напрямую через .invoke().

Задание 2 — среднее
Реализуйте полный цикл run_with_tools() из урока. Добавьте четвёртый инструмент — convert_currency(amount: float, from_currency: str, to_currency: str) с имитацией курсов. Протестируйте запрос который требует двух инструментов последовательно.

Задание 3 — сложное
Создайте мини-ассистента с инструментами:
pythontools = [
search_products,    # поиск товаров по названию → возвращает список
get_price,          # получить цену товара по id → возвращает float
add_to_cart,        # добавить товар в корзину → возвращает подтверждение
get_cart_total,     # получить сумму корзины → возвращает float
]
Все инструменты имитируют работу с данными (используйте dict как "БД"). Реализуйте полный цикл и протестируйте: "Найди ноутбук, узнай цену и добавь в корзину если дешевле 100000 рублей".

❓ Вопросы для самопроверки

Почему LLM не выполняет инструмент напрямую, а возвращает намерение?
Что будет если не вернуть ToolMessage после вызова инструмента?
Зачем нужен tool_call_id в ToolMessage?
Чем @tool с Pydantic схемой лучше обычного @tool?
Что произойдёт если Tool бросит исключение вместо того чтобы вернуть строку с ошибкой?
Почему tools_map = {t.name: t for t in tools} — обязательный шаг?
Что означает tool_choice="any" и когда это полезно?