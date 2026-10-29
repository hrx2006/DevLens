import urllib.parse
from bs4 import BeautifulSoup
from app.scanners.base import BaseScanner, NormalizedFinding

class SEOScanner(BaseScanner):
    def scan(self, crawl_result) -> tuple[float, list[NormalizedFinding]]:
        findings = []
        deductions = 0.0
        soup = BeautifulSoup(crawl_result.html, "html.parser")

        # 1. Page Title Check
        title = crawl_result.title
        if not title:
            findings.append(NormalizedFinding(
                category="SEO",
                title="Missing Page Title",
                description="The page lacks a `<title>` tag in its HTML header.",
                severity="High",
                evidence="<title> tag was not found in the HTML document.",
                source="seo_scanner",
                recommendation="Add a descriptive `<title>` tag (30-60 characters) inside the `<head>` section."
            ))
            deductions += 25.0
        elif len(title) < 10:
            findings.append(NormalizedFinding(
                category="SEO",
                title="Short Page Title",
                description="The page title is very short (< 10 characters) and may not provide sufficient context for search engine indexes.",
                severity="Low",
                evidence=f"Current title: '{title}' ({len(title)} characters).",
                source="seo_scanner",
                recommendation="Expand the title tag to clearly summarize page topic (aim for 30-60 characters)."
            ))
            deductions += 8.0
        elif len(title) > 65:
            findings.append(NormalizedFinding(
                category="SEO",
                title="Excessively Long Page Title",
                description="Page title exceeds 65 characters and is likely to be truncated on search engine results pages (SERPs).",
                severity="Low",
                evidence=f"Current title length: {len(title)} characters (recommended <= 60 characters).",
                source="seo_scanner",
                recommendation="Condense the title to keep key keywords within the initial 50-60 characters."
            ))
            deductions += 5.0

        # 2. Meta Description Check
        meta_desc = soup.find("meta", attrs={"name": lambda x: x and x.lower() == "description"})
        desc_content = meta_desc.get("content", "").strip() if meta_desc else ""
        if not desc_content:
            findings.append(NormalizedFinding(
                category="SEO",
                title="Missing Meta Description",
                description="The page does not contain a meta description tag.",
                severity="Medium",
                evidence="meta[name='description'] was not found or has empty content.",
                source="seo_scanner",
                recommendation="Add a concise `<meta name=\"description\" content=\"...\">` tag summarizing the page (120-160 characters)."
            ))
            deductions += 20.0
        elif len(desc_content) < 50:
            findings.append(NormalizedFinding(
                category="SEO",
                title="Short Meta Description",
                description="Meta description is shorter than 50 characters, potentially underutilizing SERP snippet real estate.",
                severity="Low",
                evidence=f"Meta description is {len(desc_content)} characters.",
                source="seo_scanner",
                recommendation="Expand meta description to between 120 and 160 characters to entice click-throughs."
            ))
            deductions += 5.0
        elif len(desc_content) > 165:
            findings.append(NormalizedFinding(
                category="SEO",
                title="Overly Long Meta Description",
                description="Meta description exceeds 165 characters and may be clipped in search engine snippets.",
                severity="Low",
                evidence=f"Meta description length is {len(desc_content)} characters.",
                source="seo_scanner",
                recommendation="Keep primary description messaging within 150-160 characters."
            ))
            deductions += 5.0

        # 3. Headings Hierarchy Check
        h1_tags = soup.find_all("h1")
        if len(h1_tags) == 0:
            findings.append(NormalizedFinding(
                category="SEO",
                title="Missing H1 Heading",
                description="The page does not contain an `<h1>` heading tag.",
                severity="Medium",
                evidence="No <h1> tag discovered in the document structure.",
                source="seo_scanner",
                recommendation="Include a single primary `<h1>` heading tag that represents the main topic of the page."
            ))
            deductions += 15.0
        elif len(h1_tags) > 1:
            findings.append(NormalizedFinding(
                category="SEO",
                title="Multiple H1 Headings Detected",
                description="Multiple `<h1>` tags were found on a single page, which can dilute semantic hierarchy.",
                severity="Low",
                evidence=f"Found {len(h1_tags)} <h1> elements on the page.",
                source="seo_scanner",
                recommendation="Structure your page hierarchy with one primary `<h1>` tag and use `<h2>` to `<h6>` for sub-sections."
            ))
            deductions += 8.0

        # Check for heading hierarchy level skips (e.g., h1 then h3 without h2)
        all_headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        skipped_levels = False
        prev_level = 0
        for h in all_headings:
            curr_level = int(h.name[1])
            if prev_level > 0 and curr_level > prev_level + 1:
                skipped_levels = True
                break
            prev_level = curr_level

        if skipped_levels:
            findings.append(NormalizedFinding(
                category="SEO",
                title="Skipped Heading Levels",
                description="Heading tags skip hierarchical levels (e.g. h1 directly followed by h3), which confuses outline parsing.",
                severity="Low",
                evidence="Discovered non-consecutive heading level increments.",
                source="seo_scanner",
                recommendation="Maintain sequential heading levels (h1 -> h2 -> h3) without skipping intermediate levels."
            ))
            deductions += 5.0

        # 4. Canonical Tag Check
        canonical_tag = soup.find("link", attrs={"rel": lambda x: x and "canonical" in x})
        if not canonical_tag or not canonical_tag.get("href"):
            findings.append(NormalizedFinding(
                category="SEO",
                title="Missing Canonical Link Tag",
                description="No canonical link header was defined for this page.",
                severity="Low",
                evidence="link[rel='canonical'] was not found in <head>.",
                source="seo_scanner",
                recommendation="Add `<link rel=\"canonical\" href=\"YOUR_URL\" />` to prevent duplicate content indexing issues."
            ))
            deductions += 8.0
        else:
            canonical_href = canonical_tag.get("href", "").strip()
            parsed_canonical = urllib.parse.urlparse(canonical_href)
            if not parsed_canonical.scheme or not parsed_canonical.netloc:
                findings.append(NormalizedFinding(
                    category="SEO",
                    title="Relative or Malformed Canonical URL",
                    description="The canonical link tag specifies a relative or malformed URL instead of an absolute canonical address.",
                    severity="Low",
                    evidence=f"Current canonical href: '{canonical_href}'",
                    source="seo_scanner",
                    recommendation="Always use absolute URLs (e.g. https://example.com/page) in canonical tags."
                ))
                deductions += 5.0

        # 5. Robots Meta Directive Check
        robots_meta = soup.find("meta", attrs={"name": lambda x: x and x.lower() == "robots"})
        if robots_meta and robots_meta.get("content"):
            content_lower = robots_meta.get("content", "").lower()
            if "noindex" in content_lower:
                findings.append(NormalizedFinding(
                    category="SEO",
                    title="Page Has 'noindex' Directive",
                    description="Search engines are explicitly instructed not to index this page via a robots meta tag.",
                    severity="Medium",
                    evidence=f"robots meta content: '{robots_meta.get('content')}'",
                    source="seo_scanner",
                    recommendation="Ensure 'noindex' is intentional. Remove it if this page should appear in organic search results."
                ))
                deductions += 10.0

        # 6. Open Graph Meta Tags Check
        og_title = soup.find("meta", attrs={"property": "og:title"})
        og_desc = soup.find("meta", attrs={"property": "og:description"})
        og_image = soup.find("meta", attrs={"property": "og:image"})

        missing_og = []
        if not og_title: missing_og.append("og:title")
        if not og_desc: missing_og.append("og:description")
        if not og_image: missing_og.append("og:image")

        if missing_og:
            findings.append(NormalizedFinding(
                category="SEO",
                title="Incomplete Open Graph Social Metadata",
                description=f"Social sharing metadata is missing: {', '.join(missing_og)}.",
                severity="Info",
                evidence=f"Missing tags: {missing_og}",
                source="seo_scanner",
                recommendation="Include `og:title`, `og:description`, and `og:image` tags for rich link previews across social platforms."
            ))
            deductions += 3.0

        score = max(0.0, min(100.0, 100.0 - deductions))
        return round(score, 1), findings
