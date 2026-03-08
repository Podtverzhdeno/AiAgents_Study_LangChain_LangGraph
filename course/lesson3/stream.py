from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model = "qwen2.5:7b",
    temperature = 0
)

prompt = ChatPromptTemplate.from_template("Напиши короткое эссе о {topic}")
chain = prompt | llm | StrOutputParser()

# Стриминг — пользователь видит текст сразу, не ждёт конца генерации
print("Генерация: ", end="")
for chunk in chain.stream({"topic": "квантовые компьютеры"}):
    print(chunk, end="", flush=True)
print()

# Async стриминг (для веб-приложений)
import asyncio

async def stream_async():
    async for chunk in chain.astream({"topic": "искусственный интеллект"}):
        print(chunk, end="", flush=True)

asyncio.run(stream_async())
