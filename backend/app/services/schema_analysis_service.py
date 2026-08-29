"""Schema.org analysis service.

Detects, parses, validates, and suggests structured data improvements.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import re
import json


class SchemaType(str, Enum):
    """Common Schema.org types to detect."""
    ARTICLE = "Article"
    ORGANIZATION = "Organization"
    PERSON = "Person"
    PRODUCT = "Product"
    SERVICE = "Service"
    FAQ_PAGE = "FAQPage"
    HOW_TO = "HowTo"
    REVIEW = "Review"
    LOCAL_BUSINESS = "LocalBusiness"
    WEB_PAGE = "WebPage"
    WEB_SITE = "Website"
    BREADCRUMB_LIST = "BreadcrumbList"
    IMAGE_OBJECT = "ImageObject"
    VIDEO_OBJECT = "VideoObject"
    EVENT = "Event"
    JOB_POSTING = "JobPosting"


class SchemaSeverity(str, Enum):
    """Severity levels for schema findings."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    PASS = "pass"


@dataclass
class SchemaFinding:
    """A schema analysis finding."""
    severity: SchemaSeverity
    title: str
    description: str
    evidence: Dict[str, Any]
    recommendation: str
    impact_score: float


@dataclass
class SchemaBlock:
    """A parsed structured data block."""
    type: str
    properties: Dict[str, Any]
    valid: bool = True
    errors: List[str] = field(default_factory=list)


@dataclass
class SchemaAnalysis:
    """Complete schema analysis for a page."""
    url: str
    blocks: List[SchemaBlock] = field(default_factory=list)
    findings: List[SchemaFinding] = field(default_factory=list)
    score: float = 50.0  # 0-100

    @property
    def types_found(self) -> List[str]:
        return [b.type for b in self.blocks]

    @property
    def has_errors(self) -> bool:
        return any(not b.valid for b in self.blocks)


# Required properties for common types
REQUIRED_PROPERTIES = {
    "Article": ["headline", "author", "datePublished"],
    "Organization": ["name", "@type"],
    "Person": ["name", "@type"],
    "Product": ["name", "@type", "offers"],
    "FAQPage": ["mainEntity"],
    "HowTo": ["name", "step", "@type"],
    "LocalBusiness": ["name", "@type", "address"],
    "Review": ["author", "reviewBody", "rating"],
    "WebPage": ["@type"],
}

# Recommended properties for common types
RECOMMENDED_PROPERTIES = {
    "Article": ["image", "publisher", "description", "wordCount"],
    "Organization": ["url", "logo", "sameAs"],
    "Person": ["jobTitle", "url", "image"],
    "Product": ["description", "image", "brand", "aggregateRating"],
    "FAQPage": ["name"],
    "HowTo": ["description", "image", "totalTime"],
    "LocalBusiness": ["telephone", "priceRange", "openingHours", "geo"],
}


