import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

#!/usr/bin/env python3
"""
HTML Document Generator - Creates OberaConnect branded HTML documents
Uses the official template with logo header
"""
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Logo path for Windows
LOGO_PATH = "file:///C:/Users/JeremySmith/OneDrive%20-%20Obera%20Connect/Pictures/Screenshots/OberaConnect%20logo.png"


def generate_html_document(structured_data: Dict[str, Any], output_path: Path = None) -> str:
    """
    Generate an OberaConnect branded HTML document from structured data

    Args:
        structured_data: Document data with title, key_data, tags, etc.
        output_path: Optional path to save the HTML file

    Returns:
        HTML content string
    """
    title = structured_data.get('title', 'Untitled Document')
    date = datetime.now().strftime('%m/%d/%Y')

    # Build executive summary from metadata
    doc_type = structured_data.get('document_type', 'document')
    customer = structured_data.get('customer', '')
    technology = structured_data.get('technology', '')

    summary_parts = []
    if doc_type and doc_type != 'unknown':
        summary_parts.append(f"Document Type: {doc_type}")
    if customer and customer != 'unknown':
        summary_parts.append(f"Customer: {customer}")
    if technology:
        summary_parts.append(f"Technology: {technology}")

    executive_summary = "<br>".join(summary_parts) if summary_parts else "No summary available."

    # Build key data section
    key_data = structured_data.get('key_data', {})
    key_data_html = ""
    if key_data:
        key_data_html = "\n".join([
            f'<li><strong>{k}:</strong> {v}</li>'
            for k, v in key_data.items()
        ])
    else:
        key_data_html = "<li>No key data extracted</li>"

    # Build tags
    tags = structured_data.get('tags', [])
    tags_html = ", ".join(tags) if tags else "None"

    # Source preview
    raw_content = structured_data.get('raw_content', '')
    source_preview = raw_content[:500] if raw_content else "No source content available."

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333333;
            max-width: 8.5in;
            margin: 0 auto;
            padding: 0.5in;
            background: #fff;
        }}

        .header {{
            border-bottom: 3px solid #0066CC;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}

        .logo-container {{
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }}

        .logo-img {{
            height: 50px;
            width: auto;
        }}

        .tagline {{
            font-size: 14px;
            color: #666666;
            font-style: italic;
            margin-left: 2px;
        }}

        .doc-meta {{
            margin-top: 20px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }}

        .doc-title {{
            font-size: 24px;
            font-weight: 600;
            color: #333333;
        }}

        .doc-date {{
            font-size: 12px;
            color: #666666;
        }}

        .section {{
            margin-bottom: 25px;
        }}

        .section-title {{
            font-size: 18px;
            font-weight: 600;
            color: #0066CC;
            border-bottom: 1px solid #e0e0e0;
            padding-bottom: 8px;
            margin-bottom: 15px;
        }}

        .section-content {{
            color: #333333;
            font-size: 14px;
        }}

        .section-content p {{
            margin-bottom: 10px;
        }}

        .section-content ul {{
            margin-left: 20px;
            margin-bottom: 10px;
        }}

        .section-content li {{
            margin-bottom: 5px;
        }}

        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            font-size: 11px;
            color: #999999;
            text-align: center;
        }}

        .highlight-box {{
            background: #f5f9ff;
            border-left: 4px solid #0066CC;
            padding: 15px;
            margin: 15px 0;
        }}

        .tags {{
            font-size: 12px;
            color: #666;
            margin-top: 10px;
        }}

        .source-preview {{
            background: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 12px;
            white-space: pre-wrap;
            max-height: 200px;
            overflow-y: auto;
        }}

        @media print {{
            body {{
                padding: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo-container">
            <img src="{LOGO_PATH}" alt="OberaConnect" class="logo-img">
        </div>
        <div class="tagline">Technology Solutions for Modern Business</div>

        <div class="doc-meta">
            <div class="doc-title">{title}</div>
            <div class="doc-date">Date: {date}</div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">Executive Summary</div>
        <div class="section-content">
            <p>{executive_summary}</p>
            <div class="tags"><strong>Tags:</strong> {tags_html}</div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">Key Data</div>
        <div class="section-content">
            <ul>
                {key_data_html}
            </ul>
        </div>
    </div>

    <div class="section">
        <div class="section-title">Source Preview</div>
        <div class="section-content">
            <div class="source-preview">{source_preview}</div>
        </div>
    </div>

    <div class="footer">
        OberaConnect LLC | www.oberaconnect.com | Generated by SecondBrain
    </div>
</body>
</html>'''

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding='utf-8')
        print(f"Generated HTML: {output_path}")

    return html


def batch_generate_html(notes_dir: Path, output_dir: Path) -> int:
    """
    Generate HTML documents for all markdown notes in a directory

    Args:
        notes_dir: Directory containing markdown notes
        output_dir: Directory to save HTML files

    Returns:
        Number of files generated
    """
    import re

    output_dir.mkdir(parents=True, exist_ok=True)
    generated = 0

    for md_file in notes_dir.rglob("*.md"):
        try:
            content = md_file.read_text(encoding='utf-8')

            # Parse frontmatter
            frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if not frontmatter_match:
                continue

            frontmatter = frontmatter_match.group(1)

            # Extract metadata
            structured_data = {}

            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    if key == 'tags':
                        structured_data['tags'] = [t.strip() for t in value.split(',')]
                    else:
                        structured_data[key] = value

            # Get any remaining content as raw_content
            body_start = content.find('---', 3) + 3
            body = content[body_start:].strip()
            structured_data['raw_content'] = body[:500]

            # Generate HTML
            html_filename = md_file.stem + '.html'
            html_path = output_dir / html_filename

            generate_html_document(structured_data, html_path)
            generated += 1

        except Exception as e:
            print(f"Error processing {md_file.name}: {e}")

    return generated


if __name__ == "__main__":
    # Example usage
    sample_data = {
        "title": "SonicWall Configuration - Freeport",
        "document_type": "config",
        "customer": "City of Freeport",
        "technology": "SonicWall",
        "tags": ["customer/freeport", "tech/sonicwall", "network/firewall"],
        "key_data": {
            "WAN IP": "192.168.1.1",
            "LAN Subnet": "10.0.0.0/24",
            "Contact": "IT Admin"
        },
        "raw_content": "Firewall configuration for City of Freeport main office. Includes VPN settings and access rules..."
    }

    output = Path("/home/mavrick/Projects/Secondbrain/output_html")
    html = generate_html_document(sample_data, output / "sample_document.html")
    print(f"Sample document generated at: {output / 'sample_document.html'}")
