import pytest
from app.services.ai_service import AIService

@pytest.mark.asyncio
async def test_ai_fallback_without_api_key():
    ai = AIService()
    ai.api_key = ""  # Ensure no key
    dummy_findings = [
        {
            "category": "SEO",
            "title": "Missing Page Title",
            "evidence": "No title tag found",
            "recommendation": "Add a title tag"
        }
    ]
    res = await ai.analyze_findings("https://example.com", dummy_findings)
    assert "summary" in res
    assert len(res["analyzed_issues"]) == 1
    issue = res["analyzed_issues"][0]
    assert issue["title"] == "Missing Page Title"
    assert "Likely" in issue["root_cause"] or "evidence" in issue["root_cause"]
