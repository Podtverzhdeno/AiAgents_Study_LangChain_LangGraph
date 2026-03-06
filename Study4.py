from http.cookiejar import cut_port_re

from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# 1. Определяем состояние (что будет храниться в графе)

class MyState(TypedDict):
    messages: list[str]
    counter: int

graph = StateGraph(MyState)

def node_a(state: MyState) -> dict:
    return {"counter": state["counter"] + 1}

def node_b(state: MyState) -> dict:
    current_messages = state.get("messages", [])
    new_messages = current_messages + ["Умножил на 5"]
    return {"counter": state["counter"] * 5, "messages": new_messages}

graph.add_node("A",node_a)
graph.add_node("B",node_b)

graph.add_edge(START,"A")
graph.add_edge("A","B")
graph.add_edge("B", END)

graph_compiled = graph.compile()

result = graph_compiled.invoke({
    "messages": ["Начинаем"],
    "counter": 2
})

print(result)