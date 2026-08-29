"""E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) analysis service.

Analyzes content quality signals that search engines use to evaluate page quality.
All metrics are evidence-based with transparent scoring.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import re


class EEAATDimension(str, Enum):
    """E-E-A-T dimensions."""
    EXPERIENCE = "experience"
    EXPERTISE = "expertise"
    AUTHORITATIVENESS = "authoritativeness"
    TRUSTWORTHINESS = "trustworthiness"
    TOPICAL_DEPTH = "topical_depth"


@dataclass
class EEAATFinding:
    """An E-E-A-T analysis finding."""
    dimension: EEAATDimension
    severity: str  # critical, high, medium, low, pass
    title: str
    description: str
    evidence: Dict[str, Any]
    recommendation: str
    impact_score: float


@dataclass
class EEAATAnalysis:
    """Complete E-E-A-T analysis for a page."""
    url: str
    dimensions: Dict[EEAATDimension, float]  # 0-100 scores
    findings: List[EEAATFinding] = field(default_factory=list)

    @property
    def overall_score(self) -> float:
        """Weighted overall E-E-A-T score."""
        weights = {
            EEAATDimension.EXPERIENCE: 0.15,
            EEAATDimension.EXPERTISE: 0.25,
            EEAATDimension.AUTHORITATIVENESS: 0.20,
            EEAATDimension.TRUSTWORTHINESS: 0.25,
            EEAATDimension.TOPICAL_DEPTH: 0.15,
        }
        total = 0.0
        weight_total = 0.0
        for dim, score in self.dimensions.items():
            weight = weights.get(dim, 0.2)
            total += score * weight
            weight_total += weight
        return round(total / weight_total, 1) if weight_total > 0 else 0.0


class EEAATAnalysisService:
    """Service for analyzing E-E-A-T signals in content."""

    # First-person experience signals
    EXPERIENCE_SIGNALS = [
        r"(?i)\bI\s+(?:learned|experienced|found|discovered)\b",
        r"(?i)\bwe\s+(?:found|experienced|learned)\b",
        r"(?i)\bour\s+(?:experience|team|expertise)\b",
        r"(?i)\bfrom\s+(?:personal|hands?[-\s]?on)\s+experience\b",
        r"(?i)\bin\s+(?:my|our)\s+(?:experience|practice)\b",
        r"(?i)\bwhen\s+(?:I|we)\s+(?:tried|tested|used)\b",
        r"(?i)\bas\s+(?:a\s+)?(?:professional|expert|practitioner)\b",
    ]

    # Expertise signals
    EXPERTISE_SIGNALS = [
        r"(?i)\b(?:Ph\.?D\.?|M\.?D\.?|Esq\.?|CPA|CISSP|P\.?MP|AWS|Azure|Google\s+Certified)\b",
        r"(?i)\b(?:credentials?|qualifications?|certifications?|licenses?)\b",
        r"(?i)\b(?:board\s+certified|licensed\s+(?:attorney|doctor|engineer))\b",
        r"(?i)\b(?:years?\s+of\s+(?:experience|practice))\b",
        r"(?i)\b(?:academic|researcher|scholar|professor)\b",
        r"(?i)\b(?:published\s+work|peer[-\s]?reviewed)\b",
    ]

    # Authority signals
    AUTHORITY_SIGNALS = [
        r"(?i)\bas\s+(?:cited|referenced|quoted)\s+by\b",
        r"(?i)\bfeatured\s+in\s+(?: Forbes|CNN|BBC|NYT|WSJ|TechCrunch)\b",
        r"(?i)\b(?:according\s+to|based\s+on)\s+(?:study|research|report)\b",
        r"(?i)\b(?:sources?|references?|bibliography)\b",
        r"(?i)\b(?:citation|cited|reference)\b",
        r"(?i)\b(?:linking\s+to|linked\s+from)\s+(?:gov|edu)\b",
    ]

    # Trust signals
    TRUST_SIGNALS = [
        r"(?i)\b(?:secure|SSL|HTTPS|encrypted)\b",
        r"(?i)\b(?:contact\s+(?:us|info|page)|about\s+us)\b",
        r"(?i)\b(?:privacy\s+policy|terms\s+of\s+service|cookie\s+policy)\b",
        r"(?i)\b(?:editorial\s+policy|correction\s+policy|fact[-\s]?check)\b",
        r"(?i)\b(?:money[-\s]?back\s+guarantee|satisfaction\s+guarantee)\b",
        r"(?i)\b(?:trusted\s+by|as\s+seen\s+on)\b",
    ]

    # Author information patterns
    AUTHOR_PATTERNS = [
        r"(?i)\bby\s+(?:[A-Z][a-z]+\s+[A-Z][a-z]+)\b",
        r"(?i)\bauthor(?:\s*(?:bio|profile|page))?\b",
        r"(?i)\bwritten\s+by\b",
        r"(?i)\bcontributed\s+by\b",
        r"(?i)\bguest\s+post\s+by\b",
    ]

    def __init__(self):
        self._compiled_patterns = {
            "experience": [re.compile(p) for p in self.EXPERIENCE_SIGNALS],
            "expertise": [re.compile(p) for p in self.EXPERTISE_SIGNALS],
            "authority": [re.compile(p) for p in self.AUTHORITY_SIGNALS],
            "trust": [re.compile(p) for p in self.TRUST_SIGNALS],
            "author": [re.compile(p) for p in self.AUTHOR_PATTERNS],
        }

    def analyze(self, text: str, html: Optional[str] = None) -> EEAATAnalysis:
        """Analyze content for E-E-A-T signals."""
        findings: List[EEAATFinding] = []
        dimensions: Dict[EEAATDimension, float] = {}

        # Experience analysis
        experience = self._analyze_experience(text)
        dimensions[EEAATDimension.EXPERIENCE] = experience["score"]
        findings.extend(experience["findings"])

        # Expertise analysis
        expertise = self._analyze_expertise(text, html)
        dimensions[EEAATDimension.EXPERTISE] = expertise["score"]
        findings.extend(expertise["findings"])

        # Authoritativeness analysis
        authority = self._analyze_authoritativeness(text, html)
        dimensions[EEAATDimension.AUTHORITATIVENESS] = authority["score"]
        findings.extend(authority["findings"])

        # Trustworthiness analysis
        trust = self._analyze_trustworthiness(text, html)
        dimensions[EEAATDimension.TRUSTWORTHINESS] = trust["score"]
        findings.extend(trust["findings"])

        # Topical depth analysis
        depth = self._analyze_topical_depth(text, html)
        dimensions[EEAATDimension.TOPICAL_DEPTH] = depth["score"]
        findings.extend(depth["findings"])

        return EEAATAnalysis(
            url="",
            dimensions=dimensions,
            findings=findings,
        )

    def _analyze_experience(self, text: str) -> Dict[str, Any]:
        """Analyze first-hand experience signals."""
        score = 30.0  # Start low - experience is rare
        findings = []

        # Count experience signals
        experience_count = 0
        for pattern in self._compiled_patterns["experience"]:
            experience_count += len(pattern.findall(text))

        if experience_count >= 3:
            score += 40
            findings.append(EEAATFinding(
                dimension=EEAATDimension.EXPERIENCE,
                severity="pass",
                title="Strong first-hand experience signals",
                description=f"Found {experience_count} first-hand experience indicators.",
                evidence={"experience_count": experience_count},
                recommendation="Maintain this level of personal experience in content.",
                impact_score=0.0,
            ))
        elif experience_count >= 1:
            score += 20
            findings.append(EEAATFinding(
                dimension=EEAATDimension.EXPERIENCE,
                severity="low",
                title="Some first-hand experience signals",
                description=f"Found {experience_count} experience indicator(s).",
                evidence={"experience_count": experience_count},
                recommendation="Add more personal experience and case studies.",
                impact_score=3.0,
            ))
        else:
            findings.append(EEAATFinding(
                dimension=EEAATDimension.EXPERIENCE,
                severity="medium",
                title="No first-hand experience signals",
                description="Content lacks personal experience indicators. First-hand experience builds trust.",
                evidence={"experience_count": 0},
                recommendation="Include case studies, personal anecdotes, or first-hand accounts.",
                impact_score=5.0,
            ))

        return {"score": min(100, score), "findings": findings}

    def _analyze_expertise(self, text: str, html: Optional[str] = None) -> Dict[str, Any]:
        """Analyze expertise signals."""
        score = 30.0
        findings = []

        # Count expertise signals
        expertise_count = 0
        for pattern in self._compiled_patterns["expertise"]:
            expertise_count += len(pattern.findall(text))

        if expertise_count >= 2:
            score += 40
            findings.append(EEAATFinding(
                dimension=EEAATDimension.EXPERTISE,
                severity="pass",
                title="Strong expertise signals",
                description=f"Found {expertise_count} expertise indicators (credentials, certifications).",
                evidence={"expertise_count": expertise_count},
                recommendation="Maintain clear expertise demonstration.",
                impact_score=0.0,
            ))
        elif expertise_count >= 1:
            score += 20
            findings.append(EEAATFinding(
                dimension=EEAATDimension.EXPERTISE,
                severity="low",
                title="Some expertise signals",
                description=f"Found {expertise_count} expertise indicator(s).",
                evidence={"expertise_count": expertise_count},
                recommendation="Add more credentials and qualifications.",
                impact_score=3.0,
            ))
        else:
            findings.append(EEAATFinding(
                dimension=EEAATDimension.EXPERTISE,
                severity="medium",
                title="No expertise signals detected",
                description="Content lacks credentials, certifications, or qualifications.",
                evidence={"expertise_count": 0},
                recommendation="Include author credentials, certifications, or professional qualifications.",
                impact_score=5.0,
            ))

        # Check for author bio in HTML
        if html:
            has_author_bio = bool(re.search(r'(?i)author\s*(?:bio|profile|about)', html))
            if has_author_bio:
                score += 10
            else:
                findings.append(EEAATFinding(
                    dimension=EEAATDimension.EXPERTISE,
                    severity="low",
                    title="No author bio found",
                    description="Author biography helps establish expertise.",
                    evidence={"has_author_bio": False},
                    recommendation="Add an author bio with relevant qualifications.",
                    impact_score=2.0,
                ))

        return {"score": min(100, score), "findings": findings}

    def _analyze_authoritativeness(self, text: str, html: Optional[str] = None) -> Dict[str, Any]:
        """Analyze authority signals."""
        score = 30.0
        findings = []

        # Count authority signals
        authority_count = 0
        for pattern in self._compiled_patterns["authority"]:
            authority_count += len(pattern.findall(text))

        if authority_count >= 2:
            score += 40
            findings.append(EEAATFinding(
                dimension=EEAATDimension.AUTHORITATIVENESS,
                severity="pass",
                title="Strong authority signals",
                description=f"Found {authority_count} authority indicators (citations, features).",
                evidence={"authority_count": authority_count},
                recommendation="Maintain strong citation and reference practices.",
                impact_score=0.0,
            ))
        elif authority_count >= 1:
            score += 20
            findings.append(EEAATFinding(
                dimension=EEAATDimension.AUTHORITATIVENESS,
                severity="low",
                title="Some authority signals",
                description=f"Found {authority_count} authority indicator(s).",
                evidence={"authority_count": authority_count},
                recommendation="Add more citations and references to authoritative sources.",
                impact_score=3.0,
            ))
        else:
            findings.append(EEAATFinding(
                dimension=EEAATDimension.AUTHORITATIVENESS,
                severity="medium",
                title="No authority signals detected",
                description="Content lacks citations, references, or mentions by authoritative sources.",
                evidence={"authority_count": 0},
                recommendation="Cite authoritative sources and studies. Include references.",
                impact_score=5.0,
            ))

        # Check for external links to .gov/.edu
        if html:
            gov_links = len(re.findall(r'(?i)\.gov[^"]*href', html))
            edu_links = len(re.findall(r'(?i)\.edu[^"]*href', html))
            if gov_links + edu_links >= 1:
                score += 10
            else:
                findings.append(EEAATFinding(
                    dimension=EEAATDimension.AUTHORITATIVENESS,
                    severity="low",
                    title="No .gov or .edu references",
                    description="Links to government or educational sites add authority.",
                    evidence={"gov_links": gov_links, "edu_links": edu_links},
                    recommendation="Reference authoritative sources like .gov and .edu domains.",
                    impact_score=2.0,
                ))

        return {"score": min(100, score), "findings": findings}

    def _analyze_trustworthiness(self, text: str, html: Optional[str] = None) -> Dict[str, Any]:
        """Analyze trust signals."""
        score = 30.0
        findings = []

        # Count trust signals
        trust_count = 0
        for pattern in self._compiled_patterns["trust"]:
            trust_count += len(pattern.findall(text))

        if trust_count >= 3:
            score += 40
            findings.append(EEAATFinding(
                dimension=EEAATDimension.TRUSTWORTHINESS,
                severity="pass",
                title="Strong trust signals",
                description=f"Found {trust_count} trust indicators (privacy, contact, guarantees).",
                evidence={"trust_count": trust_count},
                recommendation="Maintain strong trust practices.",
                impact_score=0.0,
            ))
        elif trust_count >= 1:
            score += 20
            findings.append(EEAATFinding(
                dimension=EEAATDimension.TRUSTWORTHINESS,
                severity="low",
                title="Some trust signals",
                description=f"Found {trust_count} trust indicator(s).",
                evidence={"trust_count": trust_count},
                recommendation="Add more trust signals: contact info, privacy policy, guarantees.",
                impact_score=3.0,
            ))
        else:
            findings.append(EEAATFinding(
                dimension=EEAATDimension.TRUSTWORTHINESS,
                severity="high",
                title="No trust signals detected",
                description="Content lacks trust indicators like contact info, privacy policy, or guarantees.",
                evidence={"trust_count": 0},
                recommendation="Add contact information, privacy policy, terms of service, and trust badges.",
                impact_score=6.0,
            ))

        # Check for HTTPS (from URL)
        if html:
            has_ssl = "https" in html.lower()[:500]
            if has_ssl:
                score += 5
            else:
                findings.append(EEAATFinding(
                    dimension=EEAATDimension.TRUSTWORTHINESS,
                    severity="medium",
                    title="No HTTPS signal detected",
                    description="SSL/HTTPS is a basic trust requirement.",
                    evidence={"has_https": False},
                    recommendation="Ensure site uses HTTPS.",
                    impact_score=4.0,
                ))

        return {"score": min(100, score), "findings": findings}

    def _analyze_topical_depth(self, text: str, html: Optional[str] = None) -> Dict[str, Any]:
        """Analyze topical coverage and depth."""
        score = 40.0  # Base score for having content
        findings = []

        # Word count analysis
        word_count = len(text.split())
        if word_count >= 2000:
            score += 30
            findings.append(EEAATFinding(
                dimension=EEAATDimension.TOPICAL_DEPTH,
                severity="pass",
                title="Comprehensive content depth",
                description=f"Content has {word_count} words, indicating thorough coverage.",
                evidence={"word_count": word_count},
                recommendation="Maintain this level of content depth.",
                impact_score=0.0,
            ))
        elif word_count >= 1000:
            score += 15
            findings.append(EEAATFinding(
                dimension=EEAATDimension.TOPICAL_DEPTH,
                severity="pass",
                title="Good content depth",
                description=f"Content has {word_count} words.",
                evidence={"word_count": word_count},
                recommendation="Consider expanding for more comprehensive coverage.",
                impact_score=0.0,
            ))
        elif word_count >= 500:
            score += 5
            findings.append(EEAATFinding(
                dimension=EEAATDimension.TOPICAL_DEPTH,
                severity="medium",
                title="Moderate content depth",
                description=f"Content has {word_count} words. Consider expanding for better topical coverage.",
                evidence={"word_count": word_count},
                recommendation="Expand content to at least 1000 words for comprehensive coverage.",
                impact_score=4.0,
            ))
        else:
            score -= 10
            findings.append(EEAATFinding(
                dimension=EEAATDimension.TOPICAL_DEPTH,
                severity="high",
                title="Thin content",
                description=f"Content has only {word_count} words. This is considered thin content.",
                evidence={"word_count": word_count},
                recommendation="Expand content significantly. Aim for 1000+ words for comprehensive coverage.",
                impact_score=6.0,
            ))

        # Check for related topics coverage
        if html:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3']) if h.get_text(strip=True)]

            if len(headings) >= 5:
                score += 5
            elif len(headings) < 3:
                findings.append(EEAATFinding(
                    dimension=EEAATDimension.TOPICAL_DEPTH,
                    severity="low",
                    title="Limited content structure",
                    description=f"Only {len(headings)} headings found. More structure helps demonstrate depth.",
                    evidence={"heading_count": len(headings)},
                    recommendation="Add more subheadings to structure content and demonstrate depth.",
                    impact_score=2.0,
                ))

        return {"score": max(0, min(100, score)), "findings": findings}


def analyze_eeat(text: str, html: Optional[str] = None) -> EEAATAnalysis:
    """Convenience function for E-E-A-T analysis."""
    service = EEAATAnalysisService()
    return service.analyze(text, html)
