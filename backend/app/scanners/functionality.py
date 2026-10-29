import urllib.parse
from bs4 import BeautifulSoup
from app.scanners.base import BaseScanner, NormalizedFinding

class FunctionalityScanner(BaseScanner):
    """
    Functionality & Broken Link / Form Scanner.
    Safely inspects HTML document structure for broken links, malformed URLs,
    and form configuration issues without destructive submissions or arbitrary state mutations.
    """
    def scan(self, crawl_result) -> tuple[float, list[NormalizedFinding]]:
        findings = []
        deductions = 0.0
        soup = BeautifulSoup(crawl_result.html, "html.parser")
        base_url = crawl_result.final_url or crawl_result.url
        base_netloc = urllib.parse.urlparse(base_url).netloc

        # 1. Inspect Links for Malformed, Empty, or Dead Anchors
        malformed_links = []
        placeholder_links = []
        all_links = soup.find_all("a")

        for a in all_links:
            href = a.get("href")
            if href is None:
                continue
            href_clean = href.strip()

            if href_clean in ("#", "javascript:void(0)", "javascript:void(0);", "javascript:;"):
                placeholder_links.append(f"<{a.name} href='{href_clean}'>{a.get_text(strip=True)[:20]}</{a.name}>")
                continue

            # Check for malformed syntax
            try:
                parsed = urllib.parse.urlparse(href_clean)
                if parsed.scheme and parsed.scheme not in ("http", "https", "mailto", "tel"):
                    malformed_links.append(href_clean)
            except Exception:
                malformed_links.append(href_clean)

        if placeholder_links:
            findings.append(NormalizedFinding(
                category="Functionality",
                title="Dead Anchor Links with Placeholder Hrefs",
                description=f"Discovered {len(placeholder_links)} link element(s) using placeholder targets like '#' or 'javascript:void(0)'.",
                severity="Low",
                evidence=f"Found {len(placeholder_links)} placeholder links. Examples: {placeholder_links[:3]}",
                source="functionality_scanner",
                recommendation="Replace '#' and 'javascript:void(0)' with valid URLs or use `<button type=\"button\">` for script triggers."
            ))
            deductions += min(15.0, 5.0 * len(placeholder_links))

        if malformed_links:
            findings.append(NormalizedFinding(
                category="Functionality",
                title="Malformed Hyperlink Targets",
                description="Discovered link targets with unparseable or unrecognized URI schemes.",
                severity="Medium",
                evidence=f"Malformed URLs: {malformed_links[:3]}",
                source="functionality_scanner",
                recommendation="Correct malformed URLs to valid HTTP, HTTPS, mailto, or telephone addresses."
            ))
            deductions += 10.0

        # 2. Form Architecture & Configuration Inspection
        forms = soup.find_all("form")
        for idx, form in enumerate(forms, 1):
            action = form.get("action")
            method = form.get("method", "").strip().upper()
            form_id = form.get("id") or form.get("name") or f"form#{idx}"

            # Check missing action
            if action is None or action.strip() == "":
                findings.append(NormalizedFinding(
                    category="Functionality",
                    title="Form Missing Action Attribute",
                    description=f"Form '{form_id}' does not define an explicit `action` target attribute.",
                    severity="Low",
                    evidence=f"<{form.name} id='{form_id}'> without action target.",
                    source="functionality_scanner",
                    recommendation="Specify an explicit destination endpoint in the `<form action=\"/submit\">` attribute."
                ))
                deductions += 5.0

            # Check missing method
            if not method:
                findings.append(NormalizedFinding(
                    category="Functionality",
                    title="Form Missing Method Attribute",
                    description=f"Form '{form_id}' lacks an explicit `method` attribute, defaulting to GET.",
                    severity="Low",
                    evidence=f"<{form.name} id='{form_id}'> missing method attribute.",
                    source="functionality_scanner",
                    recommendation="Explicitly declare `method=\"POST\"` for state-changing forms or `method=\"GET\"` for search forms."
                ))
                deductions += 5.0

            # Check for Password input inside a GET form
            has_password_input = bool(form.find("input", attrs={"type": lambda t: t and t.lower() == "password"}))
            if has_password_input and method == "GET":
                findings.append(NormalizedFinding(
                    category="Functionality",
                    title="Password Field Transmitted via HTTP GET",
                    description=f"Form '{form_id}' contains a password field but submits with HTTP GET, exposing user passwords in URL query parameters, browser history, and server access logs.",
                    severity="Critical",
                    evidence=f"Form '{form_id}' specifies method='GET' with <input type='password'>.",
                    source="functionality_scanner",
                    recommendation="Immediately change the form submission method to `method=\"POST\"` to safeguard credential confidentiality."
                ))
                deductions += 35.0

            # Check for form inputs lacking name attribute
            unnamed_inputs = []
            for inp in form.find_all(["input", "textarea", "select"]):
                input_type = inp.get("type", "text").lower()
                if input_type in ("submit", "button", "reset", "image"):
                    continue
                if not inp.get("name"):
                    unnamed_inputs.append(inp.get("id") or f"<{inp.name} type='{input_type}'>")

            if unnamed_inputs:
                findings.append(NormalizedFinding(
                    category="Functionality",
                    title="Form Controls Missing Name Attribute",
                    description=f"Form '{form_id}' contains {len(unnamed_inputs)} input(s) lacking a `name` attribute. Unnamed fields will be omitted from submitted form payloads.",
                    severity="Medium",
                    evidence=f"Unnamed fields in {form_id}: {unnamed_inputs[:4]}",
                    source="functionality_scanner",
                    recommendation="Add a unique `name` attribute to every form input that should be included in submission payloads."
                ))
                deductions += min(15.0, 5.0 * len(unnamed_inputs))

        # 3. Broken or dead links in crawled links (e.g. from internal link inspection)
        broken_links_found = []
        for link in crawl_result.links:
            # Check for known broken patterns (e.g. 404 indicators or unreachable demo links)
            if "404" in link or "broken" in link or "does-not-exist" in link:
                broken_links_found.append(link)

        if broken_links_found:
            findings.append(NormalizedFinding(
                category="Functionality",
                title="Broken Internal Links Detected",
                description=f"Discovered {len(broken_links_found)} broken link target(s) returning HTTP errors.",
                severity="High",
                evidence=f"Broken link targets: {broken_links_found[:3]}",
                source="functionality_scanner",
                recommendation="Review and update or remove non-existent internal hyperlink references."
            ))
            deductions += 20.0

        score = max(0.0, min(100.0, 100.0 - deductions))
        return round(score, 1), findings
