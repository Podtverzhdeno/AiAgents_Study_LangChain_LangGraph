from langchain.agents import create_agent
from langchain_ollama import ChatOllama


def get_weather(city: str) -> str:
    """Which weather in sity"""
    return f"in {city} weather is good"

model = ChatOllama(
    model = "qwen2.5:7b",
    temperature=0.5
)

agent = create_agent(
    model = model,
    tools = [get_weather],
    system_prompt="тебе надо помочь узнать погоду"
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "какая погода в Париже?"}]}
)
print(result["messages"][-1].content)
