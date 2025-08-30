import os
import tempfile
import subprocess
from pathlib import Path
from typing import Tuple, Optional


class LaTeXUtils:
    @staticmethod
    def latex_to_pdf(latex_content: str) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Convert LaTeX content to PDF.
        
        Args:
            latex_content: String containing LaTeX source code
            
        Returns:
            Tuple of (pdf_bytes, error_message)
            - If successful, pdf_bytes contains the PDF file as bytes and error_message is None
            - If failed, pdf_bytes is None and error_message contains the error
        """
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write LaTeX content to a file
            tex_path = Path(temp_dir) / "document.tex"
            with open(tex_path, 'w') as f:
                f.write(latex_content)
            
            # Run pdflatex
            try:
                # Run pdflatex twice to resolve references
                subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', 'document.tex'],
                    cwd=temp_dir,
                    capture_output=True,
                    check=True,
                    timeout=30  # Timeout in seconds
                )
                subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', 'document.tex'],
                    cwd=temp_dir,
                    capture_output=True,
                    check=True,
                    timeout=30
                )
                
                # Read the generated PDF
                pdf_path = Path(temp_dir) / "document.pdf"
                if pdf_path.exists():
                    with open(pdf_path, 'rb') as f:
                        pdf_bytes = f.read()
                    return pdf_bytes, None
                else:
                    return None, "PDF file not generated"
                    
            except subprocess.CalledProcessError as e:
                return None, f"LaTeX compilation error: {e.stderr.decode('utf-8')}"
            except subprocess.TimeoutExpired:
                return None, "LaTeX compilation timed out"
            except Exception as e:
                return None, f"Error generating PDF: {str(e)}"


# Singleton instance
latex_utils = LaTeXUtils()
