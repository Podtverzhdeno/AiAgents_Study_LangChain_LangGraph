from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

class Analysis(BaseModel):
    summary: str
    score: int = Field(ge=1, le=10)
    tags: List[str]

llm = ChatOllama(model="qwen2.5:7b", temperature=0)
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