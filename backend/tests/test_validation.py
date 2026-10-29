from app.crawler.crawler import validate_url

def test_validate_url():
    assert validate_url("https://example.com") is True
    assert validate_url("http://subdomain.domain.org/path?query=1") is True
    assert validate_url("ftp://example.com") is False
    assert validate_url("not_a_url") is False
    assert validate_url("") is False
    assert validate_url(None) is False
