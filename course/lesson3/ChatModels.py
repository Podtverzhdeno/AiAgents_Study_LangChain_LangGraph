from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",   # какая модель
    temperature=0,          # 0 = детерминированно, 1 = креативно, макс ~2
    max_tokens=500,         # максимум токенов в ответе
    timeout=30,             # секунд до таймаута запроса
    max_retries=2,          # повторов при сбое сети
)


### Temperature — самый важный параметр

temperature=0.0  #всегда один и тот же ответ (факты, код, классификация)
temperature=0.3  #чуть вариативнее (аналитика, резюме)
temperature=0.7   #баланс (общение, объяснения)
temperature=1.5  #творческий режим (стихи, истории, brainstorm)

# Правило: если нужна воспроизводимость → 0, если нужно разнообразие → выше



# Смена провайдера — только импорт меняется

# OpenAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini")

# Anthropic
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")

# Google
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# Остальной код — без изменений
chain = prompt | llm | parser

# Это и есть сила абстракции LangChain.