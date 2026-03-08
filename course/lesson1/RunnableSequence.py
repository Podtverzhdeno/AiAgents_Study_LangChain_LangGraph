from langchain_core.runnables import RunnableLambda

# Оператор | создаёт RunnableSequence
pipeline = (RunnableLambda(lambda x: x.strip()) | RunnableLambda(lambda x: x.split()) | RunnableLambda(lambda x: len(x)))

# Что происходит под капотом:
# strip.__or__(split)  → RunnableSequence([strip, split])
# seq.__or__(count)    → RunnableSequence([strip, split, count])

print(pipeline.invoke(" раз    два три"))
print(pipeline.batch([" a b ", "c d", " e f g k l m "])) # [2, 2, 6]