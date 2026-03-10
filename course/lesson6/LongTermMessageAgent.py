from dataclasses import dataclass
from langchain_core.tools import tool
from langchain.tools import ToolRuntime
from langchain.agents import create_agent
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

@dataclass
class Context:
    user_id: str   # передаётся при каждом вызове агента

@tool
def get_user_info(runtime: ToolRuntime[Context]) -> str:
    """Получает информацию о текущем пользователе.
    Используй когда нужно узнать имя, предпочтения или историю пользователя."""
    user_info = runtime.store.get(("users",), runtime.context.user_id)
    if user_info:
        return str(user_info.value)
    return "Информация о пользователе не найдена"

agent = create_agent(
    model="gpt-4o-mini",
    tools=[get_user_info],
    store=store,
    context_schema=Context,
)

# Записываем данные заранее
store.put(("users",), "user_42", {
    "name":        "Алексей",
    "preferences": ["Python", "ML"],
    "style":       "краткие ответы",
})

# Запускаем агента
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Что ты знаешь обо мне?"}]},
    context=Context(user_id="user_42"),
)
print(result["messages"][-1].content)
# "Тебя зовут Алексей, ты любишь Python и ML, предпочитаешь краткие ответы"