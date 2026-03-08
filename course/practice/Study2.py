from langchain.agents.structured_output import ToolStrategy
from langchain_ollama import ChatOllama
from langchain.tools import tool
from langchain.agents import create_agent
from pydantic import BaseModel  # ИСПРАВЛЕНО: добавил импорт

# ИСПРАВЛЕНО: добавил импорт BaseModel
class WeatherResponse(BaseModel):
    city: str
    temperature: str
    condition: str

# ИСПРАВЛЕНО: синтаксис параметра функции
@tool
def get_weather(city: str) -> str:  # Было: def get_weather(str: city) -> str:
    """инструмент, чтобы узнать погоду"""
    weather_data = {
        "москва": {"temperature": "38", "condition": "Солнечно"},  # ИСПРАВЛЕНО: ключи в нижнем регистре
        "санкт-петербург": {"temperature": "38", "condition": "Пасмурно"},
        # Убрал "Другие города/страны" из словаря, т.к. это не конкретный город
    }

    city_lower = city.lower()
    if city_lower in weather_data:
        data = weather_data[city_lower]
        return f"{data['temperature']}|{data['condition']}"
    else:
        return f"в {city} очень тепло"

model = ChatOllama(
    model="qwen2.5:7b",  # ИСПРАВЛЕНО: убрал лишние пробелы
    temperature=0.1,
)

# ИСПРАВЛЕНО: bind_tools вызываем отдельно, а не в цепочке
model_with_tools = model.bind_tools([get_weather])

agent = create_agent(
    model=model_with_tools,  # Используем модель с привязанными инструментами
    tools=[get_weather],      # ДОБАВЛЕНО: tools должны быть переданы в create_agent
    system_prompt="Ты - помощник, который должен узнавать погоду",
    response_format = ToolStrategy(WeatherResponse)
)

result = agent.invoke({"messages": [{"role": "user", "content": "Какая погода в Амстердаме?"}]})

# ИСПРАВЛЕНО: выводим content сообщения, а не весь объект
print(result["messages"][-1].content)