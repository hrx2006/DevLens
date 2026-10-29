from app.crawler.crawler import CrawlResult
from app.scanners.seo import SEOScanner
from app.scanners.accessibility import AccessibilityScanner
from app.scanners.performance import PerformanceScanner

def test_seo_scanner_detects_missing_title_and_meta():
    bad_html = "<html><head></head><body><h1>Heading</h1></body></html>"
    crawl_res = CrawlResult(
        url="https://test.local",
        status_code=200,
        title="",
        html=bad_html,
        links=[],
        images=[],
        response_time=0.5
    )
    seo = SEOScanner()
    score, findings = seo.scan(crawl_res)
    assert score < 100.0
    finding_titles = [f.title for f in findings]
    assert "Missing Page Title" in finding_titles
    assert "Missing Meta Description" in finding_titles

def test_accessibility_scanner_detects_missing_alt():
    bad_html = "<html><head><title>Test</title></head><body><img src='test.jpg'></body></html>"
    crawl_res = CrawlResult(
        url="https://test.local",
        status_code=200,
        title="Test",
        html=bad_html,
        links=[],
        images=[{"src": "test.jpg", "alt": None}],
        response_time=0.5
    )
    acc = AccessibilityScanner()
    score, findings = acc.scan(crawl_res)
    assert score < 100.0
    finding_titles = [f.title for f in findings]
    assert "Images Missing Alt Text" in finding_titles

def test_performance_scanner_latency_deduction():
    html = "<html><head><title>Test</title></head><body><p>Clean HTML</p></body></html>"
    crawl_res = CrawlResult(
        url="https://test.local",
        status_code=200,
        title="Test",
        html=html,
        links=[],
        images=[],
        response_time=3.0  # Slow > 2.5s
    )
    perf = PerformanceScanner()
    score, findings = perf.scan(crawl_res)
    assert score <= 70.0
    finding_titles = [f.title for f in findings]
    assert "Slow Initial Server Response Time" in finding_titles
