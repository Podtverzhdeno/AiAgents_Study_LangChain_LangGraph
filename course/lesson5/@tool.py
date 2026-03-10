# Способ 1: декоратор @tool — быстро и просто
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