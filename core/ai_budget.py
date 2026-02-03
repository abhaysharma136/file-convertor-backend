# core/ai_budget.py
import datetime
from core.config import MAX_AI_CALLS_PER_DAY
_ai_calls_today = 0
_ai_day = datetime.date.today()

def can_use_ai() -> bool:
    global _ai_calls_today, _ai_day

    today = datetime.date.today()
    if today != _ai_day:
        _ai_day = today
        _ai_calls_today = 0

    return _ai_calls_today < MAX_AI_CALLS_PER_DAY


def register_ai_call():
    global _ai_calls_today
    _ai_calls_today += 1