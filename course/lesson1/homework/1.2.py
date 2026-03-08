# Задание 2 — среднее
# Напишите RunnableParallel, который принимает строку и возвращает:
# {
#     "word_count":  int,   # количество слов
#     "char_count":  int,   # количество символов без пробелов
#     "first_word":  str,   # первое слово
#     "is_question": bool,  # True если строка заканчивается на "?"
# }
#
# Проверьте:
# analyze.invoke("Как дела у тебя?")
# # {"word_count": 4, "char_count": 13, "first_word": "Как", "is_question": True}

from langchain_core.runnables import RunnableLambda, RunnableParallel

analyze = RunnableParallel({
    "word_count": lambda x: len(x.split()),
    "char_count": lambda x: len(x.replace(" ", "")),
    "first_word": lambda x: x.split()[0],
    "is_question": lambda x: x.strip()[-1] == "?"
})

print(analyze.invoke("Как дела у тебя?"))