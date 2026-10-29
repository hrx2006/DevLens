from bs4 import BeautifulSoup
from app.scanners.base import BaseScanner, NormalizedFinding

class PerformanceScanner(BaseScanner):
    def scan(self, crawl_result) -> tuple[float, list[NormalizedFinding]]:
        findings = []
        deductions = 0.0
        soup = BeautifulSoup(crawl_result.html, "html.parser")

        # 1. Response / Server Latency Check
        resp_time = crawl_result.response_time
        if resp_time > 2.5:
            findings.append(NormalizedFinding(
                category="Performance",
                title="Slow Initial Server Response Time",
                description=f"The server took {resp_time} seconds to respond to the HTTP GET request.",
                severity="High",
                evidence=f"Time-to-first-byte / HTTP response latency was {resp_time}s (recommended < 0.8s).",
                source="performance_scanner",
                recommendation="Optimize backend database queries, implement HTTP caching headers, and utilize a Content Delivery Network (CDN)."
            ))
            deductions += 30.0
        elif resp_time > 1.2:
            findings.append(NormalizedFinding(
                category="Performance",
                title="Moderate Server Response Time",
                description=f"Initial response time was {resp_time} seconds, which could be improved for optimal mobile user experience.",
                severity="Medium",
                evidence=f"HTTP response latency was {resp_time}s (recommended < 0.8s).",
                source="performance_scanner",
                recommendation="Review server-side processing, database execution plans, and page-level caching."
            ))
            deductions += 15.0

        # 2. HTML Payload Size Check
        html_size_kb = len(crawl_result.html.encode('utf-8')) / 1024.0
        if html_size_kb > 250:
            findings.append(NormalizedFinding(
                category="Performance",
                title="Large HTML Document Payload Size",
                description=f"The raw HTML payload size is {html_size_kb:.1f} KB, exceeding recommended guidelines.",
                severity="Medium",
                evidence=f"Raw HTML document size: {html_size_kb:.1f} KB (recommended < 100 KB).",
                source="performance_scanner",
                recommendation="Extract large inline CSS/JS scripts into external cached bundles and minify HTML markup."
            ))
            deductions += 20.0
        elif html_size_kb > 100:
            findings.append(NormalizedFinding(
                category="Performance",
                title="Moderate HTML Document Size",
                description=f"Base HTML document size is {html_size_kb:.1f} KB.",
                severity="Low",
                evidence=f"Raw HTML payload size: {html_size_kb:.1f} KB.",
                source="performance_scanner",
                recommendation="Enable Gzip/Brotli compression and remove redundant whitespace/comments."
            ))
            deductions += 10.0

        # 3. Render-Blocking Scripts in <head>
        head_tag = soup.find("head")
        render_blocking_scripts = []
        if head_tag:
            for s in head_tag.find_all("script", src=True):
                # Check if script lacks defer and async
                if not s.has_attr("defer") and not s.has_attr("async") and s.get("type") != "module":
                    render_blocking_scripts.append(s.get("src")[:50])

        if render_blocking_scripts:
            findings.append(NormalizedFinding(
                category="Performance",
                title="Render-Blocking Scripts in Document Head",
                description=f"Found {len(render_blocking_scripts)} script(s) in `<head>` without `defer` or `async`, delaying initial DOM paint.",
                severity="Medium",
                evidence=f"Render-blocking scripts: {render_blocking_scripts[:3]}",
                source="performance_scanner",
                recommendation="Add `defer` or `async` to scripts in `<head>`, or move non-critical scripts to the bottom of `<body>`."
            ))
            deductions += min(15.0, 5.0 * len(render_blocking_scripts))

        # 4. External Script and Stylesheet Count
        scripts = soup.find_all("script", src=True)
        stylesheets = soup.find_all("link", rel=lambda r: r and "stylesheet" in r)
        total_external_resources = len(scripts) + len(stylesheets) + len(crawl_result.images)

        if total_external_resources > 35:
            findings.append(NormalizedFinding(
                category="Performance",
                title="High External Resource Count",
                description=f"Discovered {total_external_resources} total asset requests (scripts, stylesheets, images).",
                severity="Medium",
                evidence=f"Breakdown: {len(scripts)} scripts, {len(stylesheets)} CSS files, {len(crawl_result.images)} images.",
                source="performance_scanner",
                recommendation="Bundle external JavaScript/CSS assets, use HTTP/2 multiplexing, and audit third-party tracker scripts."
            ))
            deductions += 15.0

        # 5. Unoptimized Images (Missing Lazy Loading)
        images_missing_lazy = [img.get("src", "img") for img in soup.find_all("img") if img.get("loading") != "lazy"]
        if len(images_missing_lazy) > 3:
            findings.append(NormalizedFinding(
                category="Performance",
                title="Images Missing Native Lazy Loading",
                description=f"{len(images_missing_lazy)} image(s) do not utilize the browser-native `loading=\"lazy\"` attribute.",
                severity="Low",
                evidence=f"Images lacking loading='lazy': {len(images_missing_lazy)} count. Examples: {images_missing_lazy[:2]}",
                source="performance_scanner",
                recommendation="Add `loading=\"lazy\"` to below-the-fold image tags to accelerate initial page rendering."
            ))
            deductions += 10.0

        score = max(0.0, min(100.0, 100.0 - deductions))
        return round(score, 1), findings
