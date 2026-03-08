from langchain_core.runnables import RunnableParallel, RunnableLambda

# RunnableParallel — параллельные ветки

# Каждая ветка получает ОДИН И ТОТ ЖЕ вход
# Все ветки выполняются параллельно
# Результат — dict с ключами

analyze = RunnableParallel({
    "upper": RunnableLambda(str.upper),
    "lower": RunnableLambda(len),
    "words": RunnableLambda(lambda x: x.split()),
    "reverse": RunnableLambda(lambda x: x[::-1])
})

result = analyze.invoke("langchainCourse")
print(result) # {'upper': 'LANGCHAINCOURSE', 'lower': 15, 'words': ['langchainCourse'], 'reverse': 'esruoCniahcgnal'}

pipeline = RunnableLambda(str.strip) | RunnableLambda(len)
print(pipeline.invoke("   Hello World   ")) # 11