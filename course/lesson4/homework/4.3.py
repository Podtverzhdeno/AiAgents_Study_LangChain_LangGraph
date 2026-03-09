# Задание 3 — сложное
# Постройте надёжную цепочку с тремя уровнями защиты:
#
# .with_retry(stop_after_attempt=3) — на случай сетевых сбоев
# .with_fallbacks([fallback_chain]) — запасная цепочка с другой моделью
# try/except с разными обработчиками для OutputParserException и общего Exception
#
# Оберните всё в функцию safe_analyze(text: str) -> BookAnalysis | None и продемонстрируйте работу.