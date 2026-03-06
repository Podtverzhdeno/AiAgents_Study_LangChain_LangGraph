from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class MyState(TypedDict):
    messages: list[str]
    counter: int

graph = StateGraph(MyState)

def node_a(state: MyState) -> dict:
    message_a = state.get("messages", []) + ["Начинаем"]
    return {
        "messages": message_a,
        "counter": state["counter"] + 1,
    }

def node_b(state: MyState) -> dict:
    message_b = state.get("messages") + ["Умножим на 8"]
    return {
        "messages": message_b,
        "counter": state["counter"] * 8,
    }

graph.add_node("A", node_a)
graph.add_node("B", node_b)

graph.add_edge(START, "A")
graph.add_edge("A","B")
graph.add_edge("B",END)

graph_compiled = graph.compile()

result = graph_compiled.invoke({"messages": ["Начнем"], "counter": 0})
print(result)