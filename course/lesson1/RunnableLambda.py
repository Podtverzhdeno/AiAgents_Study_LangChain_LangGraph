from langchain_core.runnables import RunnableLambda

strip_text = RunnableLambda(lambda x: x.strip())
split_text = RunnableLambda(lambda x: x.split())
count_words = RunnableLambda(lambda x: len(x))

# Каждый - полноценный Runnable
print(strip_text.invoke("   Первы  й   ")) # Первы  й
print(split_text.invoke(" Второй Третий Четвертый")) #['Второй', 'Третий', 'Четвертый']
print(count_words.invoke("Пятый")) # 5

print(strip_text.batch([" Один    ", " Два     ", "Три      "])) #['Один', 'Два', 'Три']

# stream - для лямбд приходит сразу целиком (не по чанкам)

for chunk in strip_text.stream(" тестовый текст      "):
    print(repr(chunk)) # 'тестовый текст'