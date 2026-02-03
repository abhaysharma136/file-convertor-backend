def estimate_tokens(text: str) -> int:
    """
    Rough token estimator:
    1 token ≈ 4 characters (safe heuristic)
    """
    if not text:
        return 0
    return max(1, len(text) // 4)
