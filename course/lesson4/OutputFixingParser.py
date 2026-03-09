from langchain.output_parsers import OutputFixingParser
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

class Result(BaseModel):
    value: int
    label: str

base_parser = PydanticOutputParser(pydantic_object=Result)

# Оборачиваем в OutputFixingParser
fixing_parser = OutputFixingParser.from_llm(
    parser=base_parser,
    llm=ChatOpenAI(model="gpt-4o-mini"),
)

# Если base_parser не справится — fixing_parser попросит LLM исправить ответ
# Автоматически, без вашего участия
chain = prompt | llm | fixing_parser