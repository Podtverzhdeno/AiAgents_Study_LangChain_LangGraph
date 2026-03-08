# Задание 1 — лёгкое
# Создайте цепочку из трёх RunnableLambda:
#
# strip пробелов
# split по пробелам
# подсчёт количества слов
#
# Ожидаемый результат:
# chain.invoke("  hello world foo  ")  # → 3
# chain.batch(["  а б  ", "  в г д е  "])  # → [2, 4]

from langchain_core.runnables import RunnableLambda

text_strip = RunnableLambda(lambda x: x.strip())
text_split = RunnableLambda(lambda x: x.split())
word_len = RunnableLambda(lambda x: len(x))

chain = text_strip | text_split | word_len

print(chain.invoke("  Hello World foo  "))
print(chain.batch(["  a b ", " c d e f    "]))