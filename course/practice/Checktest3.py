from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

@tool
def get_weather(city: str) -> str:
    """Инструмент, позволяющий узнать погоду в городе"""
    data_weather = {
        "москва": "очень Солнечно",
        "санкт-петербург": "идет дождь",
        "париж": "очень пасмурно"
    }

    # Приводим город к нижнему регистру для поиска
    city_lower = city.lower()

    # Проверяем наличие города в словаре
    if city_lower in data_weather:
        return f"Погода в {city}: {data_weather[city_lower]}"
    else:
        return f"Не знаю, какая погода сейчас в {city}"

# Создаем checkpointer
checkpointer = InMemorySaver()

# Создаем модель (не забудьте установить API ключ, если нужно)
model = ChatOllama(
    model="qwen2.5:7b",
    temperature=0
)

# Создаем агента
agent = create_agent(
    model=model,
    tools=[get_weather],
    checkpointer=checkpointer,
    system_prompt="Ты - помощник для поиска погоды в городах"
)

# Вызываем агента
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Какая погода сейчас в Париже?"}]},
    config={"configurable": {"thread_id": "1"}}
)

# Выводим результат
print(result["messages"][-1].content)