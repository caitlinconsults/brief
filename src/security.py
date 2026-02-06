"""Security and containment for Brief (spec 003).

Sanitizes content before it reaches the LLM, validates LLM outputs,
and verifies link safety.
"""

import re
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Common prompt injection patterns to strip from content before LLM processing
INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?previous\s+instructions",
    r"(?i)ignore\s+(all\s+)?above\s+instructions",
    r"(?i)disregard\s+(all\s+)?previous",
    r"(?i)forget\s+(all\s+)?prior",
    r"(?i)you\s+are\s+now\s+a",
    r"(?i)new\s+instructions?:",
    r"(?i)system\s*prompt:",
    r"(?i)<\s*system\s*>",
    r"(?i)<\s*/?\s*instructions?\s*>",
    r"(?i)respond\s+with\s+only",
    r"(?i)output\s+only\s+the\s+following",
    r"(?i)do\s+not\s+follow\s+any\s+other",
]

COMPILED_PATTERNS = [re.compile(p) for p in INJECTION_PATTERNS]

# Known source domains for link verification
SOURCE_DOMAINS = {
    "simon-willison": ["simonwillison.net"],
    "hacker-news": ["news.ycombinator.com", "ycombinator.com"],
    "latent-space": ["latent.space", "www.latent.space"],
    "langchain": ["blog.langchain.dev", "langchain.dev"],
    "lilian-weng": ["lilianweng.github.io"],
    "trail-of-bits": ["blog.trailofbits.com", "trailofbits.com"],
    "shreyas-doshi": ["shreyas.substack.com"],
    "lennys-newsletter": ["lennysnewsletter.com", "www.lennysnewsletter.com"],
    "not-boring": ["notboring.co", "www.notboring.co"],
    "a16z": ["a16z.com", "www.a16z.com"],
    "yc-blog": ["ycombinator.com", "www.ycombinator.com"],
    "anthropic-safety": ["anthropic.com", "www.anthropic.com"],
    "salesforce-eng": ["engineering.salesforce.com"],
}


def sanitize_content(text, source_slug=None):
    """Strip known injection patterns from content before LLM processing.

    Returns (sanitized_text, flags) where flags is a list of detected patterns.
    """
    if not text:
        return text, []

    flags = []
    sanitized = text

    for pattern in COMPILED_PATTERNS:
        matches = pattern.findall(sanitized)
        if matches:
            flags.append(f"Detected pattern: {pattern.pattern[:50]}")
            sanitized = pattern.sub("[REDACTED]", sanitized)

    if flags:
        logger.warning(
            "Content from %s had %d injection pattern(s) stripped",
            source_slug or "unknown", len(flags)
        )

    return sanitized, flags


def validate_enrichment(enrichment):
    """Validate LLM enrichment output against expected formats.

    Returns (is_valid, cleaned_enrichment, errors).
    """
    errors = []
    cleaned = {}

    # Summary short: should be text, under 500 chars
    summary_short = enrichment.get("summary_short", "")
    if not isinstance(summary_short, str) or not summary_short.strip():
        errors.append("Missing or invalid summary_short")
        cleaned["summary_short"] = ""
    elif len(summary_short) > 500:
        cleaned["summary_short"] = summary_short[:500]
    else:
        cleaned["summary_short"] = summary_short

    # Summary long: should be text, under 2000 chars
    summary_long = enrichment.get("summary_long", "")
    if not isinstance(summary_long, str):
        errors.append("Invalid summary_long type")
        cleaned["summary_long"] = ""
    elif len(summary_long) > 2000:
        cleaned["summary_long"] = summary_long[:2000]
    else:
        cleaned["summary_long"] = summary_long

    # Topics: should be a list of strings
    topics = enrichment.get("topics", [])
    if not isinstance(topics, list):
        errors.append("Topics is not a list")
        cleaned["topics"] = []
    else:
        cleaned["topics"] = [t for t in topics if isinstance(t, str)]

    # Entities: should be a list of dicts with name and type
    entities = enrichment.get("entities", [])
    if not isinstance(entities, list):
        errors.append("Entities is not a list")
        cleaned["entities"] = []
    else:
        valid_entities = []
        for e in entities:
            if isinstance(e, dict) and "name" in e:
                valid_entities.append({
                    "name": str(e["name"]),
                    "type": str(e.get("type", "unknown"))
                })
        cleaned["entities"] = valid_entities

    # Lane scores: must be floats between 0 and 1
    for lane in ["lane_builders", "lane_security", "lane_business"]:
        score = enrichment.get(lane, 0.0)
        try:
            score = float(score)
            score = max(0.0, min(1.0, score))
        except (TypeError, ValueError):
            errors.append(f"Invalid {lane} score: {score}")
            score = 0.0
        cleaned[lane] = score

    is_valid = len(errors) == 0
    if errors:
        logger.warning("Enrichment validation errors: %s", errors)

    return is_valid, cleaned, errors


def verify_url(url, source_slug):
    """Check that a URL's domain matches the expected source domain."""
    if not url or source_slug not in SOURCE_DOMAINS:
        return True  # can't verify, allow through

    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    expected = SOURCE_DOMAINS[source_slug]
    for expected_domain in expected:
        if domain == expected_domain or domain.endswith("." + expected_domain):
            return True

    logger.warning(
        "URL domain mismatch for %s: expected %s, got %s (%s)",
        source_slug, expected, domain, url
    )
    return False
