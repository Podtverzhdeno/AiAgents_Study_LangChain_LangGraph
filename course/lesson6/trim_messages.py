from langchain_core.messages import trim_messages, SystemMessage
from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama

llm = ChatOllama(model = "qwen2.5:7b")

# Создаём триммер
trimmer = trim_messages(
    max_tokens=1000,          # максимум токенов
    strategy="last",          # оставить последние сообщения
    token_counter=llm,        # использовать llm для подсчёта токенов
    include_system=True,      # SystemMessage всегда сохраняем
    allow_partial=False,      # не обрезать сообщение на середине
    start_on="human",         # начинать с HumanMessage (не с AIMessage)
)

# Пример работы
messages = [
    SystemMessage(content="Ты ассистент"),
    HumanMessage(content="Сообщение 1"),
    AIMessage(content="Ответ 1"),
    HumanMessage(content="Сообщение 2"),
    AIMessage(content="Ответ 2"),
    HumanMessage(content="Сообщение 3"),  # последнее
]

trimmed = trimmer.invoke(messages)
# SystemMessage сохранён + последние N сообщений в лимите токенов

# Встраиваем в цепочку
from langchain_core.runnables import RunnablePassthrough

chain_with_trim = (
        RunnablePassthrough.assign(
            history=lambda x: trimmer.invoke(x["history"])
        )
        | prompt
        | llm
        | StrOutputParser()
)