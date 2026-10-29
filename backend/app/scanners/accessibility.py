from bs4 import BeautifulSoup
from app.scanners.base import BaseScanner, NormalizedFinding

class AccessibilityScanner(BaseScanner):
    def scan(self, crawl_result) -> tuple[float, list[NormalizedFinding]]:
        findings = []
        deductions = 0.0
        soup = BeautifulSoup(crawl_result.html, "html.parser")

        # 1. Image Alt Attribute Check
        images_missing_alt = []
        suspicious_empty_alt = []
        for img in soup.find_all("img"):
            src = img.get("src", "unnamed image")
            if "alt" not in img.attrs or img["alt"] is None:
                images_missing_alt.append(src)
            elif img["alt"] == "" and (img.get("title") or "banner" in src.lower() or "hero" in src.lower()):
                suspicious_empty_alt.append(src)

        if images_missing_alt:
            severity = "High" if len(images_missing_alt) > 2 else "Medium"
            findings.append(NormalizedFinding(
                category="Accessibility",
                title="Images Missing Alt Text",
                description=f"Discovered {len(images_missing_alt)} image(s) lacking an `alt` attribute required by WCAG 2.2 Guideline 1.1.1.",
                severity=severity,
                evidence=f"{len(images_missing_alt)} <img> element(s) without alt tag. Examples: {images_missing_alt[:3]}",
                source="accessibility_scanner",
                recommendation="Provide concise, descriptive `alt` text for informative images or explicit `alt=\"\"` for purely decorative images."
            ))
            deductions += min(30.0, 10.0 * len(images_missing_alt))

        if suspicious_empty_alt:
            findings.append(NormalizedFinding(
                category="Accessibility",
                title="Potentially Informative Images with Empty Alt",
                description="Images that appear to convey significant content (e.g., banners/heroes) have empty `alt=\"\"` attributes.",
                severity="Low",
                evidence=f"Images with empty alt: {suspicious_empty_alt[:2]}",
                source="accessibility_scanner",
                recommendation="Verify whether these images are purely decorative. If informative, provide meaningful alternative text."
            ))
            deductions += 5.0

        # 2. Form Input Label Association Check
        unlabeled_inputs = []
        for inp in soup.find_all(["input", "textarea", "select"]):
            input_type = inp.get("type", "text").lower()
            if input_type in ["hidden", "submit", "button", "image", "reset"]:
                continue

            input_id = inp.get("id")
            has_label = False

            if input_id:
                label_for = soup.find("label", attrs={"for": input_id})
                if label_for and label_for.get_text(strip=True):
                    has_label = True

            if not has_label:
                # Check enclosing label with text
                parent_label = inp.find_parent("label")
                if parent_label and parent_label.get_text(strip=True):
                    has_label = True
                elif inp.get("aria-label", "").strip() or inp.get("aria-labelledby", "").strip() or inp.get("title", "").strip():
                    has_label = True

            if not has_label:
                unlabeled_inputs.append(inp.get("name") or input_id or f"<{inp.name} type='{input_type}'>")

        if unlabeled_inputs:
            findings.append(NormalizedFinding(
                category="Accessibility",
                title="Form Controls Missing Accessible Labels",
                description=f"Found {len(unlabeled_inputs)} form input element(s) without associated `<label>`, `aria-label`, or accessible names (WCAG 1.3.1 / 4.1.2).",
                severity="High",
                evidence=f"Form controls lacking labels: {unlabeled_inputs[:4]}",
                source="accessibility_scanner",
                recommendation="Associate each form input with an explicit `<label for=\"input_id\">` or add an `aria-label` attribute."
            ))
            deductions += min(25.0, 12.0 * len(unlabeled_inputs))

        # 3. HTML Document Language Attribute
        html_tag = soup.find("html")
        if not html_tag or not html_tag.get("lang"):
            findings.append(NormalizedFinding(
                category="Accessibility",
                title="Missing Language Attribute on <html> Element",
                description="The root `<html>` element does not specify a language `lang` attribute (WCAG 3.1.1 Language of Page).",
                severity="Medium",
                evidence="<html> tag missing lang attribute.",
                source="accessibility_scanner",
                recommendation="Add `lang=\"en\"` (or appropriate ISO 639-1 language code) to the `<html>` root element."
            ))
            deductions += 15.0

        # 4. Non-descriptive and Empty Link Text
        vague_link_texts = {"click here", "read more", "learn more", "more", "link", "here", "details", "go"}
        vague_links_found = []
        empty_links_found = []

        for a in soup.find_all("a"):
            text = a.get_text(strip=True)
            aria_label = a.get("aria-label", "").strip()
            title_attr = a.get("title", "").strip()
            accessible_name = text or aria_label or title_attr

            if not accessible_name:
                # Check for enclosed img with alt
                img_child = a.find("img")
                if not img_child or not img_child.get("alt"):
                    empty_links_found.append(a.get("href", "#")[:30])
            elif accessible_name.lower() in vague_link_texts:
                vague_links_found.append(accessible_name)

        if empty_links_found:
            findings.append(NormalizedFinding(
                category="Accessibility",
                title="Links Missing Accessible Name",
                description="Discovered hyperlinked elements with no readable inner text, image alt, or ARIA label (WCAG 2.4.4 Link Purpose).",
                severity="Medium",
                evidence=f"Empty link targets: {empty_links_found[:3]}",
                source="accessibility_scanner",
                recommendation="Ensure all links contain readable anchor text, an image with alt text, or an `aria-label`."
            ))
            deductions += 12.0

        if vague_links_found:
            findings.append(NormalizedFinding(
                category="Accessibility",
                title="Non-Descriptive Link Anchors",
                description="Links with generic text like 'click here' or 'read more' provide poor standalone context for screen readers.",
                severity="Low",
                evidence=f"Discovered links with generic text: {vague_links_found[:3]}",
                source="accessibility_scanner",
                recommendation="Replace generic text with meaningful link target descriptions (e.g., 'Read our security policy')."
            ))
            deductions += 8.0

        # 5. Buttons Missing Accessible Names
        unnamed_buttons = []
        for btn in soup.find_all("button"):
            btn_text = btn.get_text(strip=True)
            aria_label = btn.get("aria-label", "").strip()
            aria_labelledby = btn.get("aria-labelledby", "").strip()
            title_attr = btn.get("title", "").strip()
            if not btn_text and not aria_label and not aria_labelledby and not title_attr:
                unnamed_buttons.append(btn.get("id") or btn.get("class", ["button"])[0] if btn.get("class") else "button")

        if unnamed_buttons:
            findings.append(NormalizedFinding(
                category="Accessibility",
                title="Buttons Missing Accessible Text",
                description="Icon-only or blank buttons missing readable text, `aria-label`, or title (WCAG 4.1.2 Name, Role, Value).",
                severity="Medium",
                evidence=f"Found {len(unnamed_buttons)} button(s) without accessible text. Examples: {unnamed_buttons[:3]}",
                source="accessibility_scanner",
                recommendation="Add readable inner text, a descriptive `<svg><title>`, or an `aria-label` attribute to all `<button>` elements."
            ))
            deductions += 15.0

        # 6. Iframes Missing Title Attribute
        iframes_missing_title = [iframe.get("src", "embedded frame") for iframe in soup.find_all("iframe") if not iframe.get("title", "").strip()]
        if iframes_missing_title:
            findings.append(NormalizedFinding(
                category="Accessibility",
                title="iFrames Missing Title Attribute",
                description="Embedded `<iframe>` elements must have a descriptive `title` attribute for screen reader navigation (WCAG 4.1.2).",
                severity="Low",
                evidence=f"iFrames missing title: {iframes_missing_title[:2]}",
                source="accessibility_scanner",
                recommendation="Add a descriptive `title=\"...\"` attribute to all `<iframe>` elements to communicate their purpose."
            ))
            deductions += 5.0

        score = max(0.0, min(100.0, 100.0 - deductions))
        return round(score, 1), findings
