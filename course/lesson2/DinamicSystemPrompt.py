from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model = "qwen2.5:7b",
    temperature = 0
)

# System prompt тоже может быть переменной
prompt = ChatPromptTemplate.from_messages([
    ("system", "{persona}"),
    ("human",  "{message}"),
])

personas = {
    "pirate":    "Отвечай как пират, используй 'Йо-хо-хо' и морскую тематику",
    "scientist": "Отвечай как учёный, используй научную терминологию и точные факты",
    "child":     "Отвечай как пятилетний ребёнок, очень просто и наивно",
}

chain = prompt | llm

for role, persona in personas.items():
    result = chain.invoke({"persona": persona, "message": "Что такое дождь?"})
    print(f"\n[{role}]: {result}")