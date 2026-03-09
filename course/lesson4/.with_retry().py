from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOllama(
    model = "qwen2.5:7b",
    temperature = 0
)

chain = ChatPromptTemplate.from_template("{input}") | llm | StrOutputParser()

# Базовый retry
resilient_chain = chain.with_retry(
    stop_after_attempt=3,        # максимум попыток
    wait_exponential_jitter=True # экспоненциальный backoff + случайность
)

# Retry только на конкретные ошибки
from openai import RateLimitError, APITimeoutError

selective_chain = chain.with_retry(
    stop_after_attempt=3,
    retry_if_exception_type=(RateLimitError, APITimeoutError),
    # другие ошибки (AuthenticationError) — не повторять
)

result = resilient_chain.invoke({"input": "Привет"})