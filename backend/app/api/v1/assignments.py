from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response, FileResponse
from sqlmodel import Session
import os
import time

from app.db.session import get_session
from app.models.models import LearningModule
from app.utils.latex_utils import LaTeXUtils

STORAGE_DIR = os.path.abspath(os.path.join(os.getcwd(), "storage", "assignments"))
os.makedirs(STORAGE_DIR, exist_ok=True)

router = APIRouter(
    prefix="/api/v1/assignments",
    tags=["assignments"]
)


@router.get("/{module_id}/pdf")
async def get_assignment_pdf(
    module_id: int,
    session: Session = Depends(get_session)
):
    """
    Get a PDF version of the assignment for a learning module.
    
    Args:
        module_id: ID of the module
        session: Database session
        
    Returns:
        PDF file as a downloadable response
    """
    # Get the module
    module = session.get(LearningModule, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with ID {module_id} not found"
        )
    
    if not module.assignment_latex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No assignment available for this module"
        )
    
    # If PDF already generated and exists on disk, return it
    if module.assignment_pdf_path and os.path.exists(module.assignment_pdf_path):
        return FileResponse(module.assignment_pdf_path, media_type="application/pdf", filename=os.path.basename(module.assignment_pdf_path))

    # Convert LaTeX to PDF bytes
    pdf_bytes, error = LaTeXUtils.latex_to_pdf(module.assignment_latex)

    if error or not pdf_bytes:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating PDF: {error}"
        )

    # Save PDF to storage with clear name
    timestamp = int(time.time())
    filename = f"assignment_{module_id}_{timestamp}.pdf"
    file_path = os.path.join(STORAGE_DIR, filename)
    try:
        with open(file_path, "wb") as f:
            f.write(pdf_bytes)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save PDF: {e}")

    # Persist path to DB
    module.assignment_pdf_path = file_path
    session.add(module)
    session.commit()
    session.refresh(module)

    return FileResponse(file_path, media_type="application/pdf", filename=filename)


@router.get("/{module_id}/latex")
async def get_assignment_latex(
    module_id: int,
    session: Session = Depends(get_session)
):
    """
    Get the LaTeX source code for an assignment.
    
    Args:
        module_id: ID of the module
        session: Database session
        
    Returns:
        LaTeX source code
    """
    module = session.get(LearningModule, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with ID {module_id} not found"
        )
    
    if not module.assignment_latex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No assignment available for this module"
        )
    
    return {"latex": module.assignment_latex}
