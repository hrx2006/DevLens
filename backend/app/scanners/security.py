import urllib.parse
from bs4 import BeautifulSoup
from app.scanners.base import BaseScanner, NormalizedFinding

class SecurityScanner(BaseScanner):
    """
    Deterministic Security Scanner.
    Inspects transport encryption, HTTP security headers, mixed-content, and cookie hygiene.
    Operates strictly within passive, non-destructive inspection limits.
    """
    def scan(self, crawl_result) -> tuple[float, list[NormalizedFinding]]:
        findings = []
        deductions = 0.0
        headers = {k.lower(): v for k, v in crawl_result.headers.items()}
        soup = BeautifulSoup(crawl_result.html, "html.parser")
        is_https = crawl_result.is_https

        # 1. HTTPS Transport Encryption Check
        if not is_https:
            # Check if initial HTTP had a redirect towards HTTPS in redirect history
            redirected_to_https = any(
                h.get("to_url", "").lower().startswith("https://")
                for h in crawl_result.redirect_history
            )
            if not redirected_to_https:
                findings.append(NormalizedFinding(
                    category="Security",
                    title="Insecure HTTP Transport (No HTTPS)",
                    description="The website is served over unencrypted HTTP, leaving data vulnerable to interception and man-in-the-middle (MITM) attacks.",
                    severity="Critical",
                    evidence=f"Final URL is '{crawl_result.final_url}' without TLS encryption.",
                    source="security_scanner",
                    recommendation="Install an SSL/TLS certificate and enforce automatic 301 redirection from HTTP to HTTPS across all routes."
                ))
                deductions += 40.0
        else:
            # Target is HTTPS, check if HSTS is present
            hsts = headers.get("strict-transport-security")
            if not hsts:
                findings.append(NormalizedFinding(
                    category="Security",
                    title="Missing Strict-Transport-Security (HSTS) Header",
                    description="The `Strict-Transport-Security` header is missing, allowing potential SSL-stripping attacks on first-time connections.",
                    severity="High",
                    evidence="Strict-Transport-Security header was not returned by server.",
                    source="security_scanner",
                    recommendation="Add `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload` header to all HTTPS responses."
                ))
                deductions += 15.0

        # 2. Content-Security-Policy (CSP) Check
        csp = headers.get("content-security-policy")
        if not csp:
            findings.append(NormalizedFinding(
                category="Security",
                title="Missing Content-Security-Policy (CSP)",
                description="No `Content-Security-Policy` header is configured. CSP protects against Cross-Site Scripting (XSS) and code injection.",
                severity="High",
                evidence="Content-Security-Policy header was absent in HTTP response.",
                source="security_scanner",
                recommendation="Define a robust CSP (e.g. `default-src 'self'; script-src 'self'; object-src 'none'`) to restrict untrusted scripts."
            ))
            deductions += 20.0

        # 3. X-Content-Type-Options Header Check
        x_content_type = headers.get("x-content-type-options")
        if not x_content_type or "nosniff" not in x_content_type.lower():
            findings.append(NormalizedFinding(
                category="Security",
                title="Missing X-Content-Type-Options: nosniff Header",
                description="Without `X-Content-Type-Options: nosniff`, browsers may MIME-sniff response bodies and execute malicious files as scripts or stylesheets.",
                severity="Medium",
                evidence=f"Header value: '{x_content_type}' (expected 'nosniff').",
                source="security_scanner",
                recommendation="Configure your web server to return `X-Content-Type-Options: nosniff` on all responses."
            ))
            deductions += 10.0

        # 4. Clickjacking Protection (X-Frame-Options or CSP frame-ancestors)
        x_frame = headers.get("x-frame-options")
        has_frame_ancestors = csp and "frame-ancestors" in csp.lower()
        if not x_frame and not has_frame_ancestors:
            findings.append(NormalizedFinding(
                category="Security",
                title="Missing Clickjacking Defense (X-Frame-Options)",
                description="Neither `X-Frame-Options` nor CSP `frame-ancestors` directive was detected, leaving the page vulnerable to UI redressing (Clickjacking).",
                severity="Medium",
                evidence="Neither X-Frame-Options header nor CSP frame-ancestors was configured.",
                source="security_scanner",
                recommendation="Set `X-Frame-Options: DENY` or `SAMEORIGIN`, or include `frame-ancestors 'self'` in your Content-Security-Policy."
            ))
            deductions += 15.0

        # 5. Referrer-Policy Header Check
        referrer_policy = headers.get("referrer-policy")
        if not referrer_policy:
            findings.append(NormalizedFinding(
                category="Security",
                title="Missing Referrer-Policy Header",
                description="No `Referrer-Policy` header was found. Browsers may leak sensitive URL parameters to external third-party domains.",
                severity="Low",
                evidence="Referrer-Policy header not provided.",
                source="security_scanner",
                recommendation="Set `Referrer-Policy: strict-origin-when-cross-origin` or `no-referrer`."
            ))
            deductions += 5.0

        # 6. Permissions-Policy Header Check
        permissions_policy = headers.get("permissions-policy") or headers.get("feature-policy")
        if not permissions_policy:
            findings.append(NormalizedFinding(
                category="Security",
                title="Missing Permissions-Policy Header",
                description="The `Permissions-Policy` header controls browser APIs (camera, microphone, geolocation) that can be accessed by the document or embedded frames.",
                severity="Low",
                evidence="Permissions-Policy header was not found.",
                source="security_scanner",
                recommendation="Define `Permissions-Policy: geolocation=(), camera=(), microphone=()` to restrict unneeded device capabilities."
            ))
            deductions += 5.0

        # 7. Insecure Mixed-Content Detection (HTTPS page loading HTTP resources)
        if is_https:
            mixed_content_items = []
            for tag, attr in [("script", "src"), ("link", "href"), ("img", "src"), ("iframe", "src")]:
                for elem in soup.find_all(tag):
                    val = elem.get(attr, "").strip()
                    if val.lower().startswith("http://"):
                        mixed_content_items.append(f"<{tag} {attr}='{val[:60]}'>")

            if mixed_content_items:
                findings.append(NormalizedFinding(
                    category="Security",
                    title="Insecure Mixed-Content Detected",
                    description="The HTTPS document loads active or passive assets over insecure HTTP connections, which modern browsers block or warn against.",
                    severity="High",
                    evidence=f"Discovered {len(mixed_content_items)} mixed-content resource(s): {mixed_content_items[:3]}",
                    source="security_scanner",
                    recommendation="Update all asset URLs to use `https://` protocol or protocol-relative paths."
                ))
                deductions += 20.0

        # 8. Cookie Security Flags Check
        set_cookie = headers.get("set-cookie")
        if set_cookie:
            cookie_lower = set_cookie.lower()
            issues_found = []
            if "httponly" not in cookie_lower:
                issues_found.append("Missing HttpOnly (susceptible to XSS cookie theft)")
            if is_https and "secure" not in cookie_lower:
                issues_found.append("Missing Secure flag (may be transmitted over HTTP)")
            if "samesite" not in cookie_lower:
                issues_found.append("Missing SameSite attribute (susceptible to CSRF)")

            if issues_found:
                findings.append(NormalizedFinding(
                    category="Security",
                    title="Insecure Cookie Attributes",
                    description=f"Cookies set by the application lack essential defensive flags: {'; '.join(issues_found)}.",
                    severity="Medium",
                    evidence=f"Set-Cookie header flags: {issues_found}",
                    source="security_scanner",
                    recommendation="Ensure all session and auth cookies include `HttpOnly; Secure; SameSite=Lax` (or Strict)."
                ))
                deductions += 10.0

        score = max(0.0, min(100.0, 100.0 - deductions))
        return round(score, 1), findings
