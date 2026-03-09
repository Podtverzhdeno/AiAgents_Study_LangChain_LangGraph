from langchain_core.output_parsers import JsonOutputParser

parser = JsonOutputParser()

# Умеет извлечь JSON даже если вокруг есть текст
result = parser.invoke(AIMessage(content='Вот результат: {"score": 8, "ok": true}'))
print(result)         # {"score": 8, "ok": True}
print(type(result))   # dict

# Поддерживает стриминг — dict собирается по мере прихода токенов
chain = prompt | llm | JsonOutputParser()
for chunk in chain.stream({"input": "..."}):
    print(chunk)  # dict достраивается постепенно