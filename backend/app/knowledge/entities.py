"""
app/knowledge/entities.py
─────────────────────────────────────────────────────────────────────────────
Rule-based entity extraction (dates, technologies, projects, departments) from text.
Compatible with Python 3.9.
"""

from __future__ import annotations

import re
from typing import Dict, List


def extract_entities_from_text(text: str) -> Dict[str, List[str]]:
    """Extract standard entities from document text using regular expressions and profiles."""
    if not text:
        return {"people": [], "technologies": [], "projects": [], "dates": [], "departments": []}

    text_lower = text.lower()
    
    # 1. Technologies
    tech_keywords = [
        "python", "javascript", "typescript", "fastapi", "react", "next.js", "nextjs",
        "supabase", "postgresql", "postgres", "sqlalchemy", "docker", "kubernetes",
        "aws", "gcp", "azure", "tailwind", "redis", "celery", "git"
    ]
    tech_found = [tech for tech in tech_keywords if tech in text_lower]
    
    # 2. Projects
    project_keywords = ["atlas", "brainos", "copilot", "payments", "auth", "rag", "search"]
    projects_found = [proj for proj in project_keywords if proj in text_lower]
    
    # 3. Dates (standard regex matching e.g. YYYY-MM-DD or YYYY/MM/DD)
    dates_found = re.findall(r"\b\d{4}[-/]\d{2}[-/]\d{2}\b", text)
    
    # 4. People (detect email patterns as proxy for people identities in logs)
    emails_found = list(set(re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)))
    
    # 5. Departments
    dept_keywords = ["engineering", "product", "sales", "marketing", "finance", "legal", "hr", "operations"]
    depts_found = [dept for dept in dept_keywords if dept in text_lower]

    return {
        "people": emails_found,
        "technologies": [t.title() for t in tech_found],
        "projects": [p.title() for p in projects_found],
        "dates": list(set(dates_found)),
        "departments": [d.title() for d in depts_found],
    }
