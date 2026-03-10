# Задание 1 — лёгкое
# Создайте цепочку с CommaSeparatedListOutputParser.
# Промпт: "Назови 5 {category}".
# Проверьте на трёх категориях: фрукты, языки программирования, страны. Выведите результат как список Python.
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import CommaSeparatedListOutputParser

parser = CommaSeparatedListOutputParser()

prompt = ChatPromptTemplate.from_messages([
    ("human", "Назови 5 {category}.{format_instructions}")
])

model = ChatOllama(model="qwen2.5:7b")

chain = prompt | model | parser

categories = ["фрукты", "языки программирования", "страны"]

for category in categories:
    result = chain.invoke({
        "category": category,
        "format_instructions": parser.get_format_instructions()
    })
    print(f"{category}: {result}")