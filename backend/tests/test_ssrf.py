from app.crawler.ssrf import is_safe_url

def test_reject_localhost_and_loopback():
    safe, msg = is_safe_url("http://127.0.0.1:8000/api")
    assert not safe
    assert "blocked" in msg.lower()

    safe2, msg2 = is_safe_url("http://localhost/admin")
    assert not safe2
    assert "restricted hostname" in msg2.lower()

def test_reject_private_rfc1918_ips():
    for private_target in [
        "http://10.0.0.1/status",
        "http://192.168.1.1/router",
        "http://172.16.0.1/login"
    ]:
        safe, msg = is_safe_url(private_target)
        assert not safe, f"Failed to reject private IP target: {private_target}"
        assert "blocked" in msg.lower()

def test_reject_cloud_metadata_endpoints():
    safe, msg = is_safe_url("http://169.254.169.254/latest/meta-data/")
    assert not safe
    assert "blocked" in msg.lower() or "restricted" in msg.lower()

    safe_gcp, msg_gcp = is_safe_url("http://metadata.google.internal/computeMetadata/v1/")
    assert not safe_gcp
    assert "restricted" in msg_gcp.lower()

def test_reject_unsupported_schemes():
    for bad_scheme in [
        "ftp://example.com/file.txt",
        "file:///etc/passwd",
        "gopher://example.com",
        "data:text/html,<script>alert(1)</script>"
    ]:
        safe, msg = is_safe_url(bad_scheme)
        assert not safe
        assert "scheme" in msg.lower()

def test_allow_demo_target_safe_bypass():
    safe, msg = is_safe_url("https://demo.local")
    assert safe
    assert "demo" in msg.lower()

def test_reject_invalid_port_numbers():
    for bad_url in [
        "http://example.com:99999",
        "http://example.com:0",
        "http://example.com:70000"
    ]:
        safe, msg = is_safe_url(bad_url)
        assert not safe
        assert "port" in msg.lower()

def test_reject_ipv6_loopback_and_link_local():
    for ipv6_target in [
        "http://[::1]/",
        "http://[fe80::1]/",
        "http://[fc00::1]/"
    ]:
        safe, msg = is_safe_url(ipv6_target)
        assert not safe
        assert "blocked" in msg.lower()
