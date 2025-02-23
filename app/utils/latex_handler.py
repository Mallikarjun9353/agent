import os
from pathlib import Path
import subprocess
from typing import Dict, Optional

class LaTeXHandler:
    @staticmethod
    def read_base_resume(file_path: str = 'data/templates/resume.tex') -> str:
        """Read the base LaTeX resume"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Resume template not found at {file_path}")
        except Exception as e:
            raise Exception(f"Error reading resume template: {str(e)}")

    @staticmethod
    def convert_to_pdf(tex_file: str) -> str:
        """Convert LaTeX file to PDF"""
        try:
            pdf_name = Path(tex_file).stem + '.pdf'
            
            # Run pdflatex twice for proper compilation
            for _ in range(2):
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', tex_file],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    raise Exception(f"PDF conversion failed: {result.stderr}")
            
            # Cleanup auxiliary files
            for ext in ['.aux', '.log', '.out']:
                aux_file = Path(tex_file).stem + ext
                if os.path.exists(aux_file):
                    os.remove(aux_file)
                    
            return pdf_name
        except Exception as e:
            raise Exception(f"Error converting to PDF: {str(e)}")

    @staticmethod
    def create_modified_resume(modified_content: str, company_name: str) -> Dict[str, str]:
        """Create a new version of the resume"""
        try:
            from datetime import datetime
            date_str = datetime.now().strftime("%Y%m%d")
            tex_filename = f"{company_name}_{date_str}_resume.tex"
            
            # Write the new TEX file
            with open(tex_filename, 'w', encoding='utf-8') as file:
                file.write(modified_content.strip())
            
            # Convert to PDF
            pdf_filename = LaTeXHandler.convert_to_pdf(tex_filename)
            
            # Verify files
            if not os.path.exists(tex_filename):
                raise Exception("Failed to create LaTeX file")
            if not os.path.exists(pdf_filename):
                raise Exception("Failed to create PDF file")
                
            return {
                'tex_file': tex_filename,
                'pdf_file': pdf_filename
            }
        except Exception as e:
            raise Exception(f"Error creating modified resume: {str(e)}") 