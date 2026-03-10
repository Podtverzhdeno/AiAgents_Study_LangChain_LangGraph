# Заставить LLM всегда использовать конкретный инструмент
llm_forced = llm.bind_tools(tools, tool_choice="calculate")

# Заставить использовать хоть какой-то инструмент
llm_any = llm.bind_tools(tools, tool_choice="any")

# Поведение по умолчанию — LLM сама решает
llm_auto = llm.bind_tools(tools, tool_choice="auto")


# Параллельный вызов инструментов

# Современные модели умеют вызывать несколько Tools за один раз
response = llm_with_tools.invoke(
    "Какая погода в Москве и в Сочи?"
)

print(len(response.tool_calls))  # 2 — оба вызова сразу!
for tc in response.tool_calls:
    print(tc["name"], tc["args"])
# get_weather {"city": "Москва"}
# get_weather {"city": "Сочи"}


# Обработка ошибок в Tools

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