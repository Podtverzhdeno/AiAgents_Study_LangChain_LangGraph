# Задание 2 — среднее
# Создайте промпт с MessagesPlaceholder и .partial():
#
# Базовый промпт с переменными {role}, {history}, {input}
# Сделайте два специализированных промпта через .partial(): один для роли "юрист", второй для "врач"
# Соберите цепочку и проверьте что оба работают с разным контекстом в history


from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

llm = ChatOllama(
    model = "qwen2.5:7b",
    temperature = 0
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Ты - эксперт в области {domain}"),
    MessagesPlaceholder("history"),
    ("human", "{input}")
])

lawyer_prompt = prompt.partial(domain="юриспруденции")
doctor_prompt = prompt.partial(domain="медицины")

lawyer_chain = lawyer_prompt | llm
doctor_chain = doctor_prompt | llm

response1 = lawyer_chain.invoke({
    "history": [
        HumanMessage(content="Здравствуйте, у меня вопрос по договору"),
        AIMessage(content="Конечно, задавайте ваш вопрос")
    ],
    "input": "Что такое исковая давность?"
})
print("Юрист:", response1.content)

response2 = doctor_chain.invoke({
    "history": [
        HumanMessage(content="Доктор, у меня болит голова"),
        AIMessage(content="Как давно это началось?")
    ],
    "input": "Что мне принять?"
})
print("Врач:", response2.content)
print("-" * 50)

response3 = lawyer_chain.invoke({
    "history": [],
    "input": "Что такое контракт?"
})
print("Юрист (без истории):", response3.content)