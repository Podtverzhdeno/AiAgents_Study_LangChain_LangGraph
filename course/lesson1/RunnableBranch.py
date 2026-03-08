from langchain_core.runnables import RunnableBranch, RunnableLambda

short_handler = RunnableLambda(lambda x: f"[короткий] {x}")
long_handler = RunnableLambda(lambda x: f"[длинный] {x[:20]}...")
default = RunnableLambda(lambda x: f"[обычный] {x}")

branch = RunnableBranch(
    (lambda x: len(x) < 10, short_handler), # Если длина слова меньше 10, тогда вызываем short_handler
    (lambda x: len(x) > 100, long_handler),
    default
)

print(branch.invoke("Привет"))
print(branch.invoke("Очень длинный привет" * 200))
print(branch.invoke("Самый обычный привет"))