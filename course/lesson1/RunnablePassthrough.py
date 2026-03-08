from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda

# RunnablePassthrough — пробросить вход дальше

translate = RunnableLambda(lambda x: f"перевод {x}") #создаем имитацию перевода

pipeline = RunnableParallel({
    "original": RunnablePassthrough(),
    "translate": translate,
    "length": RunnableLambda(len)
})

result = pipeline.invoke("Капитанская Дочка")
print(result) # {'original': 'Капитанская Дочка', 'translate': 'перевод Капитанская Дочка', 'length': 17}