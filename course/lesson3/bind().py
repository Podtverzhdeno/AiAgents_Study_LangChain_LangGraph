# Создать специализированную версию модели
json_llm = llm.bind(
    response_format={"type": "json_object"}  # OpenAI JSON mode
)

# Зафиксировать стоп-слова
focused_llm = llm.bind(stop=["###", "---"])  # остановится при этих токенах

# Передать инструменты (разберём детально в уроке про Tools)
llm_with_tools = llm.bind_tools([search_tool, calc_tool])

# Всё это — Runnable, встраивается в цепочку как обычно
chain = prompt | json_llm | parser