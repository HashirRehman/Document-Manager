from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from typing import List, Optional
from pydantic import BaseModel, Field

from ..models import Document
from ..services import DocumentService

router = APIRouter()

@router.post("/documents", response_model=Document)
async def upload_document(
    file: UploadFile = File(...), document_service: DocumentService = Depends()
) -> Document:
    """
    Upload a document of any type (PDF, PPT, CSV, etc.) for processing and storage.

    Raises:
        HTTPException: If there's an error during upload or parsing.
    """

    try:
        document_data = await document_service.upload_and_parse_document(file)
        return document_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading/parsing document: {str(e)}")

@router.get("/documents/{document_id}", response_model=Document)
async def get_document(document_id: str, document_service: DocumentService = Depends()) -> Document:
    """
    Retrieve a specific document by its ID.

    Raises:
        HTTPException: If the document is not found.
    """

    document = await document_service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.get("/documents", response_model=List[Document])
async def get_all_documents(document_service: DocumentService = Depends()) -> List[Document]:
    """
    Retrieve a list of all uploaded documents.
    """

    documents = await document_service.get_all_documents()
    return documents

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str, document_service: DocumentService = Depends()) -> None:
    """
    Delete a specific document by its ID.

    Raises:
        HTTPException: If the document is not found or deletion fails.
    """

    deleted = await document_service.delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")

@router.get("/documents/{document_id}/download")
async def download_document(document_id: str, document_service: DocumentService = Depends()) -> FileResponse:
    """
    Download a specific document by its ID.

    Raises:
        HTTPException: If the document is not found or retrieval fails.
    """

    try:
        document_bytes = await document_service.download_document(document_id)
        return FileResponse(document_bytes, media_type="application/octet-stream", filename=f"document_{document_id}.pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading document: {str(e)}")
