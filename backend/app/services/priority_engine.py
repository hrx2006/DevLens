from typing import List, Dict, Any, Optional

SEVERITY_WEIGHTS = {
    "Critical": 95,
    "High": 80,
    "Medium": 55,
    "Low": 30,
    "Info": 15
}

CATEGORY_WEIGHT_MULTIPLIERS = {
    "Security": 1.05,
    "Functionality": 1.0,
    "Accessibility": 1.0,
    "SEO": 0.95,
    "Performance": 1.0
}

class PriorityEngine:
    @staticmethod
    def calculate_priority(severity: str, category: str = "") -> int:
        """
        Maps finding severity and category to an actionable priority score (0-100).
        High-severity security or functionality issues are emphasized for remediation.
        """
        base = SEVERITY_WEIGHTS.get(severity, 50)
        multiplier = CATEGORY_WEIGHT_MULTIPLIERS.get(category, 1.0)
        final_priority = int(min(100, max(0, round(base * multiplier))))
        return final_priority

    @staticmethod
    def calculate_overall_health(
        seo_score: float,
        accessibility_score: float,
        performance_score: float,
        security_score: Optional[float] = None,
        functionality_score: Optional[float] = None
    ) -> float:
        """
        Calculates the transparent overall website health score (0.0 - 100.0)
        based on all active category audit scores.
        """
        active_scores = [s for s in [seo_score, accessibility_score, performance_score, security_score, functionality_score] if s is not None]
        if not active_scores:
            return 0.0
        
        overall = sum(active_scores) / len(active_scores)
        clamped = max(0.0, min(100.0, overall))
        return round(clamped, 1)

priority_engine = PriorityEngine()
