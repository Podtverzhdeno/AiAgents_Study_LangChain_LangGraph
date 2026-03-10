from langgraph.store.memory import InMemoryStore

# Для векторного поиска нужна функция эмбеддингов
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

def embed(texts: list[str]) -> list[list[float]]:
    return embeddings.embed_documents(texts)

# Store с поддержкой векторного поиска
store = InMemoryStore(index={
    "embed": embed,
    "dims":  1536,   # размерность text-embedding-3-small
})

# Заполняем данными
store.put(("memories", "user_123"), "fact_1", {
    "content": "Пользователь любит Python и машинное обучение",
    "type":    "preference"
})
store.put(("memories", "user_123"), "fact_2", {
    "content": "Пользователь работает в стартапе",
    "type":    "work"
})
store.put(("memories", "user_123"), "fact_3", {
    "content": "Пользователь предпочитает короткие ответы",
    "type":    "preference"
})

# ── Фильтрация по полю ────────────────────────────────────
prefs = store.search(
    ("memories", "user_123"),
    filter={"type": "preference"}   # только preferences
)
for p in prefs:
    print(p.value["content"])
# "Пользователь любит Python и машинное обучение"
# "Пользователь предпочитает короткие ответы"

# ── Векторный поиск по смыслу ─────────────────────────────
results = store.search(
    ("memories", "user_123"),
    query="Что пользователь любит делать?",   # семантический поиск
    limit=2,                                   # топ-2 результата
)
for r in results:
    print(r.value["content"], "| score:", r.score)