# Способ 2: декоратор + Pydantic схема — для сложных входов
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional

class SearchInput(BaseModel):
    query:       str            = Field(description="Поисковый запрос")
    max_results: int            = Field(default=5, ge=1, le=20,
                                        description="Количество результатов")
    language:    Optional[str]  = Field(default="ru",
                                        description="Язык результатов: ru, en")

@tool(args_schema=SearchInput)
def search_database(query: str, max_results: int = 5, language: str = "ru") -> list:
    """Поиск в корпоративной базе знаний компании.

    Используй когда нужно найти информацию о продуктах, политиках
    или внутренних процессах компании. НЕ используй для поиска
    в интернете или получения актуальных новостей.
    """
    # имитация поиска
    return [f"Результат {i} для '{query}'" for i in range(max_results)]

print(search_database.args)
# {
#   "query":       {"type": "string", "description": "Поисковый запрос"},
#   "max_results": {"type": "integer", ...},
#   "language":    {"type": "string", ...}
# }