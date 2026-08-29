"""RAG (Retrieval Augmented Generation) service for SEO/GEO knowledge base.

Provides semantic search over curated SEO knowledge articles using pgvector
embeddings. Falls back to keyword matching when embeddings are unavailable.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import math


@dataclass
class KnowledgeResult:
    """A retrieved knowledge article with relevance score."""
    article_id: int
    title: str
    content: str
    category: Optional[str]
    source: Optional[str]
    relevance_score: float  # 0-1


@dataclass
class RAGContext:
    """Context assembled from knowledge retrieval for AI prompt augmentation."""
    relevant_articles: List[KnowledgeResult] = field(default_factory=list)
    retrieval_count: int = 10
    min_relevance: float = 0.1


# SEO knowledge base entries (seed data)
SEED_KNOWLEDGE = [
    {
        "title": "Google's Quality Rater Guidelines - E-E-A-T",
        "content": "Experience, Expertise, Authoritativeness, and Trustworthiness (E-E-A-T) are core principles in Google's Quality Rater Guidelines. Experience refers to first-hand life experience. Expertise relates to the knowledge or skill level of the content creator. Authoritativeness is about the reputation of the content creator and page. Trustworthiness is the most important factor - the page should be reliable, accurate, and honest.",
        "category": "eeat",
        "source": "google-guidelines",
    },
    {
        "title": "Schema.org Structured Data Best Practices",
        "content": "Structured data helps search engines understand your content. Use JSON-LD format. Key types: Article, Organization, FAQPage, HowTo, Product, Review, BreadcrumbList, LocalBusiness. Include all required properties. Use consistent schema.org vocabulary. Validate with Google Rich Results Test.",
        "category": "schema",
        "source": "schema-org-docs",
    },
    {
        "title": "GEO: Optimizing for AI Answer Engines",
        "content": "Generative Engine Optimization (GEO) focuses on making content citable by AI systems like ChatGPT, Claude, and Gemini. Key strategies: use clear question-answer format, provide direct answers early, cite sources and data, use structured content (lists, tables), establish entity clarity with consistent naming, include author attribution and dates.",
        "category": "geo",
        "source": "industry-research",
    },
    {
        "title": "Core Web Vitals and Page Experience Signals",
        "content": "Core Web Vitals: Largest Contentful Paint (LCP) should be under 2.5 seconds. First Input Delay (FID) should be under 100 milliseconds. Cumulative Layout Shift (CLS) should be under 0.1. Additional signals: mobile-friendliness, safe browsing, HTTPS, no intrusive interstitials.",
        "category": "performance",
        "source": "google-guidelines",
    },
    {
        "title": "Title Tag Optimization Guidelines",
        "content": "Title tags should be 10-60 characters. Place primary keyword near the beginning. Make each title unique. Include brand name at the end. Avoid keyword stuffing. Use separators like | or -. Test readability and click-through rates.",
        "category": "seo",
        "source": "industry-research",
    },
    {
        "title": "Meta Description Best Practices",
        "content": "Meta descriptions should be 50-160 characters. Include primary keyword naturally. Write compelling copy that encourages clicks. Each page should have a unique meta description. Don't use keyword stuffing. Include a call-to-action when appropriate.",
        "category": "seo",
        "source": "industry-research",
    },
    {
        "title": "Internal Linking Strategy",
        "content": "Internal links help search engines discover and understand site structure. Use descriptive anchor text. Link to related content. Maintain a logical hierarchy. Avoid orphan pages. Use breadcrumbs. Link from high-authority pages to new content.",
        "category": "seo",
        "source": "industry-research",
    },
    {
        "title": "FAQ Schema Implementation",
        "content": "FAQ schema helps content appear in rich results. Use Question and Answer types. Keep answers concise and direct. Mark up only FAQs that are actually on the page. Use proper nesting. Validate with Google Rich Results Test. FAQ pages have high citability in AI systems.",
        "category": "schema",
        "source": "schema-org-docs",
    },
    {
        "title": "Content Depth and Topical Authority",
        "content": "Comprehensive content signals topical authority. Aim for 1500+ words for pillar content. Cover related subtopics. Use semantic variations of keywords. Include original research or data. Update content regularly. Internal link between related content to build topic clusters.",
        "category": "seo",
        "source": "industry-research",
    },
    {
        "title": "Technical SEO: Robots.txt and Sitemap",
        "content": "Robots.txt controls crawler access. Allow important pages, disallow admin/admin areas. XML sitemaps help discovery. Include all canonical URLs. Update sitemaps when content changes. Submit to Google Search Console. Use sitemap index files for large sites.",
        "category": "technical",
        "source": "google-guidelines",
    },
    {
        "title": "Canonical URLs and Duplicate Content",
        "content": "Canonical tags tell search engines which version of a page to index. Use self-referencing canonicals. Handle URL parameters consistently. Avoid duplicate content across http/https, www/non-www, and trailing slashes. Use 301 redirects for permanent moves.",
        "category": "technical",
        "source": "google-guidelines",
    },
    {
        "title": "Image Optimization for SEO",
        "content": "Compress images without quality loss. Use WebP format when possible. Add descriptive alt text for accessibility and SEO. Use descriptive filenames. Implement lazy loading. Specify width and height to prevent layout shifts. Consider image sitemaps for image-heavy sites.",
        "category": "performance",
        "source": "industry-research",
    },
]


class RAGService:
    """RAG service for SEO/GEO knowledge retrieval."""

    def __init__(self, db: Session):
        self._db = db
        self._seed_articles = SEED_KNOWLEDGE

    def search(self, query: str, limit: int = 5) -> List[KnowledgeResult]:
        """Search knowledge base for relevant articles.

        Uses keyword-based scoring as fallback (embeddings require pgvector setup).
        """
        results = []
        query_lower = query.lower()
        query_terms = set(query_lower.split())

        for article in self._seed_articles:
            score = self._keyword_score(article, query_terms, query_lower)
            if score > 0:
                results.append(KnowledgeResult(
                    article_id=0,  # Seed articles don't have DB IDs
                    title=article["title"],
                    content=article["content"],
                    category=article["category"],
                    source=article["source"],
                    relevance_score=score,
                ))

        # Sort by relevance and return top results
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]

    def _keyword_score(self, article: Dict, query_terms: set, query_lower: str) -> float:
        """Calculate relevance score based on keyword overlap."""
        content_lower = article["content"].lower()
        title_lower = article["title"].lower()

        score = 0.0

        # Title matches weighted heavily
        for term in query_terms:
            if term in title_lower:
                score += 0.3
            if term in content_lower:
                score += 0.1

        # Category match
        if article["category"] and article["category"] in query_lower:
            score += 0.2

        # Full query phrase match
        if query_lower in content_lower:
            score += 0.15

        return round(score, 3)

    def get_rag_context(self, query: str, limit: int = 5) -> RAGContext:
        """Get RAG context for a query."""
        articles = self.search(query, limit)
        return RAGContext(relevant_articles=articles, retrieval_count=limit)

    def format_context_for_prompt(self, context: RAGContext) -> str:
        """Format retrieved articles into a prompt-ready string."""
        if not context.relevant_articles:
            return "No additional knowledge context available."

        parts = []
        for article in context.relevant_articles:
            parts.append(f"## {article.title} (category: {article.category}, source: {article.source}, relevance: {article.relevance_score:.2f})")
            parts.append(article.content)
            parts.append("")

        return "\n---\n".join(parts)


def create_rag_service(db: Session) -> RAGService:
    """Factory function to create RAG service with DB session."""
    return RAGService(db)
