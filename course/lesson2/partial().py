# Фиксируем domain заранее — получаем специализированный промпт
base_prompt = ChatPromptTemplate.from_messages([
    ("system", "Ты эксперт по {domain}"),
    ("human", "{question}"),
])

python_prompt = base_prompt.partial(domain="Python")
ml_prompt = base_prompt.partial(domain="машинному обучению")

# Теперь нужно передать только question
python_prompt.invoke({"question": "Что такое GIL?"})
ml_prompt.invoke({"question": "Что такое overfitting?"})
