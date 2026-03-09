# Задание 2 — среднее
# Создайте PydanticOutputParser для анализа книги:
# pythonclass BookAnalysis(BaseModel):
# title:       str
# author:      str
# genre:       str
# themes:      List[str]   # основные темы
# difficulty:  str         # easy/medium/hard
# rating:      int         = Field(ge=1, le=10)
# Используйте get_format_instructions() в промпте. Протестируйте на 2-3 книгах.