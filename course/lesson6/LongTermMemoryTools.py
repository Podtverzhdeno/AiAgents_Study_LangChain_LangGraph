from typing_extensions import TypedDict

class UserInfo(TypedDict):
    name:        str
    preferences: list[str]
    style:       str

@tool
def save_user_info(user_info: UserInfo, runtime: ToolRuntime[Context]) -> str:
    """Сохраняет информацию о пользователе для будущих сессий.
    Используй когда пользователь сообщает своё имя, предпочтения или стиль общения."""
    runtime.store.put(
        ("users",),
        runtime.context.user_id,
        user_info,
    )
    return f"Информация сохранена: {user_info}"

@tool
def add_memory(content: str, memory_type: str, runtime: ToolRuntime[Context]) -> str:
    """Добавляет факт в долгосрочную память о пользователе.
    memory_type: preference / work / personal / other"""
    import time
    key = f"memory_{int(time.time())}"   # уникальный ключ по времени
    runtime.store.put(
        ("memories", runtime.context.user_id),
        key,
        {"content": content, "type": memory_type},
    )
    return f"Запомнил: {content}"

agent = create_agent(
    model="gpt-4o-mini",
    tools=[get_user_info, save_user_info, add_memory],
    store=store,
    context_schema=Context,
)

# Агент сам решает когда сохранять
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Меня зовут Мария, я люблю кошек"}]},
    context=Context(user_id="user_99"),
)

# Проверяем что сохранилось
saved = store.get(("users",), "user_99")
print(saved.value)   # {"name": "Мария", "preferences": [...], ...}