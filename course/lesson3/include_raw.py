# Иногда нужно видеть и распарсенный объект, и оригинальный AIMessage
structured_llm = llm.with_structured_output(MovieReview, include_raw=True)

result = structured_llm.invoke("Рецензия на Матрицу")

print(result["parsed"])        # MovieReview объект
print(result["raw"])           # оригинальный AIMessage
print(result["parsing_error"]) # None если всё ок, иначе ошибка