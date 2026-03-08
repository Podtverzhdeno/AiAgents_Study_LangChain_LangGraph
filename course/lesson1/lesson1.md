Урок 1: Runnable Protocol — полное погружение

Часть 1: Что такое Runnable и зачем он нужен
Представьте, что вы строите конвейер обработки данных. У вас есть этапы: очистить текст → перевести → сократить → сохранить. Каждый этап — отдельная функция. Проблема: как их соединить гибко, чтобы можно было менять порядок, запускать параллельно, легко заменять один этап другим?
Именно это решает Runnable — единый интерфейс для любого шага обработки.
Без Runnable:                    С Runnable (LCEL):
───────────────                  ──────────────────
result1 = clean(text)            chain = clean | translate | shorten
result2 = translate(result1)     result = chain.invoke(text)
result3 = shorten(result2)
Runnable — это контракт: у меня есть вход и выход, и я умею обрабатывать данные шестью способами.

Часть 2: Шесть методов Runnable
┌─────────────────────────────────────────────────────────┐
│                      RUNNABLE                           │
├─────────────────┬───────────────────────────────────────┤
│   СИНХРОННЫЕ    │   АСИНХРОННЫЕ                         │
├─────────────────┼───────────────────────────────────────┤
│ invoke(x)       │ await ainvoke(x)                      │
│ batch([x,y,z])  │ await abatch([x,y,z])                 │
│ stream(x)       │ async for chunk in astream(x)         │
└─────────────────┴───────────────────────────────────────┘

invoke — один вход, один выход. Базовый случай.
batch — список входов, список выходов. Запускает параллельно под капотом.
stream — один вход, выход приходит по чанкам (токенам для LLM).
a-версии — те же, но асинхронные (для asyncio).


Часть 3: Типы Runnable — зоопарк компонентов
Runnable (интерфейс)
│
├── RunnableLambda        — обёртка над обычной функцией
├── RunnableSequence      — цепочка (A | B | C)
├── RunnableParallel      — параллельные ветки ({k1: A, k2: B})
├── RunnablePassthrough   — пробрасывает вход без изменений
├── RunnableBranch        — условная логика (if/else)
│
├── ChatPromptTemplate    — dict → PromptValue
├── ChatOpenAI            — PromptValue → AIMessage
├── StrOutputParser       — AIMessage → str
└── ... (всё остальное в LangChain тоже Runnable)

Часть 4: Код — разбираем каждый тип
4.1 RunnableLambda — любая функция становится Runnable
from langchain_core.runnables import RunnableLambda

# Оборачиваем обычную функцию
strip_text  = RunnableLambda(lambda x: x.strip())
split_words = RunnableLambda(lambda x: x.split())
count_words = RunnableLambda(lambda x: len(x))

# Каждый — полноценный Runnable
print(strip_text.invoke("  привет  "))   # "привет"
print(split_words.invoke("раз два три")) # ["раз", "два", "три"]
print(count_words.invoke(["a", "b"]))    # 2

# batch — обрабатывает список параллельно
print(strip_text.batch(["  а  ", "  б  ", "  в  "]))
# ["а", "б", "в"]

# stream — для лямбд приходит сразу целиком (не по чанкам)
for chunk in strip_text.stream("  тест  "):
print(repr(chunk))  # "тест"
4.2 RunnableSequence — цепочка через |
from langchain_core.runnables import RunnableLambda

# Оператор | создаёт RunnableSequence
pipeline = (
RunnableLambda(lambda x: x.strip())
| RunnableLambda(lambda x: x.split())
| RunnableLambda(lambda x: len(x))
)

# Что происходит под капотом:
# strip.__or__(split)  → RunnableSequence([strip, split])
# seq.__or__(count)    → RunnableSequence([strip, split, count])

print(pipeline.invoke("  раз два три  "))  # 3
print(pipeline.batch(["  а б  ", "  в г д  "]))  # [2, 3]
4.3 RunnableParallel — параллельные ветки
from langchain_core.runnables import RunnableParallel, RunnableLambda

# Каждая ветка получает ОДИН И ТОТ ЖЕ вход
# Все ветки выполняются параллельно
# Результат — dict с ключами

analyze = RunnableParallel({
"upper":   RunnableLambda(str.upper),
"length":  RunnableLambda(len),
"words":   RunnableLambda(lambda x: x.split()),
"reverse": RunnableLambda(lambda x: x[::-1]),
})

result = analyze.invoke("langchain")
print(result)
# {
#   "upper":   "LANGCHAIN",
#   "length":  9,
#   "words":   ["langchain"],
#   "reverse": "niahcgnal"
# }

# Можно вставить в цепочку — выход будет dict
pipeline = RunnableLambda(str.strip) | analyze
print(pipeline.invoke("  hello  "))
4.4 RunnablePassthrough — пробросить вход дальше
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda

translate = RunnableLambda(lambda x: f"[перевод: {x}]")  # имитация перевода

# Классический паттерн: сохранить оригинал И добавить обработанную версию
pipeline = RunnableParallel({
"original":    RunnablePassthrough(),   # вход как есть
"translated":  translate,               # обработанный вход
"length":      RunnableLambda(len),     # длина входа
})

