from langchain_core.output_parsers import XMLOutputParser

parser = XMLOutputParser(tags=["person", "name", "age", "city"])

result = parser.invoke(AIMessage(content="""
<person>
  <name>Алексей</name>
  <age>28</age>
  <city>Москва</city>
</person>
"""))

print(result)
# {"person": [{"name": "Алексей"}, {"age": "28"}, {"city": "Москва"}]}