import json
import httpx
from app.config import settings
from app.utils.helpers import heuristic_seo_score, heuristic_geo_score


SYSTEM_PROMPT = """You are an SEO and GEO (Generative Engine Optimization) expert.
You will be given extracted on-page data from a webpage.
Respond ONLY with a valid JSON object (no markdown fences, no commentary) with this exact shape:
{
  "seo_score": <number 0-100>,
  "geo_score": <number 0-100>,
  "suggestions": ["short actionable suggestion", ...],
  "generated_content": {
    "title": "...",
    "meta": "...",
    "h1": "...",
    "faq": [{"question": "...", "answer": "..."}],
    "schema": { "@context": "https://schema.org", "@type": "Article" }
  }
}
"""


def _fallback_result(data: dict) -> dict:
    """Used when no API key is configured, or the AI call fails."""
    seo = heuristic_seo_score(data)
    geo = heuristic_geo_score(data)
    suggestions = []
    if not data.get("title"):
        suggestions.append("Add a <title> tag between 10 and 60 characters.")
    if not data.get("meta_description"):
        suggestions.append("Add a meta description between 50 and 160 characters.")
    if not data.get("h1"):
        suggestions.append("Add a single, clear H1 heading.")
    if len(data.get("h2") or []) < 2:
        suggestions.append("Add more H2 subheadings to improve structure for AI answer engines.")
    if data.get("word_count", 0) < 300:
        suggestions.append("Expand the content to at least 300 words for better topical coverage.")
    if not suggestions:
        suggestions.append("Page looks solid — consider adding FAQ schema for richer AI answers.")

    return {
        "seo_score": seo,
        "geo_score": geo,
        "suggestions": suggestions,
        "generated_content": {
            "title": data.get("title") or "Suggested SEO Title",
            "meta": data.get("meta_description") or "Suggested meta description under 160 characters.",
            "h1": data.get("h1") or "Suggested H1 heading",
            "faq": [{"question": "What is this page about?", "answer": "Summarize the main topic here."}],
            "schema": {"@context": "https://schema.org", "@type": "Article"},
        },
    }


async def call_openrouter(data: dict, model: str = None) -> dict:
    """Send extracted page data to OpenRouter and get back SEO/GEO analysis.
    Falls back to a deterministic heuristic if no key is set or the call fails."""
    if not settings.OPENROUTER_API_KEY:
        return _fallback_result(data)

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model or settings.AI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(data)[:8000]},
        ],
        "response_format": {"type": "json_object"},
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            result = resp.json()
            content = result["choices"][0]["message"]["content"]
            return json.loads(content)
    except Exception:
        # Never let an AI/API hiccup break the audit — degrade gracefully.
        return _fallback_result(data)
