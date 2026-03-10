from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from typing import TypedDict, Annotated
from langchain.tools import tool
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage

llm = ChatOllama(model = "qwen2.5:7b")

class MyState(TypedDict):
    messages: Annotated[list, add_messages]


graph = StateGraph(MyState)

def tool_answer(state: MyState) -> dict:
    """Инструмент для анализа погоды"""
    return {"messages": [AIMessage(content="Погода ясная")]}

def analyze(state: MyState) -> dict:
    last_message = state["messages"][-1]
    return {"messages": [AIMessage(content = "погода хорошая")]}

def route(state: MyState) -> dict:
    last_message = state["messages"][-1]
    if "погода" in last_message.content:
        return "tool"
    return "llm"

def llm_answer(state: MyState) -> dict:
    result = llm.invoke(state["messages"])
    return {"messages": [result]}



graph.add_node("Analyze", analyze)
graph.add_node("Llm_answer", llm_answer)
graph.add_node("Tool_answer", tool_answer)

graph.add_edge(START, "Analyze")
graph.add_conditional_edges(
    "Analyze",
    route,
    {
        "tool": "Tool_answer",
        "llm": "Llm_answer"

    }
)

graph.add_edge("Llm_answer", END)
graph.add_edge("Tool_answer", END)

graph_compiled = graph.compile()

result = graph_compiled.invoke({
    "messages": [HumanMessage(content="")] #всегда гарантируется "погода ясная", поэтому нет смысла в HumanMessage
})

print(result["messages"][-1].content)