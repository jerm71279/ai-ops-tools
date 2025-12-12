"""
Document Processor - Simplified stub version
Extracts text content from various document formats
"""
from pathlib import Path
from typing import Dict, Any


class DocumentProcessor:
    """Processes documents and extracts text content"""

    def __init__(self):
        print("✓ Document processor initialized")

    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a document file and extract content

        Returns structured data with:
        - raw_content: extracted text
        - metadata: file info
        - file_type: document type
        """
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}

        file_type = file_path.suffix.lower()

        # Route to appropriate processor
        if file_type == '.txt':
            content = self._process_txt(file_path)
        elif file_type == '.md':
            content = self._process_markdown(file_path)
        elif file_type == '.pdf':
            content = self._process_pdf(file_path)
        elif file_type in ['.doc', '.docx']:
            content = self._process_word(file_path)
        elif file_type in ['.html', '.htm']:
            content = self._process_html(file_path)
        else:
            content = f"Unsupported file type: {file_type}"

        return {
            "raw_content": content,
            "file_type": file_type,
            "filename": file_path.name,
            "size": file_path.stat().st_size,
            "metadata": {
                "source": str(file_path),
                "processed": True
            }
        }

    def _process_txt(self, file_path: Path) -> str:
        """Process plain text file"""
        return file_path.read_text(encoding='utf-8')

    def _process_markdown(self, file_path: Path) -> str:
        """Process markdown file"""
        return file_path.read_text(encoding='utf-8')

    def _process_pdf(self, file_path: Path) -> str:
        """Process PDF file"""
        try:
            import PyPDF2

            text = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text.append(page.extract_text())

            return '\n\n'.join(text)

        except ImportError:
            return f"[PDF processing requires PyPDF2. Install with: pip install PyPDF2]\n\nFile: {file_path.name}"
        except Exception as e:
            return f"[Error processing PDF: {e}]\n\nFile: {file_path.name}"

    def _process_word(self, file_path: Path) -> str:
        """Process Word document"""
        try:
            import docx

            doc = docx.Document(file_path)
            text = []

            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)

            return '\n\n'.join(text)

        except ImportError:
            return f"[Word processing requires python-docx. Install with: pip install python-docx]\n\nFile: {file_path.name}"
        except Exception as e:
            return f"[Error processing Word doc: {e}]\n\nFile: {file_path.name}"

    def _process_html(self, file_path: Path) -> str:
        """Process HTML file"""
        try:
            from bs4 import BeautifulSoup

            html_content = file_path.read_text(encoding='utf-8', errors='ignore')
            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get text content
            text = soup.get_text(separator='\n', strip=True)

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            # Try to extract title
            title = ""
            if soup.title and soup.title.string:
                title = f"Title: {soup.title.string.strip()}\n\n"

            return title + text

        except ImportError:
            # Fallback: basic HTML tag stripping without BeautifulSoup
            import re
            html_content = file_path.read_text(encoding='utf-8', errors='ignore')

            # Remove script and style tags with content
            html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

            # Remove HTML tags
            text = re.sub(r'<[^>]+>', ' ', html_content)

            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()

            return f"[Basic HTML parsing - install BeautifulSoup for better results: pip install beautifulsoup4]\n\n{text}"

        except Exception as e:
            return f"[Error processing HTML: {e}]\n\nFile: {file_path.name}"

    def batch_process(self, directory: Path) -> list:
        """Process all documents in a directory"""
        results = []

        supported_extensions = ['.txt', '.md', '.pdf', '.doc', '.docx', '.html', '.htm']

        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                result = self.process_file(file_path)
                results.append(result)

        return results
