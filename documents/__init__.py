from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from qdrant import add_doc_to_qdrant

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/")
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]


@router.post("/document")
async def create_document(file: UploadFile, session: AsyncSession = Depends(get_db)):
    content = (await file.read()).decode("utf-8")
    doc = await add_doc_to_qdrant(content, session)
    return doc
