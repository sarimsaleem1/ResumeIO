import requests
from bs4 import BeautifulSoup
import io
from xhtml2pdf import pisa
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ApplicationRunner:
    def __init__(self):
        self.base_url = "https://resume.io/api/app/resumes"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def get_resume_html(self, token):
        """Fetch resume HTML from resume.io API"""
        try:
            response = requests.get(f"{self.base_url}/{token}", headers=self.headers)
            response.raise_for_status()
            data = response.json()
            html_content = data.get("html", "")
            
            if not html_content:
                logger.error("No HTML content found in API response")
                return None
                
            return html_content
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching resume: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None
    
    def html_to_pdf(self, html_content):
        """Convert HTML content to PDF format"""
        try:
            pdf_bytes = io.BytesIO()
            pisa.CreatePDF(io.StringIO(html_content), dest=pdf_bytes)
            pdf_bytes.seek(0)
            return pdf_bytes.getvalue()
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            return None
    
    def html_to_docx(self, html_content):
        """Convert HTML content to DOCX format"""
        try:
            doc = Document()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Process HTML elements
            for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li', 'strong', 'em', 'u', 'a']):
                if element.name.startswith('h'):
                    # Handle headings
                    level = int(element.name[1])
                    heading = doc.add_heading('', level=level)
                    self._process_text_element(element, heading)
                
                elif element.name == 'p':
                    # Handle paragraphs
                    paragraph = doc.add_paragraph()
                    self._process_text_element(element, paragraph)
                
                elif element.name in ['ul', 'ol']:
                    # Handle lists
                    list_type = 'unordered' if element.name == 'ul' else 'ordered'
                    for li in element.find_all('li', recursive=False):
                        paragraph = doc.add_paragraph(
                            style='List Bullet' if list_type == 'unordered' else 'List Number'
                        )
                        self._process_text_element(li, paragraph)
            
            # Save to bytes
            doc_bytes = io.BytesIO()
            doc.save(doc_bytes)
            doc_bytes.seek(0)
            return doc_bytes.getvalue()
        except Exception as e:
            logger.error(f"Error generating DOCX: {str(e)}")
            return None
    
    def _process_text_element(self, element, doc_element):
        """Process text elements with formatting"""
        try:
            for child in element.children:
                if child.name is None:
                    # Plain text
                    run = doc_element.add_run(str(child))
                elif child.name == 'strong':
                    # Bold text
                    run = doc_element.add_run(child.get_text())
                    run.bold = True
                elif child.name == 'em':
                    # Italic text
                    run = doc_element.add_run(child.get_text())
                    run.italic = True
                elif child.name == 'u':
                    # Underlined text
                    run = doc_element.add_run(child.get_text())
                    run.underline = True
                elif child.name == 'a':
                    # Hyperlinks
                    run = doc_element.add_run(child.get_text())
                    run.underline = True
                    # Note: Adding actual hyperlinks requires more complex handling
                else:
                    # Other elements - process recursively
                    self._process_text_element(child, doc_element)
        except Exception as e:
            logger.error(f"Error processing text element: {str(e)}")
