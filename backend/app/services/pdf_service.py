import io
import xml.sax.saxutils
from datetime import datetime
from typing import List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from app.db.models import AuditModel

def _safe_escape(text: str) -> str:
    """Escapes XML entities so arbitrary HTML code in recommendations or evidence doesn't break ReportLab."""
    if not text:
        return ""
    return xml.sax.saxutils.escape(str(text))

class PDFReportService:
    @staticmethod
    def generate_audit_pdf(audit: AuditModel) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()

        brand_color = colors.HexColor("#0f172a")     # Slate 900
        primary_blue = colors.HexColor("#2563eb")    # Blue 600
        text_dark = colors.HexColor("#1e293b")       # Slate 800
        text_muted = colors.HexColor("#64748b")      # Slate 500
        border_color = colors.HexColor("#e2e8f0")    # Slate 200

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=brand_color
        )

        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=text_muted
        )

        heading2_style = ParagraphStyle(
            "DocH2",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=brand_color,
            spaceBefore=12,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            "DocBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=text_dark
        )

        body_bold = ParagraphStyle(
            "DocBodyBold",
            parent=body_style,
            fontName="Helvetica-Bold"
        )

        code_style = ParagraphStyle(
            "DocCode",
            parent=styles["Normal"],
            fontName="Courier",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#047857"),  # Emerald 700
            backColor=colors.HexColor("#f1f5f9"),
            borderPadding=4
        )

        story = []

        # 1. Header Banner
        header_table = Table(
            [
                [
                    Paragraph("<b>DevLens <font color='#2563eb'>AI</font></b>", title_style),
                    Paragraph(f"<b>Audit Report #{audit.id}</b><br/>{datetime.now().strftime('%B %d, %Y')}", subtitle_style)
                ]
            ],
            colWidths=[4.0 * inch, 3.2 * inch]
        )
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1.5, color=primary_blue, spaceBefore=4, spaceAfter=14))

        # 2. Executive Overview Summary Box
        ai_engine_name = getattr(audit, "ai_source", None) or "Deterministic Fallback Engine"
        overview_data = [
            [Paragraph("<b>Target Website:</b>", body_bold), Paragraph(_safe_escape(audit.url), body_style)],
            [Paragraph("<b>Audit Date:</b>", body_bold), Paragraph(audit.created_at.strftime('%Y-%m-%d %H:%M:%S UTC') if audit.created_at else "N/A", body_style)],
            [Paragraph("<b>Audit Status:</b>", body_bold), Paragraph(f"<font color='#059669'><b>{audit.status.upper()}</b></font>", body_style)],
            [Paragraph("<b>Reasoning Engine:</b>", body_bold), Paragraph(_safe_escape(ai_engine_name), body_style)],
            [Paragraph("<b>Overall Health Score:</b>", body_bold), Paragraph(f"<b>{round(audit.overall_score, 1)} / 100</b>", body_bold)],
        ]
        overview_table = Table(overview_data, colWidths=[2.2 * inch, 5.0 * inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 1, border_color),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(overview_table)
        story.append(Spacer(1, 14))

        # 3. 5-Category Score Breakdown
        story.append(Paragraph("Category Performance Breakdown", heading2_style))
        scores_data = [
            ["Audit Category", "Score", "Rating", "Scope Tested"],
            ["SEO", f"{round(audit.seo_score, 1)} / 100", "Good" if audit.seo_score >= 80 else "Attention" if audit.seo_score >= 60 else "Critical", "Title, meta tags, heading hierarchy, canonical links, robots tags"],
            ["Accessibility", f"{round(audit.accessibility_score, 1)} / 100", "Good" if audit.accessibility_score >= 80 else "Attention" if audit.accessibility_score >= 60 else "Critical", "WCAG 2.2 image alts, input labels, button text, page language"],
            ["Performance", f"{round(audit.performance_score, 1)} / 100", "Good" if audit.performance_score >= 80 else "Attention" if audit.performance_score >= 60 else "Critical", "Latency, payload size, asset counts, render-blocking scripts"],
            ["Security", f"{round(audit.security_score, 1)} / 100", "Good" if audit.security_score >= 80 else "Attention" if audit.security_score >= 60 else "Critical", "HTTPS enforcement, HSTS, CSP, nosniff, Clickjacking, mixed-content"],
            ["Functionality", f"{round(audit.functionality_score, 1)} / 100", "Good" if audit.functionality_score >= 80 else "Attention" if audit.functionality_score >= 60 else "Critical", "Broken links, form action/method hygiene, password-over-GET detection"]
        ]

        scores_table = Table(scores_data, colWidths=[1.4 * inch, 1.0 * inch, 1.0 * inch, 3.8 * inch])
        scores_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('ALIGN', (1, 0), (2, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4.5),
            ('TOPPADDING', (0, 0), (-1, -1), 4.5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ('BOX', (0, 0), (-1, -1), 1, border_color),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ]))
        story.append(scores_table)
        story.append(Spacer(1, 14))

        # 4. Severity Distribution Summary
        severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Info": 0}
        for iss in audit.issues:
            sev = iss.severity if iss.severity in severity_counts else "Medium"
            severity_counts[sev] += 1

        story.append(Paragraph(f"Detected Issues Summary ({len(audit.issues)} Total)", heading2_style))
        sev_data = [
            ["Critical Severity", "High Severity", "Medium Severity", "Low Severity", "Informational"],
            [
                f"<font color='#be123c'><b>{severity_counts['Critical']}</b></font>",
                f"<font color='#d97706'><b>{severity_counts['High']}</b></font>",
                f"<font color='#b45309'><b>{severity_counts['Medium']}</b></font>",
                f"<font color='#2563eb'><b>{severity_counts['Low']}</b></font>",
                f"<font color='#475569'><b>{severity_counts['Info']}</b></font>"
            ]
        ]
        sev_table = Table([[Paragraph(c, body_style) for c in sev_data[0]], [Paragraph(c, body_style) for c in sev_data[1]]], colWidths=[1.44 * inch] * 5)
        sev_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOX', (0, 0), (-1, -1), 1, border_color),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(sev_table)
        story.append(Spacer(1, 14))

        # 5. Detailed Findings & AI Explanations
        story.append(Paragraph("Detailed Technical Findings & Remediation", heading2_style))

        if not audit.issues:
            story.append(Paragraph("<i>No technical issues were discovered for this website.</i>", body_style))
        else:
            for idx, issue in enumerate(audit.issues, 1):
                sev_color = "#e11d48" if issue.severity == "Critical" else "#d97706" if issue.severity == "High" else "#2563eb"
                issue_box = [
                    [
                        Paragraph(f"<b>#{idx}. {_safe_escape(issue.title)}</b>", body_bold),
                        Paragraph(f"<font color='{sev_color}'><b>{_safe_escape(issue.severity).upper()}</b></font> | Priority: {issue.priority}/100 | {_safe_escape(issue.category)}", subtitle_style)
                    ],
                    [
                        Paragraph("<b>Evidence:</b>", body_bold),
                        Paragraph(_safe_escape(issue.evidence or "No raw snippet evidence recorded."), code_style)
                    ],
                    [
                        Paragraph("<b>AI Root Cause:</b>", body_bold),
                        Paragraph(_safe_escape(issue.root_cause or issue.description or "Based on scanner evidence."), body_style)
                    ],
                    [
                        Paragraph("<b>User Impact:</b>", body_bold),
                        Paragraph(_safe_escape(issue.user_impact or "Impairs website performance and visitor experience."), body_style)
                    ],
                    [
                        Paragraph("<b>Recommendation:</b>", body_bold),
                        Paragraph(_safe_escape(issue.recommendation or "Follow web quality guidelines."), body_style)
                    ],
                ]

                issue_table = Table(issue_box, colWidths=[1.6 * inch, 5.6 * inch])
                issue_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                    ('BOX', (0, 0), (-1, -1), 1, border_color),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ]))

                story.append(KeepTogether([issue_table, Spacer(1, 8)]))

        # 6. Audit Methodology & Disclaimer Footer
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceBefore=4, spaceAfter=8))
        disclaimer = (
            "<b>Methodology & Limitations:</b> DevLens AI combines passive, deterministic scanner heuristics (SEO, WCAG 2.2, "
            "DOM structure, HTTP security headers, transport encryption) with Google Gemini AI reasoning. Automated scans provide "
            "actionable diagnostics but do not replace exhaustive manual penetration testing or human WCAG assistive-technology audits."
        )
        story.append(Paragraph(disclaimer, subtitle_style))

        # Build PDF document
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

pdf_service = PDFReportService()
