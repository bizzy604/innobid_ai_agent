from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, List, Dict, Union, Any, Optional
import requests
import PyPDF2
import io
import time
import json
import os
import hashlib
from docx import Document
from bs4 import BeautifulSoup
from datetime import datetime

class PDFReaderInput(BaseModel):
    """Input schema for PDFReaderTool."""
    bid_data: Dict[str, Any] = Field(..., description="Bid data containing document information")

class PDFReaderTool(BaseTool):
    name: str = "PDF Reader Tool"
    description: str = "Reads text from multiple document types (PDF, DOCX, HTML, TXT) in bid data"
    args_schema: Type[BaseModel] = PDFReaderInput

    def _run(self, bid_data: Dict[str, Any]) -> Dict[str, str]:
        """Reads and processes all documents from bid data."""
        try:
            # Create cache directory if it doesn't exist
            cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
                
            # Extract document URLs from the bid data
            documents = bid_data.get('documents', [])
            
            # Dictionary to store results
            results = {}
            errors = []
            
            # Track processing stats
            total_docs = len(documents)
            processed_docs = 0
            start_time = time.time()
            
            # Process each document
            for doc in documents:
                doc_type = doc.get('type', '').lower()
                url = doc.get('url')
                name = doc.get('name', f"Document_{len(results) + 1}")
                
                if not url:
                    continue
                    
                try:
                    print(f"Processing document: {name} ({doc_type}) from {url}")
                    content = process_document(url, doc_type, cache_dir)
                    results[name] = content
                    processed_docs += 1
                    
                except Exception as e:
                    print(f"Error processing document {name}: {str(e)}")
            
            return results

        except Exception as e:
            return {"error": f"Error processing documents: {str(e)}"}

# Move all document processing logic to standalone functions outside the class
# This makes it easier to maintain and avoids Pydantic validation issues

def process_document(url: str, doc_type: str = 'pdf', cache_dir: str = None) -> str:
    """Process a document of any supported type."""
    try:
        # Optional caching
        if cache_dir:
            cache_key = hashlib.md5(url.encode()).hexdigest()
            cache_path = os.path.join(cache_dir, f"{cache_key}.txt")
            
            # Check cache if it exists
            if os.path.exists(cache_path):
                print(f"Using cached content for {url}")
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return f.read()
        
        # Fetch document
        response = fetch_with_retry(url)
        if isinstance(response, str) and response.startswith("Error"):
            return response
                
        # Process based on document type
        text_content = ""
        
        if doc_type == 'pdf' or url.lower().endswith('.pdf'):
            text_content = extract_pdf_text(response.content)
        elif doc_type == 'docx' or url.lower().endswith('.docx'):
            text_content = extract_docx_text(response.content)
        elif doc_type == 'html' or url.lower().endswith(('.html', '.htm')):
            text_content = extract_html_text(response.content)
        elif doc_type == 'txt' or url.lower().endswith('.txt'):
            text_content = response.content.decode('utf-8', errors='replace')
        else:
            # Try to guess by content type
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' in content_type:
                text_content = extract_pdf_text(response.content)
            elif 'word' in content_type:
                text_content = extract_docx_text(response.content)
            elif 'html' in content_type:
                text_content = extract_html_text(response.content)
            elif 'text/plain' in content_type:
                text_content = response.content.decode('utf-8', errors='replace')
            else:
                # Try PDF as a fallback
                try:
                    text_content = extract_pdf_text(response.content)
                except:
                    return f"Unsupported document type: {doc_type or 'unknown'}"
        
        # Save to cache
        if cache_dir and text_content:
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
        
        return text_content

    except Exception as e:
        return f"Error reading document: {str(e)}"

def extract_pdf_text(content: bytes) -> str:
    """Extract text from PDF document."""
    with io.BytesIO(content) as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text_content = ""
        total_pages = len(reader.pages)
        
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            # Add page number for better organization
            text_content += f"\n--- Page {i+1}/{total_pages} ---\n{page_text}\n"
            
    return text_content

def extract_docx_text(content: bytes) -> str:
    """Extract text from DOCX document."""
    with io.BytesIO(content) as docx_file:
        doc = Document(docx_file)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)

def extract_html_text(content: bytes) -> str:
    """Extract text from HTML document."""
    soup = BeautifulSoup(content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()
        
    # Get text
    text = soup.get_text(separator='\n')
    
    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text

def fetch_with_retry(url, retries=3, backoff_factor=2, timeout=30, headers=None):
    """Fetch a URL with retry logic and optional authentication."""
    for i in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if i < retries - 1:
                wait_time = backoff_factor ** i
                time.sleep(wait_time)
            else:
                return f"Error fetching document: {str(e)}"