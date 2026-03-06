from langchain.agents.middleware import ModelResponse, wrap_model_call
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_ollama import ChatOllama


@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"

@tool
def get_weather(location: str) -> str:
    """Get weather information for a location."""
    return f"Weather in {location}: Sunny, 72°F"

basic_model = ChatOllama(
    model="qwen2.5:7b",
    temperature=0.3,
    max_tokens=100
)

advanced_model = ChatOllama(
    model="qwen2.5:7b",  # Пока используем ту же модель, но можно указать другую
    temperature=0.7,
    max_tokens=500
)

@wrap_model_call
def dynamic_model_selection(request: ModelResponse, handler) -> ModelResponse:
    """Dynamic model selection."""
    last_message = request.state["messages"][-1].content

    is_complex = (
        len(last_message) >50 or
            "почему" in last_message.lower() or
            "объясни" in last_message.lower() or
            "сделай"in last_message.lower()
    )


    selected_model = advanced_model if is_complex else basic_model
    print(f"выбрана модель {"Сложная" if is_complex else "Простая"}")

    return handler(request.override(model = selected_model))

agent = create_agent(
    model = basic_model,
    tools = [search, get_weather],
    middleware= [dynamic_model_selection]
)

result = agent.invoke({"messages": [{"role": "user", "content": "Объясни мне, какая погода сейчас в пустыне?"}]})
print(result['messages'][-1].content)