from app.crawler.crawler import CrawlResult
from app.scanners.functionality import FunctionalityScanner

def test_functionality_scanner_detects_password_over_get():
    html_with_get_pwd = """
    <html>
    <body>
        <form method="GET" id="loginForm">
            <input type="text" name="user" />
            <input type="password" name="pwd" />
            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    """
    crawl_res = CrawlResult(
        url="https://site.local",
        status_code=200,
        title="Form Test",
        html=html_with_get_pwd,
        links=[],
        images=[],
        response_time=0.3
    )
    scanner = FunctionalityScanner()
    score, findings = scanner.scan(crawl_res)
    titles = [f.title for f in findings]
    assert "Password Field Transmitted via HTTP GET" in titles
    assert any(f.severity == "Critical" for f in findings)
    assert score < 70.0

def test_functionality_scanner_detects_dead_placeholders_and_unnamed_inputs():
    html = """
    <html>
    <body>
        <a href="#">Dead Link 1</a>
        <a href="javascript:void(0)">Dead Link 2</a>
        <form method="POST">
            <input type="text" id="no_name_field" />
            <button type="submit">Send</button>
        </form>
    </body>
    </html>
    """
    crawl_res = CrawlResult(
        url="https://site.local",
        status_code=200,
        title="Placeholders Test",
        html=html,
        links=[],
        images=[],
        response_time=0.3
    )
    scanner = FunctionalityScanner()
    score, findings = scanner.scan(crawl_res)
    titles = [f.title for f in findings]
    assert "Dead Anchor Links with Placeholder Hrefs" in titles
    assert "Form Controls Missing Name Attribute" in titles