class SchemaAnalysisService:
    """Service for analyzing Schema.org structured data."""

    def __init__(self):
        self._type_patterns = {
            type_name: re.compile(rf'(?i)@"type"\s*:\s*"({type_name})"', re.I)
            for type_name in SchemaType
        }

    def analyze(self, html: str, url: str = "") -> SchemaAnalysis:
        """Analyze HTML for schema.org structured data."""
        analysis = SchemaAnalysis(url=url)

        # Extract JSON-LD
        json_ld_blocks = self._extract_json_ld(html)
        for block_data in json_ld_blocks:
            schema_block = self._parse_schema_block(block_data)
            analysis.blocks.append(schema_block)

        # Extract Microdata
        microdata_blocks = self._extract_microdata(html)
        for block_data in microdata_blocks:
            schema_block = self._parse_schema_block(block_data)
            analysis.blocks.append(schema_block)

        # Generate findings
        analysis.findings = self._generate_findings(analysis)

        # Calculate score
        analysis.score = self._calculate_score(analysis)

        return analysis

    def _extract_json_ld(self, html: str) -> List[Dict[str, Any]]:
        """Extract JSON-LD structured data from HTML."""
        blocks = []
        pattern = re.compile(r'<script\s+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.DOTALL)

        for match in pattern.finditer(html):
            try:
                data = json.loads(match.group(1).strip())
                if isinstance(data, dict):
                    blocks.append(data)
                elif isinstance(data, list):
                    blocks.extend(data)
            except json.JSONDecodeError:
                continue

        return blocks

    def _extract_microdata(self, html: str) -> List[Dict[str, Any]]:
        """Extract microdata structured data from HTML."""
        blocks = []
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")

        # Find itemscope elements
        for item in soup.find_all("div", itemscope=True):
            block = {"@context": "http://schema.org", "@type": []}
            itemtype = item.get("itemtype", "")
            if itemtype:
                block["@type"] = itemtype.split("#")[-1] if "#" in itemtype else itemtype.split("/")[-1]

            # Extract properties
            for prop in item.find_all(True):
                prop_name = prop.get("itemprop", "")
                if prop_name:
                    prop_value = prop.get_text(strip=True)
                    if prop_value:
                        if prop_name in block:
                            if isinstance(block[prop_name], list):
                                block[prop_name].append(prop_value)
                            else:
                                block[prop_name] = [block[prop_name], prop_value]
                        else:
                            block[prop_name] = prop_value

            if block["@type"]:
                blocks.append(block)

        return blocks

    def _parse_schema_block(self, data: Dict[str, Any]) -> SchemaBlock:
        """Parse a structured data block and validate it."""
        block = SchemaBlock(
            type=data.get("@type", "Unknown"),
            properties={k: v for k, v in data.items() if k not in ("@context", "@type")},
        )

        # Validate required properties
        entity_type = block.type
        if entity_type in REQUIRED_PROPERTIES:
            required = REQUIRED_PROPERTIES[entity_type]
            missing = [p for p in required if p not in block.properties and not self._has_nested_property(block.properties, p)]
            if missing:
                block.valid = False
                block.errors.extend([f"Missing required property: {p}" for p in missing])

        return block

    def _has_nested_property(self, props: Dict[str, Any], prop_name: str) -> bool:
        """Check if a property exists in nested structure."""
        if prop_name in props:
            return True
        for value in props.values():
            if isinstance(value, dict):
                if self._has_nested_property(value, prop_name):
                    return True
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and self._has_nested_property(item, prop_name):
                        return True
        return False

    def _generate_findings(self, analysis: SchemaAnalysis) -> List[SchemaFinding]:
        """Generate findings based on schema analysis."""
        findings = []

        if not analysis.blocks:
            findings.append(SchemaFinding(
                severity=SchemaSeverity.MEDIUM,
                title="No structured data found",
                description="The page does not contain any Schema.org structured data. This helps search engines understand content.",
                evidence={"block_count": 0},
                recommendation="Add JSON-LD structured data using common types like Article, Organization, or FAQPage.",
                impact_score=5.0,
            ))
            return findings

        # Check for errors
        for block in analysis.blocks:
            if not block.valid:
                findings.append(SchemaFinding(
                    severity=SchemaSeverity.HIGH,
                    title=f"Invalid {block.type} schema",
                    description=f"Schema block has validation errors: {', '.join(block.errors[:3])}",
                    evidence={"type": block.type, "errors": block.errors},
                    recommendation="Fix the schema errors to ensure proper search engine interpretation.",
                    impact_score=6.0,
                ))

        # Check for recommended properties
        for block in analysis.blocks:
            entity_type = block.type
            if entity_type in RECOMMENDED_PROPERTIES:
                missing_recommended = [
                    p for p in RECOMMENDED_PROPERTIES[entity_type]
                    if p not in block.properties
                ]
                if missing_recommended:
                    findings.append(SchemaFinding(
                        severity=SchemaSeverity.LOW,
                        title=f"Missing recommended {entity_type} properties",
                        description=f"Consider adding: {', '.join(missing_recommended[:3])}",
                        evidence={"type": entity_type, "missing": missing_recommended},
                        recommendation="Add recommended properties for richer search results.",
                        impact_score=2.0,
                    ))

        # Check for FAQPage specifically
        has_faq = any(b.type == "FAQPage" for b in analysis.blocks)
        if not has_faq:
            findings.append(SchemaFinding(
                severity=SchemaSeverity.LOW,
                title="No FAQPage schema",
                description="FAQPage schema can enable rich results in search.",
                evidence={"has_faq": False},
                recommendation="Add FAQPage structured data if the page contains questions and answers.",
                impact_score=3.0,
            ))

        return findings

    def _calculate_score(self, analysis: SchemaAnalysis) -> float:
        """Calculate schema analysis score."""
        score = 50.0

        if not analysis.blocks:
            return max(0, score - 15)

        # Bonus for having schema
        score += 20

        # Penalty for errors
        error_count = sum(1 for b in analysis.blocks if not b.valid)
        score -= error_count * 10

        # Bonus for FAQPage
        if any(b.type == "FAQPage" for b in analysis.blocks):
            score += 10

        # Bonus for complete Organization schema
        org_blocks = [b for b in analysis.blocks if b.type == "Organization"]
        if org_blocks and all(b.valid for b in org_blocks):
            score += 5

        return max(0, min(100, score))

    def suggest_schema(self, page_type: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest schema.org markup for a given page type."""
        suggestions = {
            "Article": {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": content.get("headline", "[Your headline]"),
                "description": content.get("description", "[Your description]"),
                "image": content.get("image", "[Your image URL]"),
                "author": {
                    "@type": "Person",
                    "name": content.get("author", "[Author name]"),
                },
                "publisher": {
                    "@type": "Organization",
                    "name": content.get("publisher", "[Publisher name]"),
                    "logo": {
                        "@type": "ImageObject",
                        "url": content.get("logo", "[Logo URL]"),
                    },
                },
                "datePublished": content.get("date", "[Publication date]"),
                "dateModified": content.get("modified_date", "[Last modified date]"),
            },
            "FAQPage": {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": "[Your question here]",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "[Your answer here]",
                        },
                    }
                ],
            },
            "Organization": {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": content.get("name", "[Organization name]"),
                "url": content.get("url", "[Website URL]"),
                "logo": {
                    "@type": "ImageObject",
                    "url": content.get("logo", "[Logo URL]"),
                },
                "sameAs": content.get("social_links", ["[Social media URLs]"]),
            },
        }
        return suggestions.get(page_type, {"@context": "https://schema.org", "@type": page_type})


def analyze_schema(html: str, url: str = "") -> SchemaAnalysis:
    """Convenience function for schema analysis."""
    service = SchemaAnalysisService()
    return service.analyze(html, url)
