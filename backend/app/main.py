from fastapi import FastAPI
from document_service import DocumentService

app = FastAPI()

document_service = DocumentService()

@app.post("/documents")
async def upload_document(file: UploadFile):
    document = await document_service.upload_and_parse_document(file)
    return document

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
