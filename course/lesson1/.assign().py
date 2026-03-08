from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# .assign() принимает dict, добавляет к нему новые ключи, возвращает обогащённый dict
enricher = (
    RunnablePassthrough.assign(
        word_count=lambda x: len(x["text"].split()),
        upper_text=lambda x: x["text"].upper(),
    )
    .assign(
        # второй .assign() видит уже обогащённый dict с предыдущего шага
        summary=lambda x: f"{x['word_count']} слов, первый символ: {x['text'][0]}"
    )
)

result = enricher.invoke({"text": "привет мир как дела"})
print(result)
# {
#   "text":       "привет мир как дела",
#   "word_count": 4,
#   "upper_text": "ПРИВЕТ МИР КАК ДЕЛА",
#   "summary":    "4 слов, первый символ: п"
# }