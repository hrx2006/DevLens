from typing import Dict, Any, Optional

class NormalizedFinding:
    def __init__(
        self,
        category: str,
        title: str,
        description: str,
        severity: str,
        evidence: str,
        source: str,
        recommendation: str = ""
    ):
        self.category = category
        self.title = title
        self.description = description
        self.severity = severity  # Critical, High, Medium, Low, Info
        self.evidence = evidence
        self.source = source
        self.recommendation = recommendation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "evidence": self.evidence,
            "source": self.source,
            "recommendation": self.recommendation
        }

class BaseScanner:
    def scan(self, crawl_result) -> tuple[float, list[NormalizedFinding]]:
        """
        Returns a tuple of (category_score: float [0-100], findings: List[NormalizedFinding])
        """
        raise NotImplementedError("Subclasses must implement the scan method.")
