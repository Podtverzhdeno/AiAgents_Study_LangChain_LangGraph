from langchain_core.output_parsers import CommaSeparatedListOutputParser

parser = CommaSeparatedListOutputParser()

result = parser.invoke(AIMessage(content="яблоко, груша, слива, банан"))
print(result)   # ["яблоко", "груша", "слива", "банан"]

# Тоже генерирует инструкции
print(parser.get_format_instructions())
# "Your response should be a list of comma separated values..."