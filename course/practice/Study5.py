from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Annotated
from langgraph.graph.message import add_messages
from datetime import datetime
import json

# Кастомный редусер для уникальных документов
def unique_documents(existing: List[str], new: List[str]) -> List[str]:
    """Добавляет только уникальные документы"""
    combined = existing + new
    # Убираем дубликаты, сохраняя порядок
    seen = set()
    unique = []
    for doc in combined:
        if doc not in seen:
            seen.add(doc)
            unique.append(doc)
    return unique

# Редусер для подсчета статистики
def aggregate_stats(existing: dict, new: dict) -> dict:
    """Суммирует статистику"""
    result = existing.copy()
    for key, value in new.items():
        result[key] = result.get(key, 0) + value
    return result

class DocumentState(TypedDict):
    # Автоматическое накопление сообщений
    messages: Annotated[List[str], add_messages]
    # Уникальные документы
    documents: Annotated[List[str], unique_documents]
    # Статистика обработки
    stats: Annotated[dict, aggregate_stats]
    # Метаданные (простое поле)
    current_user: str
    processed_at: str

# Узлы обработки
def receive_documents(state: DocumentState):
    """Получает новые документы"""
    new_docs = [
        "report_2024.pdf",
        "invoice_123.pdf",
        "report_2024.pdf",  # Дубликат
        "contract_final.docx"
    ]

    return {
        "documents": new_docs,
        "stats": {"received": len(new_docs)},
        "processed_at": datetime.now().isoformat()
    }

def validate_documents(state: DocumentState):
    """Валидирует документы"""
    valid_docs = [d for d in state["documents"] if d.endswith(('.pdf', '.docx'))]

    return {
        "messages": [f"Валидация: получено {len(state['documents'])} документов"],
        "documents": valid_docs,  # Сохраняем только валидные
        "stats": {
            "valid": len(valid_docs),
            "invalid": len(state['documents']) - len(valid_docs)
        }
    }

def process_documents(state: DocumentState):
    """Обрабатывает документы"""
    return {
        "messages": [f"Обработано {len(state['documents'])} документов"],
        "stats": {"processed": len(state['documents'])}
    }

# Сборка графа
builder = StateGraph(DocumentState)
builder.add_node("receive", receive_documents)
builder.add_node("validate", validate_documents)
builder.add_node("process", process_documents)

builder.add_edge(START, "receive")
builder.add_edge("receive", "validate")
builder.add_edge("validate", "process")
builder.add_edge("process", END)

graph = builder.compile()

# Запуск
result = graph.invoke({
    "messages": [],
    "documents": [],
    "stats": {},
    "current_user": "Иван",
    "processed_at": ""
})

print("=== ИТОГОВОЕ СОСТОЯНИЕ ===")
print(f"Сообщения: {result['messages']}")
print(f"Документы: {result['documents']}")
print(f"Статистика: {result['stats']}")
print(f"Пользователь: {result['current_user']}")