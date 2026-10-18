"""Explainable NLP baseline for triaging prospective-customer inquiries.

Service matching combines TF-IDF cosine similarity with exact, boundary-aware
keyword evidence. Discovery checks are explicit rules. This is a transparent
baseline: it does not call a generative model, train a classifier, or use an
external API.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SERVICE_CATALOG: dict[str, dict[str, Any]] = {
    "AI automation & agents": {
        "description": "AI agents, LLM applications, workflow automation, voice agents, repetitive task automation, autonomous business processes",
        "keywords": [
            "ai agent", "automation", "automate", "automated", "workflow",
            "manual", "voice agent", "voice", "repetitive", "llm",
        ],
    },
    "Document processing": {
        "description": "Document understanding, PDF and invoice processing, data extraction, forms, OCR, document classification and structured data capture",
        "keywords": [
            "document", "pdf", "extract", "extraction", "invoice",
            "form", "ocr", "data entry", "vendor",
        ],
    },
    "Custom software & SaaS": {
        "description": "Custom web applications, portals, dashboards, SaaS platforms, backend development, system integration, APIs and software engineering",
        "keywords": [
            "portal", "dashboard", "application", "app", "integration",
            "integrate", "integrated", "platform", "backend", "software",
            "system", "api",
        ],
    },
    "CRM & lead automation": {
        "description": "Customer relationship management, lead qualification, lead routing, sales pipelines, inquiry handling, prospect management and CRM workflow automation",
        "keywords": [
            "crm", "lead", "leads", "enquiry", "enquiries", "inquiry",
            "inquiries", "prospect", "sales", "pipeline",
            "customer relationship",
        ],
    },
    "Digital marketing & SEO": {
        "description": "Search engine optimization, SEO, landing pages, marketing funnels, organic traffic, paid ads, campaign performance and qualified enquiries",
        "keywords": [
            "seo", "landing page", "funnel", "organic", "marketing",
            "qualified enquiry", "qualified enquiries", "qualified lead",
            "qualified leads", "ads", "campaign",
        ],
    },
}

MISSING_QUESTIONS: dict[str, tuple[str, list[str]]] = {
    "business_goal": (
        "What measurable business outcome would make this project successful?",
        [
            "goal", "success", "reduce", "reduce by", "increase", "improve",
            "improvement", "improving", "hours per week", "conversion",
            "qualified", "outcome", "metric", "target",
        ],
    ),
    "systems": (
        "Which current tools or systems must this solution integrate with?",
        [
            "crm", "integrate", "integrated", "integration", "system",
            "platform", "spreadsheet", "email", "api", "hubspot", "salesforce",
        ],
    ),
    "timeline": (
        "Is there a target launch date or key deadline?",
        [
            "week", "weeks", "month", "months", "deadline", "launch",
            "timeline", "quarter", "pilot", "by january", "by february",
        ],
    ),
    "budget": (
        "Do you have an approved budget range for an initial phase or pilot?",
        [
            "budget", "pricing", "cost", "price", "funding", "usd", "inr",
            "₹", "€", "$", "rupees", "lakh", "lakhs",
        ],
    ),
    "data_and_privacy": (
        "What data will the solution process, and are there privacy or compliance requirements?",
        [
            "data privacy", "privacy", "personal data", "sensitive data",
            "compliance", "confidential", "gdpr", "data protection",
        ],
    ),
    "decision_process": (
        "Who will evaluate the proposal and approve the next step?",
        [
            "decision maker", "decision-maker", "decision", "approve",
            "approval", "stakeholder", "owner", "manager", "founder",
            "director", "sign-off", "sign off", "will evaluate",
        ],
    ),
}

HIGH_URGENCY_TERMS = [
    "as soon as possible",
    "asap",
    "this week",
    "immediately",
    "today",
]

HIGH_URGENCY_PATTERNS = [
    r"\b(?:this is|it is|it's|we need|we require|the project is|the deadline is)\s+(?:very\s+)?urgent\b",
    r"\b(?:need|require|requesting)\s+urgent\s+(?:support|help|delivery|response|implementation)\b",
    r"\burgent\s+(?:project|deadline|issue|timeline|requirement)\b",
]

MEDIUM_URGENCY_TERMS = [
    "next month",
    "next quarter",
    "this quarter",
]

# The vectorizer is fitted only to this fixed service catalogue, not user input.
_SERVICE_NAMES = list(SERVICE_CATALOG)
_VECTOR_DOCS = [
    f"{name}. {details['description']}"
    for name, details in SERVICE_CATALOG.items()
]
_VECTOR = TfidfVectorizer(
    ngram_range=(1, 2),
    stop_words="english",
    sublinear_tf=True,
)
_SERVICE_MATRIX = _VECTOR.fit_transform(_VECTOR_DOCS)


def _normalize(text: str) -> str:
    """Normalize Unicode and whitespace without stripping meaningful symbols."""
    normalized = unicodedata.normalize("NFKC", text or "").casefold()
    return re.sub(r"\s+", " ", normalized).strip()


def _term_pattern(term: str) -> re.Pattern[str]:
    """Build a phrase matcher with word boundaries to avoid substring false hits."""
    escaped = re.escape(_normalize(term)).replace(r"\ ", r"\s+")
    left = (
        r"(?<!\w)"
        if term and (term[0].isalnum() or term[0] == "_")
        else ""
    )
    right = (
        r"(?!\w)"
        if term and (term[-1].isalnum() or term[-1] == "_")
        else ""
    )
    return re.compile(left + escaped + right, flags=re.IGNORECASE)


def _contains_term(text: str, term: str) -> bool:
    return bool(_term_pattern(term).search(text))


def _contains_any(text: str, terms: list[str]) -> bool:
    return any(_contains_term(text, term) for term in terms)


def _extract_company(text: str) -> str | None:
    """Extract only when a company name is explicitly labelled or title-cased.

    Generic phrases such as 'we are a small e-commerce business' must not be
    mistaken for a company name.
    """
    explicit_patterns = [
        r"\b(?:company name|business name)\s*(?:is|:|=)\s*[\"']?([A-Za-z0-9][A-Za-z0-9&'-]*(?:\s+[A-Za-z0-9][A-Za-z0-9&'-]*){0,4})",
        r"\b(?:our company|the company)\s+(?:is|is called|is named)\s+([A-Za-z0-9][A-Za-z0-9&'-]*(?:\s+[A-Za-z0-9][A-Za-z0-9&'-]*){0,4})",
        r"\b(?:we are|we're)\s+([A-Z][A-Za-z0-9&'-]*(?:\s+[A-Z][A-Za-z0-9&'-]*){0,3})\b",
    ]

    stop_phrases = {
        "a small",
        "a company",
        "a business",
        "an agency",
        "a startup",
        "a team",
    }

    for index, pattern in enumerate(explicit_patterns):
        flags = re.IGNORECASE if index < 2 else 0
        match = re.search(pattern, text, flags=flags)

        if not match:
            continue

        candidate = match.group(1).strip(" .,!?:;\"'")

        if candidate.casefold() not in stop_phrases and len(candidate) >= 2:
            return candidate

    return None


def _infer_context(text: str) -> str:
    """Prefer explicit customer-industry cues over technologies they mention."""
    contexts = [
        (
            "Retail / e-commerce",
            ["e-commerce", "ecommerce", "online store", "shopify", "retail"],
        ),
        (
            "Operations / document-heavy workflow",
            [
                "invoice processing",
                "pdf documents",
                "document processing",
                "manual data entry",
                "vendor invoices",
            ],
        ),
        (
            "Marketing / growth",
            ["seo", "marketing", "campaign", "organic traffic", "landing page"],
        ),
        (
            "Professional / service business",
            [
                "consulting business",
                "service business",
                "appointments",
                "client portal",
                "consulting",
            ],
        ),
        (
            "SaaS / technology",
            [
                "saas",
                "software company",
                "software product",
                "developer",
                "backend development",
            ],
        ),
    ]

    for label, terms in contexts:
        if _contains_any(text, terms):
            return label

    return "Unspecified"


def _service_matches(text: str) -> list[dict[str, Any]]:
    query_vector = _VECTOR.transform([text])
    similarities = cosine_similarity(
        query_vector,
        _SERVICE_MATRIX,
    ).ravel()

    normalized = _normalize(text)
    results: list[dict[str, Any]] = []

    for index, name in enumerate(_SERVICE_NAMES):
        terms = SERVICE_CATALOG[name]["keywords"]
        evidence = sorted({
            term
            for term in terms
            if _contains_term(normalized, term)
        })

        tfidf_score = float(similarities[index])

        # This score combines lexical similarity and keyword evidence.
        # It is not a probability or calibrated confidence score.
        evidence_score = min(len(evidence) / 4, 1.0)
        combined = min(
            1.0,
            0.65 * tfidf_score + 0.35 * evidence_score,
        )

        if tfidf_score > 0 or evidence:
            results.append({
                "service": name,
                "score": round(combined, 4),
                "tfidf_similarity": round(tfidf_score, 4),
                "matched_terms": evidence,
            })

    results.sort(
        key=lambda item: (
            item["score"],
            len(item["matched_terms"]),
        ),
        reverse=True,
    )

    return results


def _timeline_mentioned(text: str) -> bool:
    if _contains_any(text, MISSING_QUESTIONS["timeline"][1]):
        return True

    # Also recognize ranges such as "6-8 weeks" or "within 12 weeks".
    duration = re.search(
        r"\b(?:within\s+)?\d+\s*(?:[-–—]\s*\d+\s*)?"
        r"(?:day|days|week|weeks|month|months)\b",
        text,
    )

    return bool(duration)


def _budget_mentioned(text: str) -> bool:
    if _contains_any(text, MISSING_QUESTIONS["budget"][1]):
        return True

    amount = re.search(
        r"(?:₹|\$|€|\bINR\b|\bUSD\b|\bRs\.?\s*)\s*"
        r"\d[\d,]*(?:\s*[-–—]\s*\d[\d,]*)?",
        text,
        flags=re.IGNORECASE,
    )

    return bool(amount)


def _urgency(text: str) -> tuple[str, list[str]]:
    """Detect explicit urgency separately from ordinary project timelines."""
    normalized = _normalize(text)

    high_hits = [
        term
        for term in HIGH_URGENCY_TERMS
        if _contains_term(normalized, term)
    ]

    high_hits.extend(
        match.group(0)
        for pattern in HIGH_URGENCY_PATTERNS
        if (match := re.search(pattern, normalized))
    )

    if high_hits:
        return "high", sorted(set(high_hits))

    medium_hits = [
        term
        for term in MEDIUM_URGENCY_TERMS
        if _contains_term(normalized, term)
    ]

    if medium_hits:
        return "medium", sorted(set(medium_hits))

    # Recognize durations and ranges such as "within 10 days"
    # or "within 6–8 weeks".
    duration = re.search(
        r"\b(?:within\s+)?(\d+)"
        r"(?:\s*[-–—]\s*(\d+))?\s*"
        r"(day|days|week|weeks|month|months)\b",
        normalized,
    )

    if duration:
        # Use the upper end of a range.
        amount = int(duration.group(2) or duration.group(1))
        unit = duration.group(3)

        if unit.startswith("day"):
            days = amount
        elif unit.startswith("week"):
            days = amount * 7
        else:
            days = amount * 30

        # A short stated deadline may indicate medium urgency.
        if days <= 14:
            return "medium", [duration.group(0)]

    # A normal project timeline alone does not establish urgency.
    return "unspecified", []


def analyze_inquiry(text: str) -> dict[str, Any]:
    """Analyze one inquiry and return a JSON-serializable structured result."""
    original = unicodedata.normalize("NFKC", (text or "")).strip()

    if not original:
        return {"error": "Please enter an inquiry before analyzing it."}

    normalized = _normalize(original)
    matches = _service_matches(original)

    top_score = matches[0]["score"] if matches else 0.0
    top_has_evidence = bool(
        matches and matches[0]["matched_terms"]
    )

    # Avoid confident routing based on weak similarity alone.
    if (
        not matches
        or top_score < 0.08
        or (not top_has_evidence and top_score < 0.15)
    ):
        primary_service = "Needs human discovery"
        recommendation_status = "low_match_route_to_human"
    else:
        primary_service = matches[0]["service"]
        recommendation_status = "suggestion_for_human_review"

    urgency, urgency_evidence = _urgency(normalized)

    budget_status = (
        "mentioned"
        if _budget_mentioned(normalized)
        else "not mentioned"
    )

    timeline_status = (
        "mentioned"
        if _timeline_mentioned(normalized)
        else "not mentioned"
    )

    missing_keys = [
        key
        for key, (_, terms) in MISSING_QUESTIONS.items()
        if not _contains_any(normalized, terms)
    ]

    missing = [
        MISSING_QUESTIONS[key][0]
        for key in missing_keys
    ]

    evidence_terms = sorted({
        term
        for item in matches
        for term in item["matched_terms"]
    })

    # Completeness is the share of six discovery dimensions with keyword
    # evidence. It is a heuristic, not a lead-conversion prediction.
    completeness_score = round(
        100
        * (len(MISSING_QUESTIONS) - len(missing_keys))
        / len(MISSING_QUESTIONS)
    )

    follow_up = "Thank you for sharing your requirements with Cynbit. "

    if primary_service != "Needs human discovery":
        follow_up += (
            f"Based on the information provided, "
            f"{primary_service.lower()} may be a relevant starting point. "
        )
    else:
        follow_up += (
            "We would like to understand your business need in more detail "
            "before recommending an approach. "
        )

    if missing:
        follow_up += (
            "To prepare an initial scope, could you clarify: "
            + " ".join(missing[:3])
        )
    else:
        follow_up += (
            "We can arrange a discovery discussion to validate requirements "
            "and agree on next steps."
        )

    follow_up += "\n\nDraft only — review and edit before sending."

    return {
        "company_guess": _extract_company(original),
        "industry_or_context": _infer_context(normalized),
        "primary_service_recommendation": primary_service,
        "recommendation_status": recommendation_status,
        "service_matches": matches[:3],
        "urgency_signal": urgency,
        "urgency_evidence": urgency_evidence,
        "budget_status": budget_status,
        "timeline_status": timeline_status,
        "lead_readiness_score": completeness_score,
        "score_interpretation": (
            "Heuristic completeness indicator: percentage of six discovery "
            "dimensions with keyword evidence; not a probability of conversion."
        ),
        "missing_discovery_questions": missing,
        "evidence_terms": evidence_terms,
        "draft_follow_up": follow_up,
        "human_review_required": True,
        "method": (
            "TF-IDF cosine similarity over a fixed service catalogue plus "
            "boundary-aware keyword rules; no generative model or external API"
        ),
    }