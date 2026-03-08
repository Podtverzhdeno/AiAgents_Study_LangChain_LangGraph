# Задание 1 — лёгкое
# Создайте две цепочки с одним промптом но разными temperature:
#
# temperature=0 — запустите 3 раза, проверьте одинаковые ли ответы
# temperature=1.2 — запустите 3 раза, проверьте разные ли ответы
#
# Промпт: "Придумай одно случайное русское имя"

from langchain_ollama import ChatOllama

llm1 = ChatOllama(
    model = "qwen2.5:7b",
    temperature = 0
)

llm2 = ChatOllama(
    model = "qwen2.5:7b",
    temperature = 0.5
)

llm3 = ChatOllama(
    model = "qwen2.5:7b",
    temperature = 1.2
)

print(llm1.invoke("Придумай одно случайное Русское имя"))
print(llm2.invoke("Придумай одно случайное Русское имя"))
print(llm3.invoke("Придумай одно случайное Русское имя"))