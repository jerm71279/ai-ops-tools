#!/usr/bin/env python3
"""
Simple SharePoint processor - uses existing process_batch logic
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from process_batch import process_documents

# Process all SharePoint files by file type
sharepoint_dir = Path("input_documents/sharepoint_all")

print("=" * 70)
print("🚀 Processing ALL SharePoint Documents")
print("=" * 70)
print()

# Count files first
pdf_files = list(sharepoint_dir.rglob("*.pdf"))
docx_files = list(sharepoint_dir.rglob("*.docx"))
txt_files = list(sharepoint_dir.rglob("*.txt"))

print(f"📊 Files to process:")
print(f"   • {len(pdf_files)} PDFs")
print(f"   • {len(docx_files)} DOCX")
print(f"   • {len(txt_files)} TXT")
print(f"   Total: {len(pdf_files) + len(docx_files) + len(txt_files)}")
print()

# Process PDFs
print("\n" + "=" * 70)
print("📄 Processing PDF files...")
print("=" * 70)
process_documents("sharepoint_all/**/*.pdf")

# Process DOCX
print("\n" + "=" * 70)
print("📝 Processing DOCX files...")
print("=" * 70)
process_documents("sharepoint_all/**/*.docx")

# Process TXT
print("\n" + "=" * 70)
print("📋 Processing TXT files...")
print("=" * 70)
process_documents("sharepoint_all/**/*.txt")

print("\n" + "=" * 70)
print("✅ All SharePoint files processed!")
print("=" * 70)
