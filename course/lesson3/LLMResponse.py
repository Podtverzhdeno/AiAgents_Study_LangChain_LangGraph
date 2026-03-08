from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model = "qwen2.5:7b",
    temperature = 0
)

response = llm.invoke([HumanMessage(content="Привет!")])

# Сам ответ
print(response.content)           # "Привет! Чем могу помочь?"

# Метаданные — токены, модель, причина остановки
print(response.response_metadata)
# {
#   "token_usage": {
#     "completion_tokens": 9,
#     "prompt_tokens": 10,
#     "total_tokens": 19
#   },
#   "model_name": "gpt-4o-mini",
#   "finish_reason": "stop"    ← "stop"=норма, "length"=обрезало по max_tokens
# }

# Удобный доступ к токенам
print(response.usage_metadata)
# {"input_tokens": 10, "output_tokens": 9, "total_tokens": 19}