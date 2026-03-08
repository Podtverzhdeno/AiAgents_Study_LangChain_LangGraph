from langchain_core.prompts import ChatPromptTemplate

# Способ 1: from_messages — самый гибкий и частый
prompt = ChatPromptTemplate.from_messages([
    ("system", "Ты эксперт по {domain}"),
    ("human",  "Объясни {concept} простыми словами"),
])

# Вызываем как Runnable
result = prompt.invoke({
    "domain":  "машинное обучение",
    "concept": "градиентный спуск",
})

print(type(result))            # ChatPromptValue
print(result.to_messages())
# [
#   SystemMessage(content="Ты эксперт по машинное обучение"),
#   HumanMessage(content="Объясни градиентный спуск простыми словами"),
# ]

# Способ 2: from_template — только один HumanMessage
from langchain_core.prompts import ChatPromptTemplate

simple = ChatPromptTemplate.from_template("Переведи на английский: {text}")
# Эквивалентно:
# ChatPromptTemplate.from_messages([("human", "Переведи на английский: {text}")])