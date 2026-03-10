# ToolMessage — правила заполнения
# tool_call_id — обязательный! Связывает результат с вызовом
# Без него модель не поймёт какой результат к какому вызову относится

ToolMessage(
    content=str(result),           # всегда строка
    tool_call_id=tool_call["id"],  # берём из tool_call объекта
    name=tool_call["name"],        # опционально, но хорошая практика
)