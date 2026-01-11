#!/usr/bin/env python3
"""
Workflow Documentation Exporter

Converts Markdown workflow documentation to PDF, HTML, or Word formats.

Usage:
    python3 export-workflow.py --input workflow.md --format pdf
    python3 export-workflow.py --input workflows/ --format html --batch
    python3 export-workflow.py --input workflow.md --format all

Requirements:
    pip install markdown2 weasyprint python-docx
    # OR use pandoc (recommended):
    sudo apt-get install pandoc texlive-xetex  # Linux
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path
from typing import List

def check_pandoc():
    """Check if pandoc is installed"""
    try:
        result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def export_with_pandoc(input_file: Path, output_format: str, output_file: Path):
    """Export using pandoc (recommended method)"""

    format_options = {
        'pdf': ['--pdf-engine=xelatex', '--embed-resources'],
        'html': ['--self-contained', '--css=style.css'],
        'docx': [],
        'word': []  # alias for docx
    }

    if output_format == 'word':
        output_format = 'docx'

    cmd = ['pandoc', str(input_file), '-o', str(output_file)]

    # Add format-specific options
    if output_format in format_options:
        cmd.extend(format_options[output_format])

    try:
        print(f"Converting {input_file.name} to {output_format.upper()}...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✓ Exported: {output_file}")
            return True
        else:
            print(f"✗ Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error exporting: {e}")
        return False

def export_with_python(input_file: Path, output_format: str, output_file: Path):
    """Export using Python libraries (fallback method)"""

    try:
        import markdown2
    except ImportError:
        print("Error: markdown2 not installed. Install with: pip install markdown2")
        return False

    # Read markdown content
    with open(input_file, 'r') as f:
        md_content = f.read()

    if output_format == 'html':
        # Convert to HTML
        html_content = markdown2.markdown(md_content, extras=['tables', 'fenced-code-blocks'])

        # Wrap in HTML document
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{input_file.stem}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        img {{
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 5px;
            margin: 10px 0;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        pre {{
            background: #f4f4f4;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f4f4f4;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

        with open(output_file, 'w') as f:
            f.write(full_html)

        print(f"✓ Exported: {output_file}")
        return True

    elif output_format == 'pdf':
        print("PDF export requires pandoc. Install with:")
        print("  sudo apt-get install pandoc texlive-xetex")
        return False

    elif output_format in ['docx', 'word']:
        print("Word export requires pandoc. Install with:")
        print("  sudo apt-get install pandoc")
        return False

    return False

def export_workflow(input_file: Path, output_format: str, output_dir: Path = None):
    """Export a single workflow file"""

    if not input_file.exists():
        print(f"Error: File not found: {input_file}")
        return False

    # Determine output directory
    if output_dir is None:
        output_dir = input_file.parent.parent / 'exports'

    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine output file extension
    ext_map = {
        'pdf': '.pdf',
        'html': '.html',
        'docx': '.docx',
        'word': '.docx'
    }

    output_file = output_dir / f"{input_file.stem}{ext_map.get(output_format, '.txt')}"

    # Try pandoc first (recommended), fallback to Python libraries
    if check_pandoc():
        return export_with_pandoc(input_file, output_format, output_file)
    else:
        print("Warning: pandoc not found. Using fallback Python export (limited features)")
        print("For best results, install pandoc:")
        print("  sudo apt-get install pandoc texlive-xetex\n")
        return export_with_python(input_file, output_format, output_file)

def batch_export(input_dir: Path, output_format: str, output_dir: Path = None):
    """Export all Markdown files in a directory"""

    if not input_dir.is_dir():
        print(f"Error: Directory not found: {input_dir}")
        return

    md_files = list(input_dir.glob('*.md'))

    if not md_files:
        print(f"No Markdown files found in: {input_dir}")
        return

    print(f"\nFound {len(md_files)} Markdown files to export\n")

    success_count = 0
    for md_file in md_files:
        if export_workflow(md_file, output_format, output_dir):
            success_count += 1

    print(f"\n{'='*60}")
    print(f"Batch export complete: {success_count}/{len(md_files)} successful")
    print(f"{'='*60}\n")

def main():
    parser = argparse.ArgumentParser(
        description="Export workflow documentation to multiple formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export single file to PDF
  python3 export-workflow.py --input documentation/workflows/unifi-setup.md --format pdf

  # Export to HTML
  python3 export-workflow.py --input documentation/workflows/backup-process.md --format html

  # Export all workflows in a directory
  python3 export-workflow.py --input documentation/workflows/ --format pdf --batch

  # Export to all formats
  python3 export-workflow.py --input workflow.md --format all

Formats:
  pdf   - PDF document (requires pandoc + texlive-xetex)
  html  - Self-contained HTML file
  docx  - Microsoft Word document (requires pandoc)
  all   - Export to all formats

Installation:
  sudo apt-get install pandoc texlive-xetex
  pip install markdown2
        """
    )

    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input Markdown file or directory'
    )

    parser.add_argument(
        '--format', '-f',
        choices=['pdf', 'html', 'docx', 'word', 'all'],
        default='pdf',
        help='Output format (default: pdf)'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output directory (default: documentation/exports)'
    )

    parser.add_argument(
        '--batch', '-b',
        action='store_true',
        help='Batch export all .md files in input directory'
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output) if args.output else None

    # Handle "all" format
    if args.format == 'all':
        formats = ['pdf', 'html', 'docx']
        for fmt in formats:
            print(f"\n{'='*60}")
            print(f"Exporting to {fmt.upper()}")
            print(f"{'='*60}\n")
            if args.batch or input_path.is_dir():
                batch_export(input_path, fmt, output_dir)
            else:
                export_workflow(input_path, fmt, output_dir)
    else:
        # Single format export
        if args.batch or input_path.is_dir():
            batch_export(input_path, args.format, output_dir)
        else:
            export_workflow(input_path, args.format, output_dir)

if __name__ == "__main__":
    main()
