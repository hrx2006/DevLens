import time
import urllib.parse
from typing import List, Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup
from app.config import settings
from app.crawler.ssrf import is_safe_url

class CrawlResult:
    def __init__(
        self,
        url: str,
        status_code: int,
        title: str,
        html: str,
        links: List[str],
        images: List[Dict[str, Any]],
        response_time: float,
        headers: Optional[Dict[str, str]] = None,
        redirect_history: Optional[List[Dict[str, Any]]] = None,
        final_url: Optional[str] = None
    ):
        self.url = url
        self.status_code = status_code
        self.title = title
        self.html = html
        self.links = links
        self.images = images
        self.response_time = response_time
        self.headers = headers or {}
        self.redirect_history = redirect_history or []
        self.final_url = final_url or url
        self.is_https = self.final_url.lower().startswith("https://")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "final_url": self.final_url,
            "status_code": self.status_code,
            "title": self.title,
            "html": self.html,
            "links": self.links,
            "images": self.images,
            "response_time": self.response_time,
            "headers": self.headers,
            "redirect_history": self.redirect_history,
            "is_https": self.is_https
        }

def validate_url(url: str) -> bool:
    """Validate format and basic safety of URL."""
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        return False

    if (parsed.scheme or "").lower() not in ("http", "https"):
        return False
    if not parsed.netloc or not parsed.hostname:
        return False

    try:
        port = parsed.port
        if port is not None and not (1 <= port <= 65535):
            return False
    except ValueError:
        return False

    return True

class Crawler:
    def __init__(
        self,
        max_pages: int = settings.MAX_CRAWL_PAGES,
        timeout: float = float(settings.CRAWL_TIMEOUT),
        max_redirects: int = 5,
        max_response_bytes: int = settings.MAX_RESPONSE_BYTES
    ):
        self.max_pages = max_pages
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.max_response_bytes = max_response_bytes

    async def crawl(self, target_url: str) -> CrawlResult:
        target_url = target_url.strip()
        if not validate_url(target_url):
            raise ValueError("Invalid URL format. Please provide a valid HTTP or HTTPS URL.")

        # Check initial URL SSRF safety
        safe, reason = is_safe_url(target_url)
        if not safe:
            raise PermissionError(f"URL access rejected by SSRF protection: {reason}")

        start_time = time.time()
        headers = {
            "User-Agent": "DevLensAI-AuditBot/1.0 (+https://devlens.ai; Website Quality Assurance Bot)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        current_url = target_url
        redirect_history = []
        visited_urls = {current_url}
        final_response = None
        html_content = ""

        # Safe HTTP client with manual redirect validation to prevent redirect-based SSRF
        timeout_config = httpx.Timeout(self.timeout, connect=min(10.0, self.timeout))
        async with httpx.AsyncClient(
            timeout=timeout_config,
            follow_redirects=False,
            verify=False  # Allows inspecting self-signed certs for testing; verification logic is in security scanner
        ) as client:
            for hop in range(self.max_redirects + 1):
                try:
                    # Stream response to enforce size limits
                    async with client.stream("GET", current_url, headers=headers) as resp:
                        # Record redirect if 3xx
                        if resp.is_redirect:
                            if hop >= self.max_redirects:
                                raise ConnectionError(f"Exceeded maximum redirect limit of {self.max_redirects} hops.")

                            loc = resp.headers.get("location")
                            if not loc:
                                raise ConnectionError("Redirect response missing 'Location' header.")

                            redirect_url = urllib.parse.urljoin(current_url, loc)
                            if redirect_url in visited_urls:
                                raise ConnectionError(f"Redirect loop detected: destination '{redirect_url}' was already visited.")

                            visited_urls.add(redirect_url)
                            redirect_history.append({
                                "status_code": resp.status_code,
                                "from_url": current_url,
                                "to_url": redirect_url
                            })

                            # Crucial: re-validate the redirect destination before following
                            redirect_safe, redirect_reason = is_safe_url(redirect_url)
                            if not redirect_safe:
                                raise PermissionError(f"Redirect to prohibited destination blocked: {redirect_reason}")

                            current_url = redirect_url
                            continue

                        # Read body safely up to max_response_bytes
                        final_response = resp
                        raw_body = bytearray()
                        async for chunk in resp.aiter_bytes():
                            raw_body.extend(chunk)
                            if len(raw_body) > self.max_response_bytes:
                                break  # Cap reading at max bytes

                        html_content = raw_body.decode(resp.encoding or "utf-8", errors="replace")
                        break

                except httpx.TimeoutException:
                    raise TimeoutError(f"The website at {current_url} took too long to respond (timeout).")
                except (PermissionError, ConnectionError):
                    raise
                except httpx.RequestError as e:
                    raise ConnectionError(f"Unable to connect to website {current_url}: {str(e)}")

        response_time = round(time.time() - start_time, 3)

        if not final_response:
            raise ConnectionError(f"Failed to retrieve content from {target_url}: No valid response obtained.")

        status_code = final_response.status_code
        resp_headers = dict(final_response.headers)

        soup = BeautifulSoup(html_content, "html.parser")

        # Extract Title
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""

        # Extract Links
        links_set = set()
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            absolute_link = urllib.parse.urljoin(current_url, href)
            parsed_link = urllib.parse.urlparse(absolute_link)
            if parsed_link.scheme in ["http", "https"]:
                links_set.add(absolute_link)
            if len(links_set) >= self.max_pages * 3:
                break

        # Extract Images
        images = []
        for img in soup.find_all("img"):
            src = img.get("src", "").strip()
            alt = img.get("alt", None)
            loading = img.get("loading", None)
            if src:
                abs_src = urllib.parse.urljoin(current_url, src)
                images.append({"src": abs_src, "alt": alt, "loading": loading})

        return CrawlResult(
            url=target_url,
            status_code=status_code,
            title=title,
            html=html_content,
            links=list(links_set),
            images=images,
            response_time=response_time,
            headers=resp_headers,
            redirect_history=redirect_history,
            final_url=current_url
        )
