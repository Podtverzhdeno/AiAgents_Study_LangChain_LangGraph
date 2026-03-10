# Production — замена InMemoryStore на БД
# InMemoryStore — только для разработки. В продакшене данные теряются при перезапуске.

# ── PostgreSQL ────────────────────────────────────────────
from langgraph.store.postgres import PostgresStore

store = PostgresStore.from_conn_string(
    "postgresql://user:password@localhost/dbname"
)

# ── Redis ─────────────────────────────────────────────────
from langgraph.store.redis import RedisStore

store = RedisStore.from_conn_string("redis://localhost:6379")

# Интерфейс одинаковый для всех — код агента не меняется!
store.put(("users",), "user_123", {"name": "Алексей"})
item = store.get(("users",), "user_123")