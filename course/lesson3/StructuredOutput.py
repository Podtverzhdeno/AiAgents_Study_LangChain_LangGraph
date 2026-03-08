from pydantic import BaseModel, Field
from typing import List
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model = "qwen2.5:7b",
    temperature = 0
)

class MovieReview(BaseModel):
    title:str = Field(description="Название фильма")
    rating:int = Field(ge=1, le=10, description="Оценка от 1 до 10")
    pros:List[str] = Field(description="Список достоинств")
    cons:List[str] = Field(description="Список недостатков")
    recommend:bool = Field(description="Рекомендуешь ли смотреть")

structured_llm = llm.with_structured_output(MovieReview)

result = structured_llm.invoke("Дай рецензию на фильм Inception (Начало)")

# Работаем с объектом напрямую
print(result.title)        # "Inception"
print(result.rating)       # 9
print(result.recommend)    # True
print(result.pros)         # ["Оригинальный сюжет", "Визуальные эффекты", ...]

# Валидация работает автоматически — rating не может быть 11