result = pipeline.invoke("Привет мир")
print(result)
# {
#   "original":   "Привет мир",
#   "translated": "[перевод: Привет мир]",
#   "length":     10
# }
4.5 .assign() — добавить поля к dict
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
4.6 RunnableBranch — условная логика
from langchain_core.runnables import RunnableBranch, RunnableLambda

short_handler = RunnableLambda(lambda x: f"[короткий] {x}")
long_handler  = RunnableLambda(lambda x: f"[длинный] {x[:20]}...")
default       = RunnableLambda(lambda x: f"[средний] {x}")

branch = RunnableBranch(
(lambda x: len(x) < 10,  short_handler),  # условие, обработчик
(lambda x: len(x) > 100, long_handler),
default,                                    # если ни одно не сработало
)

print(branch.invoke("Привет"))                    # [короткий] Привет
print(branch.invoke("А" * 200))                   # [длинный] АААААААААААААААААААА...
print(branch.invoke("Обычный текст средней длины")) # [средний] ...
4.7 Реальная LLM-цепочка
pythonimport os
from dotenv import load_dotenv
load_dotenv()

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Цепочка перевода
translate_chain = (
ChatPromptTemplate.from_template("Переведи на английский: {text}")
| llm
| StrOutputParser()
)

# Смотрим типы на каждом шаге — важно для понимания!
prompt = ChatPromptTemplate.from_template("Переведи на английский: {text}")

step1 = prompt.invoke({"text": "Привет мир"})
print(type(step1).__name__)    # ChatPromptValue
print(step1.to_messages())     # [HumanMessage(content='Переведи на английский: Привет мир')]

step2 = llm.invoke(step1)
print(type(step2).__name__)    # AIMessage
print(step2.content)           # "Hello, world"

step3 = StrOutputParser().invoke(step2)
print(type(step3).__name__)    # str
print(step3)                   # "Hello, world"

# Итог через chain — то же самое за одну строку
print(translate_chain.invoke({"text": "Привет мир"}))  # "Hello, world"

# Стриминг токенов
print("Стриминг: ", end="")
for chunk in translate_chain.stream({"text": "Квантовая физика очень интересна"}):
print(chunk, end="", flush=True)
print()

# Batch — несколько переводов параллельно
results = translate_chain.batch([
{"text": "Кот"},
{"text": "Собака"},
{"text": "Птица"},
])
print(results)  # ["Cat", "Dog", "Bird"]
```

---

## Часть 5: Как типы текут через цепочку
```
invoke({"text": "Привет мир"})
│
▼
ChatPromptTemplate
dict → ChatPromptValue
[HumanMessage("Переведи на английский: Привет мир")]
│
▼
ChatOpenAI
ChatPromptValue → AIMessage
AIMessage(content="Hello, world")
│
▼
StrOutputParser
AIMessage → str
"Hello, world"
│
▼
result
Несовместимость типов — частая причина ошибок. LangChain делает некоторые автоконвертации (str → HumanMessage, PromptValue → Messages), но знать типы важно.

🏠 Домашнее задание
Задание 1 — лёгкое
Создайте цепочку из трёх RunnableLambda:

strip пробелов
split по пробелам
подсчёт количества слов

python# Ожидаемый результат:
chain.invoke("  hello world foo  ")  # → 3
chain.batch(["  а б  ", "  в г д е  "])  # → [2, 4]

Задание 2 — среднее
Напишите RunnableParallel, который принимает строку и возвращает:
python{
"word_count":  int,   # количество слов
"char_count":  int,   # количество символов без пробелов
"first_word":  str,   # первое слово
"is_question": bool,  # True если строка заканчивается на "?"
}

# Проверьте:
analyze.invoke("Как дела у тебя?")
# {"word_count": 4, "char_count": 13, "first_word": "Как", "is_question": True}

Задание 3 — сложное (с LLM)
Создайте цепочку:

Принимает {"topic": str, "style": str}
Промпт: "Напиши одно предложение о {topic} в стиле {style}"
Через .assign() добавьте к результату:

char_count — длина ответа
word_count — количество слов в ответе


Итоговый dict должен выглядеть так:

python{
"topic":      "кошки",
"style":      "научный",
"sentence":   "Felis catus демонстрирует...",
"char_count": 42,
"word_count": 6,
}

❓ Вопросы для самопроверки

Что возвращает оператор | применённый к двум Runnable? Какой тип объекта?
В чём разница между invoke и batch? Когда batch предпочтительнее?
Зачем нужен RunnablePassthrough? Придумайте свой сценарий где без него не обойтись.
Если chain = A | B | C и вы вызываете chain.batch([x1, x2, x3]) — каждый из A, B, C вызывается сколько раз?
Чем RunnableParallel отличается от RunnableSequence? Нарисуйте схему потока данных для каждого.
Что произойдёт если выход RunnableLambda вернёт тип, несовместимый со входом следующего шага?
В чём разница между .assign() и RunnableParallel? Когда использовать каждый?