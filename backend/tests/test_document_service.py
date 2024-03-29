import pytest
from unittest.mock import patch
from document_service import DocumentService, UploadError, UnsupportedDocumentFormat
from ..models import Document

@pytest.mark.asyncio
async def test_upload_and_parse_document_success(mocker):
    mocker.patch.object(DocumentService, "_upload_to_s3")
    mocker.patch.object(DocumentService, "_parse_document_with_unstructuredio")

    mock_file = mocker.MagicMock()
    mock_file.content_type = "application/pdf"
    mock_file.file.read.return_value = b"This is a test PDF document"


    document_service = DocumentService()
    document = await document_service.upload_and_parse_document(mock_file)

    assert document.content_type == "application/pdf"
    assert document.text.startswith("This is a test")

@pytest.mark.asyncio
async def test_upload_and_parse_document_unsupported_format():
    document_service = DocumentService()

    with pytest.raises(UnsupportedDocumentFormat):
        await document_service.upload_and_parse_document(mocker.MagicMock(content_type="text/plain"))

@pytest.mark.asyncio
async def test_upload_and_parse_document_upload_error(mocker):
    mocker.patch.object(DocumentService, "_upload_to_s3", side_effect=ClientError("Test S3 Error"))

    document_service = DocumentService()
    with pytest.raises(UploadError) as excinfo:
        await document_service.upload_and_parse_document(mocker.MagicMock())
    assert "Test S3 Error" in str(excinfo.value)
