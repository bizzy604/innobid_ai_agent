from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, List, Dict, Union, Any
import requests
import PyPDF2
import io
import time
import json

class PDFReaderInput(BaseModel):
    """Input schema for PDFReaderTool."""
    bid_data: Dict[str, Any] = Field(..., description="Bid data containing document information")

class PDFReaderTool(BaseTool):
    name: str = "PDF Reader Tool"
    description: str = "Reads text from multiple PDF documents in bid data"
    args_schema: Type[BaseModel] = PDFReaderInput

    def _run(self, bid_data: Dict[str, Any]) -> Dict[str, str]:
        """Reads and processes all PDF documents from bid data."""
        try:
            # Extract document URLs from the bid data
            documents = bid_data.get('documents', [])
            
            # Dictionary to store results
            results = {}

            # Process each document
            for doc in documents:
                if doc.get('type') == 'pdf':
                    url = doc.get('url')
                    name = doc.get('name')
                    if url and name:
                        content = self._process_single_pdf(url)
                        results[name] = content

            return results

        except Exception as e:
            return {"error": f"Error processing documents: {str(e)}"}

    def _process_single_pdf(self, url: str) -> str:
        """Process a single PDF document."""
        try:
            response = fetch_with_retry(url)
            if isinstance(response, str) and response.startswith("Error"):
                return response

            # Use PyPDF2 to read the text from the PDF
            with io.BytesIO(response.content) as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                text_content = ""
                for page in reader.pages:
                    text_content += page.extract_text() or ""

            return text_content

        except Exception as e:
            return f"Error reading PDF: {str(e)}"

def fetch_with_retry(url, retries=3, backoff_factor=2):
    for i in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if i < retries - 1:
                wait_time = backoff_factor ** i
                time.sleep(wait_time)
            else:
                return f"Error fetching PDF: {str(e)}"