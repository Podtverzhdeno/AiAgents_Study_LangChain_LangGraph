# Полный цикл выполнения Tools
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage

llm = ChatOllama(model="qwen2.5:7b", temperature=0)

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
tools = [calculate, get_weather]
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