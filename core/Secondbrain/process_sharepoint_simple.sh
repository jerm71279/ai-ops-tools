#!/bin/bash
# Process all SharePoint documents

cd /home/mavrick/Projects/Secondbrain

echo "Processing SharePoint PDFs..."
./venv/bin/python - <<'PYTHON'
from pathlib import Path
from process_batch import process_documents

# Change to input_documents directory
import os
os.chdir('input_documents')

# Process SharePoint PDFs
process_documents("sharepoint/**/*.pdf")
PYTHON

echo "Processing SharePoint DOCX files..."
./venv/bin/python - <<'PYTHON'
from pathlib import Path
from process_batch import process_documents

# Change to input_documents directory
import os
os.chdir('input_documents')

# Process SharePoint DOCX files
process_documents("sharepoint/**/*.docx")
PYTHON

echo "Done!"
