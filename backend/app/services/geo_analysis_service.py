"""GEO (Generative Engine Optimization) analysis service.

Analyzes content for AI-search readiness: answerability, citability,
question-based structure, entity clarity, attribution, and structured content.
All metrics are evidence-based with transparent scoring.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import re


class GEOMetric(str, Enum):
    """GEO analysis metrics."""
    ANSWERABILITY = "answerability"
    PASSAGE_CITABILITY = "passage_citability"
    QUESTION_STRUCTURE = "question_structure"
    ENTITY_CLARITY = "entity_clarity"
    ATTRIBUTION = "attribution"
    STRUCTURED_CONTENT = "structured_content"


@dataclass
class GEOFinding:
    """A single GEO analysis finding."""
    metric: GEOMetric
    severity: str  # critical, high, medium, low, pass
    title: str
    description: str
    evidence: Dict[str, Any]
    recommendation: str
    impact_score: float  # 0-10


@dataclass
class GEOAnalysis:
    """Complete GEO analysis for a page."""
    url: str
    metrics: Dict[GEOMetric, float]  # 0-100 scores
    findings: List[GEOFinding] = field(default_factory=list)

    @property
    def overall_score(self) -> float:
        """Weighted overall GEO score."""
        weights = {
            GEOMetric.ANSWERABILITY: 0.25,
            GEOMetric.PASSAGE_CITABILITY: 0.15,
            GEOMetric.QUESTION_STRUCTURE: 0.20,
            GEOMetric.ENTITY_CLARITY: 0.15,
            GEOMetric.ATTRIBUTION: 0.10,
            GEOMetric.STRUCTURED_CONTENT: 0.15,
        }
        total = 0.0
        weight_total = 0.0
        for metric, score in self.metrics.items():
            weight = weights.get(metric, 0.1)
            total += score * weight
            weight_total += weight
        return round(total / weight_total, 1) if weight_total > 0 else 0.0


class GEOAnalysisService:
    """Service for analyzing pages for GEO (Generative Engine Optimization)."""

    # Thresholds for answerability
    QUESTION_PATTERNS = [
        r"(?i)\bwhat is\b",
        r"(?i)\bhow to\b",
        r"(?i)\bwhy does\b",
        r"(?i)\bwhen to\b",
        r"(?i)\bwhere to\b",
        r"(?i)\bwho is\b",
        r"(?i)\bcan you\b",
        r"(?i)\bishow\b",
        r"(?i)\bdoes\b.*\?",
        r"(?i)\bis\b.*\?",
    ]

    # Patterns for direct answers
    DIRECT_ANSWER_PATTERNS = [
        r"(?i)^\s*(?:the .* is|.* refers to|.* means)\s+",  # Definition pattern
        r"(?i)^\s*(?:to .* ,\s*(?:you|one|they))\s+",  # Instruction pattern
        r"(?i)^\s*(?:according to|based on|in .* ,\s*(?:.* is|.* was))\s+",  # Attribution
    ]

    # Entity types to detect
    ENTITY_TYPES = {
        "organization": r"(?i)\b(?:company|corporation|inc\.?|llc|ltd\.?|gmbh|ag|sa|nv)\b",
        "product": r"(?i)\b(?:product|item|service|solution|platform|tool|software)\b",
        "person": r"(?i)\b(?:author|writer|expert|specialist|developer|founder|ceo|cto)\b",
        "location": r"(?i)\b(?:city|state|country|region|area|location|place)\b",
        "date": r"(?i)\b(?:january|february|march|april|may|june|july|august|september|october|november|december|\d{4})\b",
    }

    # Trust signals
    TRUST_SIGNALS = [
        r"(?i)\bcontact\s+(us|page|info)\b",
        r"(?i)\babout\s+us\b",
        r"(?i)\bprivacy\s+policy\b",
        r"(?i)\bterms\s+of\s+service\b",
        r"(?i)\bauthor\b.*(?:bio|profile|page)",
        r"(?i)\blast\s+updated\b",
        r"(?i)\bpublished\s+on\b",
    ]

    def __init__(self):
        self._compiled_patterns = {
            name: [re.compile(p) for p in patterns]
            for name, patterns in {
                "question": self.QUESTION_PATTERNS,
                "direct_answer": self.DIRECT_ANSWER_PATTERNS,
                "entity": self.ENTITY_TYPES,
                "trust": self.TRUST_SIGNALS,
            }.items()
        }

    def analyze(self, page_text: str, html: Optional[str] = None) -> GEOAnalysis:
        """Analyze a page for GEO readiness."""
        findings: List[GEOFinding] = []
        metrics: Dict[GEOMetric, float] = {}

        # Answerability
        answerability = self._analyze_answerability(page_text)
        metrics[GEOMetric.ANSWERABILITY] = answerability["score"]
        findings.extend(answerability["findings"])

        # Passage citability
        citability = self._analyze_passage_citability(page_text)
        metrics[GEOMetric.PASSAGE_CITABILITY] = citability["score"]
        findings.extend(citability["findings"])

        # Question structure
        question_structure = self._analyze_question_structure(page_text)
        metrics[GEOMetric.QUESTION_STRUCTURE] = question_structure["score"]
        findings.extend(question_structure["findings"])

        # Entity clarity
        entity = self._analyze_entity_clarity(page_text, html)
        metrics[GEOMetric.ENTITY_CLARITY] = entity["score"]
        findings.extend(entity["findings"])

        # Attribution
        attribution = self._analyze_attribution(page_text, html)
        metrics[GEOMetric.ATTRIBUTION] = attribution["score"]
        findings.extend(attribution["findings"])

        # Structured content
        structure = self._analyze_structured_content(page_text, html)
        metrics[GEOMetric.STRUCTURED_CONTENT] = structure["score"]
        findings.extend(structure["findings"])

        return GEOAnalysis(
            url="",  # Will be set by caller
            metrics=metrics,
            findings=findings,
        )

    def _analyze_answerability(self, text: str) -> Dict[str, Any]:
        """Analyze how directly the content answers questions."""
        score = 50.0  # Base score
        findings = []

        # Count question patterns
        question_count = 0
        for pattern in self._compiled_patterns["question"]:
            question_count += len(pattern.findall(text))

        # Check for direct answer patterns
        direct_answer_count = 0
        for pattern in self._compiled_patterns["direct_answer"]:
            direct_answer_count += len(pattern.findall(text))

        # Findings based on question/answer patterns
        if question_count == 0:
            findings.append(GEOFinding(
                metric=GEOMetric.ANSWERABILITY,
                severity="medium",
                title="No question patterns detected",
                description="The content doesn't contain clear question patterns that AI systems look for.",
                evidence={"question_count": 0},
                recommendation="Include question-based headings (FAQ format) or explicitly answer common questions.",
                impact_score=5.0,
            ))
            score -= 10
        elif question_count < 3:
            findings.append(GEOFinding(
                metric=GEOMetric.ANSWERABILITY,
                severity="low",
                title="Few question patterns",
                description=f"Only {question_count} question patterns found. More questions improve AI answerability.",
                evidence={"question_count": question_count},
                recommendation="Add FAQ sections or question-based headings to improve answerability.",
                impact_score=3.0,
            ))
            score -= 5

        if direct_answer_count == 0:
            findings.append(GEOFinding(
                metric=GEOMetric.ANSWERABILITY,
                severity="medium",
                title="No direct answer patterns",
                description="No clear definition or answer patterns found. AI systems prefer direct answers.",
                evidence={"direct_answer_count": 0},
                recommendation="Start sections with direct answers: 'X is...', 'To do Y, do...' patterns.",
                impact_score=5.0,
            ))
            score -= 10

        return {
            "score": max(0, min(100, score)),
            "findings": findings,
        }

    def _analyze_passage_citability(self, text: str) -> Dict[str, Any]:
        """Analyze if passages are citable by AI systems."""
        score = 50.0
        findings = []

        # Count paragraph length
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if len(p.strip()) > 50]
        short_paragraphs = [p for p in paragraphs if len(p) < 100]
        long_paragraphs = [p for p in paragraphs if len(p) > 1000]

        if not paragraphs:
            findings.append(GEOFinding(
                metric=GEOMetric.PASSAGE_CITABILITY,
                severity="high",
                title="No substantial paragraphs",
                description="Content lacks well-formed paragraphs. AI systems need citable passages.",
                evidence={"paragraph_count": 0},
                recommendation="Structure content into clear, substantive paragraphs (100+ words).",
                impact_score=6.0,
            ))
            score -= 20
        else:
            if len(short_paragraphs) / len(paragraphs) > 0.5:
                findings.append(GEOFinding(
                    metric=GEOMetric.PASSAGE_CITABILITY,
                    severity="medium",
                    title="Many short paragraphs",
                    description=f"{len(short_paragraphs)}/{len(paragraphs)} paragraphs are too short for citation.",
                    evidence={"total_paragraphs": len(paragraphs), "short_count": len(short_paragraphs)},
                    recommendation="Expand shorter paragraphs to provide citable context.",
                    impact_score=4.0,
                ))
                score -= 10

            if long_paragraphs:
                score += 5  # Bonus for substantial content

        # Check for standalone factual statements
        factual_patterns = re.findall(
            r'\b(?:is|are|was|were)\s+.{0,50}(?:a|an|the)\s+\w',
            text
        )
        if len(factual_patterns) < 5:
            findings.append(GEOFinding(
                metric=GEOMetric.PASSAGE_CITABILITY,
                severity="low",
                title="Limited factual statements",
                description="Few standalone factual statements found. AI systems cite factual passages.",
                evidence={"factual_count": len(factual_patterns)},
                recommendation="Include clear, factual statements that can be cited independently.",
                impact_score=3.0,
            ))
            score -= 5

        return {
            "score": max(0, min(100, score)),
            "findings": findings,
        }

    def _analyze_question_structure(self, text: str) -> Dict[str, Any]:
        """Analyze question-based content structure."""
        score = 50.0
        findings = []

        # Check for FAQ patterns
        faq_count = len(re.findall(r'(?i)\bfaq\b', text))
        question_headings = re.findall(r'(?i)<h[1-6]>.*?\?.*?</h[1-6]>', text)

        # Count question headings
        h_question_count = 0
        for heading in re.findall(r'(?i)<h[1-6]>(.*?)</h[1-6]>', text):
            if '?' in heading:
                h_question_count += 1

        if h_question_count == 0:
            findings.append(GEOFinding(
                metric=GEOMetric.QUESTION_STRUCTURE,
                severity="medium",
                title="No question-based headings",
                description="No headings ending with '?' found. Question headings help AI systems identify answerable content.",
                evidence={"question_headings": 0},
                recommendation="Use question-based headings: 'What is X?', 'How does Y work?'",
                impact_score=5.0,
            ))
            score -= 10
        elif h_question_count < 3:
            findings.append(GEOFinding(
                metric=GEOMetric.QUESTION_STRUCTURE,
                severity="low",
                title="Few question headings",
                description=f"Only {h_question_count} question-based heading(s) found.",
                evidence={"question_headings": h_question_count},
                recommendation="Add more question-based headings for better AI discoverability.",
                impact_score=3.0,
            ))
            score -= 5

        # Check for explicit FAQ section
        has_faq = faq_count > 0 or h_question_count >= 5
        if not has_faq:
            findings.append(GEOFinding(
                metric=GEOMetric.QUESTION_STRUCTURE,
                severity="low",
                title="No explicit FAQ section",
                description="FAQ sections are highly citable by AI systems.",
                evidence={"faq_mentions": faq_count, "question_headings": h_question_count},
                recommendation="Consider adding an FAQ section for frequently asked questions.",
                impact_score=3.0,
            ))
            score -= 5

        return {
            "score": max(0, min(100, score)),
            "findings": findings,
        }

    def _analyze_entity_clarity(self, text: str, html: Optional[str] = None) -> Dict[str, Any]:
        """Analyze entity clarity and consistency."""
        score = 50.0
        findings = []
        detected_entities: Dict[str, int] = {}

        # Detect entity types
        for entity_type, patterns in self.ENTITY_TYPES.items():
            count = 0
            for pattern in re.compile(patterns).findall(text):
                count += 1
            if count > 0:
                detected_entities[entity_type] = count

        if not detected_entities:
            findings.append(GEOFinding(
                metric=GEOMetric.ENTITY_CLARITY,
                severity="high",
                title="No clear entities detected",
                description="AI systems need clear entity identification for authoritative answers.",
                evidence={"detected_entities": {}},
                recommendation="Clearly identify your organization, products, people, and locations.",
                impact_score=6.0,
            ))
            score -= 15
        else:
            if len(detected_entities) < 2:
                findings.append(GEOFinding(
                    metric=GEOMetric.ENTITY_CLARITY,
                    severity="medium",
                    title="Limited entity types",
                    description=f"Only {len(detected_entities)} entity type(s) detected: {', '.join(detected_entities.keys())}",
                    evidence={"detected_entities": detected_entities},
                    recommendation="Include diverse entity types: organization, person, product, location.",
                    impact_score=4.0,
                ))
                score -= 10

        # Check entity consistency (simplified)
        if "organization" in detected_entities:
            org_count = detected_entities["organization"]
            if org_count < 3:
                findings.append(GEOFinding(
                    metric=GEOMetric.ENTITY_CLARITY,
                    severity="low",
                    title="Limited organization mentions",
                    description=f"Organization mentioned {org_count} time(s). More mentions improve entity clarity.",
                    evidence={"organization_mentions": org_count},
                    recommendation="Mention your organization consistently throughout content.",
                    impact_score=3.0,
                ))
                score -= 5

        return {
            "score": max(0, min(100, score)),
            "findings": findings,
        }

    def _analyze_attribution(self, text: str, html: Optional[str] = None) -> Dict[str, Any]:
        """Analyze attribution signals."""
        score = 50.0
        findings = []

        # Check trust signals
        trust_signals_found = []
        for pattern in self._compiled_patterns["trust"]:
            matches = re.findall(pattern, text)
            if matches:
                trust_signals_found.append(pattern.pattern)

        if len(trust_signals_found) == 0:
            findings.append(GEOFinding(
                metric=GEOMetric.ATTRIBUTION,
                severity="high",
                title="No trust signals detected",
                description="No attribution or trust signals found. AI systems prioritize authoritative sources.",
                evidence={"trust_signals": []},
                recommendation="Add author information, publication dates, citations, and contact info.",
                impact_score=6.0,
            ))
            score -= 15
        elif len(trust_signals_found) < 3:
            findings.append(GEOFinding(
                metric=GEOMetric.ATTRIBUTION,
                severity="medium",
                title="Limited trust signals",
                description=f"Only {len(trust_signals_found)} trust signal(s) found.",
                evidence={"trust_signals": trust_signals_found},
                recommendation="Add more attribution: author bio, dates, citations, contact information.",
                impact_score=5.0,
            ))
            score -= 10

        # Check for dates
        date_patterns = re.findall(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b', text)
        if not date_patterns:
            findings.append(GEOFinding(
                metric=GEOMetric.ATTRIBUTION,
                severity="low",
                title="No publication dates found",
                description="Publication dates help AI systems assess content freshness.",
                evidence={"dates_found": 0},
                recommendation="Add clear publication and update dates.",
                impact_score=3.0,
            ))
            score -= 5

        return {
            "score": max(0, min(100, score)),
            "findings": findings,
        }

    def _analyze_structured_content(self, text: str, html: Optional[str] = None) -> Dict[str, Any]:
        """Analyze content structure for AI readability."""
        score = 50.0
        findings = []

        if not html:
            return {"score": score, "findings": findings}

        # Count headings
        h1_count = len(re.findall(r'<h1[^>]*>', html, re.I))
        h2_count = len(re.findall(r'<h2[^>]*>', html, re.I))
        h3_count = len(re.findall(r'<h3[^>]*>', html, re.I))

        # Check heading hierarchy
        if h1_count == 0:
            findings.append(GEOFinding(
                metric=GEOMetric.STRUCTURED_CONTENT,
                severity="medium",
                title="No H1 heading",
                description="H1 helps AI systems understand the main topic.",
                evidence={"h1_count": 0},
                recommendation="Add a single H1 heading that describes the page topic.",
                impact_score=4.0,
            ))
            score -= 10
        elif h1_count > 1:
            findings.append(GEOFinding(
                metric=GEOMetric.STRUCTURED_CONTENT,
                severity="low",
                title="Multiple H1 headings",
                description=f"Found {h1_count} H1 headings. Use a single H1 for clarity.",
                evidence={"h1_count": h1_count},
                recommendation="Use only one H1 per page.",
                impact_score=2.0,
            ))
            score -= 5

        # Check for lists
        list_count = len(re.findall(r'<(?:ul|ol|dl)[^>]*>', html, re.I))
        if list_count == 0:
            findings.append(GEOFinding(
                metric=GEOMetric.STRUCTURED_CONTENT,
                severity="low",
                title="No lists found",
                description="Lists are highly citable by AI systems.",
                evidence={"list_count": 0},
                recommendation="Use lists for step-by-step instructions or enumerations.",
                impact_score=3.0,
            ))
            score -= 5

        # Check for tables
        table_count = len(re.findall(r'<table[^>]*>', html, re.I))
        if table_count > 0:
            score += 5  # Bonus for tables

        # Check for definition patterns
        def_count = len(re.findall(r'<dt[^>]*>', html, re.I))
        if def_count == 0 and list_count < 2:
            score -= 3

        return {
            "score": max(0, min(100, score)),
            "findings": findings,
        }


def analyze_geo(page_text: str, html: Optional[str] = None) -> GEOAnalysis:
    """Convenience function for GEO analysis."""
    service = GEOAnalysisService()
    return service.analyze(page_text, html)
