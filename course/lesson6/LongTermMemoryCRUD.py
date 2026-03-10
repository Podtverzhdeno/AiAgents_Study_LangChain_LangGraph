from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

# ── CREATE / UPDATE ───────────────────────────────────────
store.put(
    ("users",),       # namespace — кортеж строк
    "user_123",       # key
    {                 # value — любой dict
        "name": "Алексей",
        "language": "Python",
        "age": 28,
    }
)

# ── READ ──────────────────────────────────────────────────
item = store.get(("users",), "user_123")

print(item.value)      # {"name": "Алексей", "language": "Python", "age": 28}
print(item.key)        # "user_123"
print(item.namespace)  # ("users",)

# Если ключ не существует — возвращает None
missing = store.get(("users",), "unknown")
print(missing)         # None

# ── DELETE ────────────────────────────────────────────────
store.delete(("users",), "user_123")

# ── LIST — все ключи в namespace ─────────────────────────
items = store.search(("users",))
for item in items:
    print(item.key, item.value)