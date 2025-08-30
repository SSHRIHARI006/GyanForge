from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from reportlab.lib import colors
import re
import io
import os
from typing import Dict, Any

class PDFGenerator:
    """Enhanced PDF generator using ReportLab for assignments and notes"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=1  # Center alignment
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            leading=14
        ))
    
    def clean_latex_content(self, content: str) -> str:
        """Remove LaTeX commands and convert to plain text"""
        if not content:
            return ""
        
        # Remove common LaTeX commands
        latex_patterns = [
            r'\\documentclass\{[^}]+\}',
            r'\\usepackage\{[^}]+\}',
            r'\\begin\{document\}',
            r'\\end\{document\}',
            r'\\title\{([^}]+)\}',
            r'\\author\{[^}]+\}',
            r'\\date\{[^}]+\}',
            r'\\maketitle',
            r'\\section\{([^}]+)\}',
            r'\\subsection\{([^}]+)\}',
            r'\\textbf\{([^}]+)\}',
            r'\\textit\{([^}]+)\}',
            r'\\emph\{([^}]+)\}',
            r'\\item\s+',
            r'\\begin\{itemize\}',
            r'\\end\{itemize\}',
            r'\\begin\{enumerate\}',
            r'\\end\{enumerate\}',
            r'\\\\',
            r'\\newpage',
            r'\\clearpage'
        ]
        
        cleaned = content
        for pattern in latex_patterns:
            cleaned = re.sub(pattern, '', cleaned)
        
        # Clean up extra whitespace
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned
    
    def generate_assignment_pdf(self, assignment_data: Dict[str, Any]) -> bytes:
        """Generate PDF from assignment data"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        story = []
        
        # Title
        title = assignment_data.get('title', 'Assignment')
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        # Module information
        module_title = assignment_data.get('module_title', '')
        if module_title:
            story.append(Paragraph(f"Module: {module_title}", self.styles['CustomHeading']))
            story.append(Spacer(1, 12))
        
        # Description
        description = assignment_data.get('description', '')
        if description:
            cleaned_desc = self.clean_latex_content(description)
            story.append(Paragraph("Description:", self.styles['CustomHeading']))
            story.append(Paragraph(cleaned_desc, self.styles['CustomBody']))
            story.append(Spacer(1, 12))
        
        # Questions/Tasks
        questions = assignment_data.get('questions', [])
        if questions:
            story.append(Paragraph("Questions:", self.styles['CustomHeading']))
            for i, question in enumerate(questions, 1):
                if isinstance(question, dict):
                    q_text = question.get('question', str(question))
                else:
                    q_text = str(question)
                
                cleaned_question = self.clean_latex_content(q_text)
                story.append(Paragraph(f"{i}. {cleaned_question}", self.styles['CustomBody']))
                story.append(Spacer(1, 8))
        
        # Content
        content = assignment_data.get('content', '')
        if content:
            cleaned_content = self.clean_latex_content(content)
            # Split into paragraphs
            paragraphs = cleaned_content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), self.styles['CustomBody']))
                    story.append(Spacer(1, 8))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_notes_pdf(self, notes_data: Dict[str, Any]) -> bytes:
        """Generate PDF from notes data"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        story = []
        
        # Title
        title = notes_data.get('title', 'Study Notes')
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        # Module information
        module_title = notes_data.get('module_title', '')
        if module_title:
            story.append(Paragraph(f"Module: {module_title}", self.styles['CustomHeading']))
            story.append(Spacer(1, 12))
        
        # Content sections
        content = notes_data.get('content', '')
        if content:
            cleaned_content = self.clean_latex_content(content)
            
            # Try to identify sections
            sections = re.split(r'\n(?=[A-Z][^a-z]*:|\d+\.)', cleaned_content)
            
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                
                # Check if it's a heading (starts with number or all caps)
                if re.match(r'^\d+\.|^[A-Z\s]+:', section):
                    story.append(Paragraph(section, self.styles['CustomHeading']))
                else:
                    # Split into paragraphs
                    paragraphs = section.split('\n\n')
                    for para in paragraphs:
                        if para.strip():
                            story.append(Paragraph(para.strip(), self.styles['CustomBody']))
                            story.append(Spacer(1, 8))
                
                story.append(Spacer(1, 12))
        
        # Key points
        key_points = notes_data.get('key_points', [])
        if key_points:
            story.append(Paragraph("Key Points:", self.styles['CustomHeading']))
            for point in key_points:
                story.append(Paragraph(f"• {point}", self.styles['CustomBody']))
            story.append(Spacer(1, 12))
        
        # Summary
        summary = notes_data.get('summary', '')
        if summary:
            story.append(Paragraph("Summary:", self.styles['CustomHeading']))
            cleaned_summary = self.clean_latex_content(summary)
            story.append(Paragraph(cleaned_summary, self.styles['CustomBody']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

# Create global instance
pdf_generator = PDFGenerator()
