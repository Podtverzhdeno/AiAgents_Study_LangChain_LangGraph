from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from typing import TypedDict, Annotated

llm = ChatOllama(model="qwen2.5:7b")

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# Узел 1 — анализирует вопрос, добавляет системный контекст
def analyze(state: AgentState) -> dict:
    last_message = state["messages"][-1].content
    system = SystemMessage(content="Ты полезный ассистент. Отвечай кратко и по делу.")
    return {"messages": [system]}

# Узел 2 — генерирует ответ через LLM
def generate(state: AgentState) -> dict:
    result = llm.invoke(state["messages"])
    return {"messages": [result]}

graph = StateGraph(AgentState)
graph.add_node("analyze", analyze)
graph.add_node("generate", generate)

graph.add_edge(START, "analyze")
graph.add_edge("analyze", "generate")
graph.add_edge("generate", END)

graph_compiled = graph.compile()

result = graph_compiled.invoke({
    "messages": [HumanMessage(content="Что такое LangGraph?")]
})

print(result["messages"][-1].content)