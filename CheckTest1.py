from pyexpat.errors import messages
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import create_agent

@tool
def get_animal(animal: str) -> dict:
    """Инструмент для поиска вида животного"""
    if animal.lower() == "cat":
        return f"{animal} имеется в зоопарке"
    elif animal.lower() == "dog":
        return f"{animal} прямо сейчас на выставке"
    return f"{animal} у нас нет"

model = ChatOllama (
    model = ("qwen2.5:7b"),
    temperature = 0
)

agent = create_agent(
    model = model,
    tools = [get_animal],
    system_prompt = "Ты - помощник по поиску животных в организации"
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Обезьяна в организации находится?"}]}
)

print(result["messages"][-1].content)