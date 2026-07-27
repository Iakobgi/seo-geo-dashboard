def heuristic_seo_score(data: dict) -> float:
    """A simple, deterministic fallback score so the app is useful even
    with no AI key configured. 0-100 scale."""
    score = 0
    title = data.get("title") or ""
    meta = data.get("meta_description") or ""
    h1 = data.get("h1") or ""

    if title:
        score += 20 if 10 <= len(title) <= 60 else 10
    if meta:
        score += 20 if 50 <= len(meta) <= 160 else 10
    if h1:
        score += 15
    if data.get("word_count", 0) >= 300:
        score += 20
    elif data.get("word_count", 0) >= 100:
        score += 10
    if data.get("images_count", 0) > 0:
        score += 10
    if data.get("links_count", 0) > 0:
        score += 10
    if data.get("load_time") is not None and data["load_time"] < 1.5:
        score += 5

    return round(min(score, 100), 1)


def heuristic_geo_score(data: dict) -> float:
    """Rough proxy for how 'answer-engine friendly' the content is:
    rewards clear structure (H2s), enough text, and presence of a clear H1/title."""
    score = 0
    if data.get("h1"):
        score += 20
    if len(data.get("h2") or []) >= 2:
        score += 30
    elif len(data.get("h2") or []) >= 1:
        score += 15
    if data.get("word_count", 0) >= 300:
        score += 30
    elif data.get("word_count", 0) >= 100:
        score += 15
    if data.get("meta_description"):
        score += 20

    return round(min(score, 100), 1)
