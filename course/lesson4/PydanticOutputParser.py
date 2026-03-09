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