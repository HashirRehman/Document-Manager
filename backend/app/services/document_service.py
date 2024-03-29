from fastapi import Depends
from typing import List, Optional
from pydantic import BaseModel
from botocore.exceptions import ClientError
from unstructuredio import UnstructuredIO

from ..models import Document
from ..config import settings
from ..database import SessionLocal, engine

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UploadError(Exception):
    """Custom exception for upload errors."""
    pass


class UnsupportedDocumentFormat(Exception):
    """Custom exception for unsupported document formats."""
    pass


class DocumentService:

    def __init__(self):
        self.s3_client = boto3.client("s3",
                                       aws_access_key_id=settings.aws_access_key_id,
                                       aws_secret_access_key=settings.aws_secret_access_key)
        self.unstructuredio_api_key = settings.unstructuredio_api_key
        self.unstructuredio = UnstructuredIO(api_key=self.unstructuredio_api_key)

    async def upload_and_parse_document(self, file: UploadFile, db: Session = Depends(get_db)) -> Document:
        """
        Uploads a document to S3, parses its content using unstructured.io, and creates a document record.

        Raises:
            UploadError: If there's an error during upload to S3.
            UnsupportedDocumentFormat: If the file format is not supported by unstructured.io.
        """

        try:
            if not file.content_type.startswith(("application/pdf", "application/vnd.ms-powerpoint", "text/csv")):
                raise UnsupportedDocumentFormat("Unsupported document format.")

            filename = f"{uuid.uuid4()}.{file.content_type.split('/')[1]}"

            self.s3_client.upload_fileobj(file.file, settings.aws_s3_bucket_name, filename)

            data = await self.unstructuredio.process_from_url(f"s3://{settings.aws_s3_bucket_name}/{filename}")

            text = data.get("text", "")
            metadata = data.get("metadata", {})

            new_document = Document(
                filename=filename,
                file_size=file.file_size,
                content_type=file.content_type,
                text=text,
                metadata=metadata
            )

            db.add(new_document)
            db.commit()

            return new_document

        except ClientError as e:
            raise UploadError(f"Error uploading document to S3: {str(e)}") from e
        except Exception as e:
            raise UploadError(f"Error processing document: {str(e)}") from e

    async def get_document(self, document_id: str, db: Session = Depends(get_db)) -> Optional[Document]:
        """
        Retrieves a document by its ID from the database.

        Returns:
            Document: The document object if found, else None.
        """

        document = db.query(Document).filter(Document.id == document_id).first()
        return document

    async def get_all_documents(self, db: Session = Depends(get_db)) -> List[Document]:
        """
        Retrieves all documents from the database.

        Returns:
            List[Document]: A list of Document objects.
        """

        documents = db.query(Document).all()
        return documents

    async def delete_document(self, document_id: str, db: Session = Depends(get_db)) -> bool:
        """
        Deletes a document by its ID from the database and S3.

        Returns:
            bool: True if the document was deleted successfully, False otherwise.
        """

        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                return False

            db.delete(document)
            db.commit()

            self.s3_client.delete_object(Bucket=settings.aws_s3_bucket_name, Key=document.filename)

            return True

        except ClientError as e:
            raise UploadError(f"Error deleting document from S3: {str(e)}") from e
        except Exception as e:
            db.rollback()
            raise UploadError(f"Error deleting document: {str(e)}") from e
