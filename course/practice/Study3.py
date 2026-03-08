from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import asyncio
from langchain.messages import SystemMessage, HumanMessage

model = ChatOllama(
    model = "qwen2.5:7b",
    temperature=0.7
)
system_prompt = SystemMessage(
    """Ты- помощник-инженер, который придумывает новые самолеты"""
)

messages = [
    system_prompt,
    HumanMessage("Какой самолет самый быстрый?")
]

result = model.invoke(messages)

print(result["messages"][-1])