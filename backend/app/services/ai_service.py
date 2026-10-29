import json
import logging
import httpx
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger("devlens.ai_service")

SYSTEM_PROMPT = """
You are DevLens AI, an intelligent website audit reasoning engine.
You will be provided with technical findings detected by deterministic scanners for a website across 5 categories: SEO, Accessibility, Performance, Security, and Functionality.

STRICT OPERATIONAL RULES:
1. Only analyze the supplied findings.
2. Do NOT invent or hallucinate technical issues that are not present in the supplied findings.
3. Do NOT claim a check was performed if the scanner did not provide evidence.
4. For root causes, use probabilistic language like "Likely caused by", "May indicate", or "Based on scanner evidence".
5. Return your response as a strictly valid JSON object matching this schema:
{
  "summary": "Executive audit summary...",
  "overall_assessment": "Overall technical quality assessment...",
  "analyzed_issues": [
    {
      "title": "Exact issue title from findings",
      "category": "Category name",
      "ai_explanation": "Clear explanation of what the issue means",
      "root_cause": "Likely root cause based on evidence",
      "user_impact": "Direct impact on visitors, screen readers, browser security, or search engines",
      "recommendation": "Clear step-by-step developer remediation recommendation"
    }
  ]
}
"""

class AIService:
    def __init__(self):
        self.api_key = settings.AI_API_KEY
        self.model = settings.AI_MODEL

    async def analyze_findings(self, target_url: str, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Takes normalized scanner findings and returns structured AI reasoning.
        Falls back seamlessly if API key is missing, network fails, or output is invalid.
        """
        if not findings:
            return {
                "summary": "No technical issues were detected during the automated audit scan.",
                "overall_assessment": "The website passed all active technical audit checks cleanly across all categories.",
                "ai_source": "Deterministic Fallback Engine",
                "analyzed_issues": []
            }

        if self.api_key and len(self.api_key.strip()) > 5:
            try:
                ai_response = await self._call_gemini_api(target_url, findings)
                if ai_response and "analyzed_issues" in ai_response:
                    source_label = f"Google Gemini ({self.model})"
                    ai_response["ai_source"] = source_label
                    for iss in ai_response.get("analyzed_issues", []):
                        iss["ai_source"] = source_label
                    return ai_response
            except Exception as e:
                logger.warning(f"Gemini AI API call failed: {e}. Falling back to deterministic reasoning engine.")

        # Deterministic / Evidence-Based Fallback Reasoning
        return self._generate_fallback_analysis(target_url, findings)

    async def _call_gemini_api(self, target_url: str, findings: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        prompt_content = {
            "website": target_url,
            "findings": findings
        }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": SYSTEM_PROMPT},
                        {"text": f"Analyze these findings for website: {target_url}\nJSON input:\n{json.dumps(prompt_content, indent=2)}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }

        # Bounded retry and timeout
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        result_json = resp.json()
                        text_content = result_json["candidates"][0]["content"]["parts"][0]["text"]
                        parsed = json.loads(text_content)
                        if isinstance(parsed, dict) and "analyzed_issues" in parsed:
                            return parsed
                    else:
                        logger.warning(f"Gemini API attempt {attempt+1} returned HTTP {resp.status_code}")
            except Exception as e:
                logger.warning(f"Gemini API attempt {attempt+1} error: {e}")

        return None

    def _generate_fallback_analysis(self, target_url: str, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        analyzed_issues = []
        for f in findings:
            cat = f.get("category", "")
            title = f.get("title", "")
            evidence = f.get("evidence", "")

            explanation = f"Automated scan identified '{title}' under {cat}. Evidence: {evidence}"

            if cat == "SEO":
                root_cause = "Likely caused by missing HTML document metadata, unoptimized heading hierarchy, or missing canonical tags in the template."
                user_impact = "Search engines may display incomplete SERP snippets or index pages less favorably in organic rankings."
                rec = f.get("recommendation") or "Review document head elements and add required meta, title, and canonical tags."
            elif cat == "Accessibility":
                root_cause = "Likely caused by unlabeled UI controls, missing text alternatives, or omitted language declarations."
                user_impact = "Assistive technology users (screen readers) will experience severe friction navigating content or understanding media."
                rec = f.get("recommendation") or "Ensure all interactive elements have explicit labels and images provide alternative text per WCAG 2.2."
            elif cat == "Performance":
                root_cause = "Likely caused by high network/server latency, uncompressed asset payloads, or render-blocking scripts in document head."
                user_impact = "Visitors on mobile devices or constrained connections experience slower page rendering and increased bounce rates."
                rec = f.get("recommendation") or "Minify HTML/CSS, add defer/async to scripts, and implement asset caching."
            elif cat == "Security":
                root_cause = "Likely caused by omitted defense-in-depth HTTP security headers, unencrypted transport, or missing cookie flags."
                user_impact = "Vulnerability to man-in-the-middle interception, clickjacking, MIME confusion attacks, or cross-site request forgery."
                rec = f.get("recommendation") or "Enforce HTTPS with HSTS, configure CSP, and set Strict-Transport-Security and cookie security flags."
            elif cat == "Functionality":
                root_cause = "Likely caused by incomplete form attributes, broken internal hyperlink references, or placeholder anchor targets."
                user_impact = "Users encounter dead ends, failed form submissions, or exposed credentials in URL query logs."
                rec = f.get("recommendation") or "Provide valid target actions for forms, set method='POST' for credentials, and update dead links."
            else:
                root_cause = "Based on scanner evidence, component configuration requires review."
                user_impact = "May degrade website reliability and user satisfaction."
                rec = f.get("recommendation") or "Follow standard web development best practices."

            fallback_source = "DevLens Deterministic Fallback Engine"
            analyzed_issues.append({
                "title": title,
                "category": cat,
                "ai_explanation": explanation,
                "root_cause": root_cause,
                "user_impact": user_impact,
                "recommendation": rec,
                "ai_source": fallback_source
            })

        issue_count = len(findings)
        summary = f"DevLens AI analyzed {issue_count} technical finding(s) across SEO, Accessibility, Performance, Security, and Functionality."
        assessment = f"The website exhibits {issue_count} area(s) needing technical remediation to achieve optimal compliance, security, and performance standards."

        return {
            "summary": summary,
            "overall_assessment": assessment,
            "ai_source": "DevLens Deterministic Fallback Engine",
            "analyzed_issues": analyzed_issues
        }

ai_service = AIService()
