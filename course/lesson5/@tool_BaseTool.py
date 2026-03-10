# Способ 3: класс BaseTool — максимальный контроль
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
import httpx

class WeatherInput(BaseModel):
    city: str
    units: str = Field(default="celsius", description="celsius или fahrenheit")

class WeatherTool(BaseTool):
    name: str = "get_weather"
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