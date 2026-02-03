from datetime import date
from core.config import FREE_DAILY_LIMITS, CREDIT_COST

# In-memory store (Redis later)
credit_store = {}
quota_store = {}


def today_key():
    return date.today().isoformat()


def get_remaining_free(ip_hash: str, service: str):
    key = f"{ip_hash}:{service}:{today_key()}"
    used = quota_store.get(key, 0)
    return FREE_DAILY_LIMITS[service] - used

def get_credits(ip_hash:str):
    return credit_store.get(ip_hash, 0)

def consume_free(ip_hash: str, service: str):
    key = f"{ip_hash}:{service}:{today_key()}"
    quota_store[key] = quota_store.get(key, 0) + 1

def consume_credit(ip_hash: str, service: str):
    cost = CREDIT_COST[service]
    if cost == 0:
        return True

    balance = credit_store.get(ip_hash, 0)
    if balance < cost:
        return False

    credit_store[ip_hash] = balance - cost
    return True


def authorize_usage(ip_hash: str, service: str, *, use_credit: bool, allow_credit_fallback: bool = False):
    remaining_free = get_remaining_free(ip_hash, service)

    # 🔵 USER EXPLICITLY WANTS CREDIT
    if use_credit:
        if get_credits(ip_hash) >= CREDIT_COST[service]:
            return {
                "allowed": True,
                "mode": "credit",
                "remaining_free": remaining_free
            }
        return {
            "allowed": False,
            "error": "insufficient_credits",
            "remaining_free": remaining_free
        }

    # 🟢 USER WANTS FREE
    if remaining_free > 0:
        consume_free(ip_hash, service)
        return {
            "allowed": True,
            "mode": "free",
            "remaining_free": remaining_free - 1
        }

    # 🔁 Optional fallback to credit
    if allow_credit_fallback and get_credits(ip_hash) >= CREDIT_COST[service]:
        return {
            "allowed": True,
            "mode": "credit",
            "remaining_free": 0
        }

    return {
        "allowed": False,
        "error": "quota_exhausted",
        "remaining_free": 0
    }
