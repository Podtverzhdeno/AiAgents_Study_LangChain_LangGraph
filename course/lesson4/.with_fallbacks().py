from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama

prompt = ChatPromptTemplate.from_template("Ответь на вопрос: {question}")
parser = StrOutputParser()

# Основная модель — дорогая и умная
primary = prompt | ChatOllama(model="qwen211.3.55v") | parser  # Берем несуществующую модель

# Запасная — дешевле
fallback = prompt | ChatOllama(model="qwen2.5:7b") | parser

# Если primary упала — автоматически пробуем fallback
safe_chain = primary.with_fallbacks([fallback])

result = safe_chain.invoke({"question": "Что такое квантовая запутанность?"})

print(result)