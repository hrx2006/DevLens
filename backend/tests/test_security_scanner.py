from app.crawler.crawler import CrawlResult
from app.scanners.security import SecurityScanner

def test_security_scanner_detects_http_insecure_transport():
    crawl_res = CrawlResult(
        url="http://insecure-site.local",
        status_code=200,
        title="Insecure HTTP Site",
        html="<html><body><p>Testing</p></body></html>",
        links=[],
        images=[],
        response_time=0.4,
        headers={"content-type": "text/html"},
        final_url="http://insecure-site.local"
    )
    scanner = SecurityScanner()
    score, findings = scanner.scan(crawl_res)
    assert score <= 60.0
    titles = [f.title for f in findings]
    assert "Insecure HTTP Transport (No HTTPS)" in titles

def test_security_scanner_detects_missing_headers_and_mixed_content():
    # HTTPS site missing HSTS, CSP, and X-Frame-Options, containing mixed-content image
    html_with_mixed = """
    <html>
    <head><title>Secure Page</title></head>
    <body>
        <img src="http://insecure.example.com/banner.jpg" />
    </body>
    </html>
    """
    crawl_res = CrawlResult(
        url="https://secure-site.local",
        status_code=200,
        title="Secure Page",
        html=html_with_mixed,
        links=[],
        images=[{"src": "http://insecure.example.com/banner.jpg", "alt": "banner"}],
        response_time=0.5,
        headers={"content-type": "text/html"},
        final_url="https://secure-site.local"
    )
    scanner = SecurityScanner()
    score, findings = scanner.scan(crawl_res)
    titles = [f.title for f in findings]

    assert "Missing Strict-Transport-Security (HSTS) Header" in titles
    assert "Missing Content-Security-Policy (CSP)" in titles
    assert "Missing Clickjacking Defense (X-Frame-Options)" in titles
    assert "Insecure Mixed-Content Detected" in titles
    assert score < 60.0
