from langchain_core.exceptions import OutputParserException
from pydantic import ValidationError

def safe_invoke(chain, input_data):
    try:
        return chain.invoke(input_data)

    except OutputParserException as e:
        # LLM ответила, но не в нужном формате
        print(f"Ошибка парсинга: {e}")
        return None

    except ValidationError as e:
        # Pydantic не прошёл валидацию
        print(f"Ошибка валидации: {e}")
        return None

    except Exception as e:
        # Всё остальное (сеть, API)
        print(f"Неизвестная ошибка: {e}")
        raise  # пробрасываем дальше

result = safe_invoke(chain, {"input": "тест"})
if result is None:
    print("Используем значение по умолчанию")