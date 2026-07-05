"""
app/knowledge/classifier.py
─────────────────────────────────────────────────────────────────────────────
Rule-based heuristic document classifier.
Classifies text into domains (e.g., Legal, Finance, Engineering) using keyword densities.
Compatible with Python 3.9.
"""

from __future__ import annotations

from typing import List


def classify_text(text: str) -> List[str]:
    """Classify text topics based on keyword lookup profiles."""
    if not text:
        return []

    text_lower = text.lower()
    scores = {
        "Engineering": ["code", "software", "api", "database", "git", "backend", "frontend", "aws", "deploy", "architecture"],
        "HR & Policies": ["policy", "onboarding", "leave", "benefits", "employee", "handbook", "hr", "recruiting", "salary"],
        "Finance & Billing": ["invoice", "payment", "revenue", "price", "budget", "billing", "cost", "financial", "tax"],
        "Legal & Compliance": ["contract", "agreement", "nda", "compliance", "terms", "liability", "clause", "gdpr", "privacy"],
        "Product Management": ["roadmap", "sprint", "milestone", "user story", "backlog", "epic", "jira", "feature", "mvp"],
    }

    detected_topics = []
    for topic, keywords in scores.items():
        count = sum(text_lower.count(kw) for kw in keywords)
        if count >= 2:
            detected_topics.append(topic)
            
    if not detected_topics:
        detected_topics.append("General Documentation")

    return detected_topics
