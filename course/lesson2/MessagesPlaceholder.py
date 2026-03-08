from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

prompt = ChatPromptTemplate.from_messages([
    ("system", "Ты ассистент"),
    MessagesPlaceholder("history"),   # сюда подставится список Messages
    ("human", "{input}"),
])

# Подставляем историю
result = prompt.invoke({
    "history": [
        HumanMessage(content="Меня зовут Алексей"),
        AIMessage(content="Приятно познакомиться, Алексей!"),
    ],
    "input": "Как меня зовут?",
})

print(result.to_messages())
# [
#   SystemMessage("Ты ассистент"),
#   HumanMessage("Меня зовут Алексей"),
#   AIMessage("Приятно познакомиться, Алексей!"),
#   HumanMessage("Как меня зовут?"),
# ]