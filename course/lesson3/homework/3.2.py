# Задание 2 — среднее
# Создайте structured_output для анализа вакансии:
# pythonclass JobAnalysis(BaseModel):
# position:        str        # название должности
# required_skills: List[str]  # обязательные навыки
# nice_to_have:    List[str]  # желательные навыки
# experience_years: int       # лет опыта
# is_remote:       bool       # удалённая ли работа
# seniority:       str        # junior/middle/senior/lead

from pydantic import BaseModel, Field
from typing import List
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model = "qwen2.5:7b",
    temperature= 0
)

class JobAnalysis(BaseModel):
    position: str
    required_skills: List[str] = Field("Обязательные навыки")
    nice_to_have: List[str] = Field("Желательные навыки")
    experience_years: int
    is_remote: bool
    seniority: str

llm_structured = llm.with_structured_output(JobAnalysis)

result = llm_structured.invoke("Опиши вакансию Ai Agent Engineer")

print(result.position)
print(result.required_skills)
print(result.nice_to_have)
print(result.experience_years)
print(result.is_remote)
print(result.seniority)