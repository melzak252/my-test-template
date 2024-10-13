import asyncio
import logging
import os
from pathlib import Path
from typing import List

from db.models import Document, Fragment
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.models import Distance, PointStruct, VectorParams, IntegerIndexParams
from qdrant_client.http.models import FieldCondition, Filter, MatchValue
from sqlalchemy.ext.asyncio import AsyncSession
from .utils import get_embedding

load_dotenv()

EMBEDDING_SIZE = 1536
EMBEDDING_MODEL = "text-embedding-ada-002"

QDRANT_HOST = "localhost"
QDRANT_PORT = 6351
COLLECTION_NAME = "documents"

client: QdrantClient = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


def search_matches(
    collection_name: str, query_vector: list, document_id: str = None, limit: int = 5
):
    search_result = client.search(
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(
                        value=document_id,
                    ),
                )
            ]
        ),
        collection_name=collection_name,
        query_vector=query_vector,
        limit=limit,
    )

    return search_result


def get_fragments_for_context(question: str, collection_name: str, part_of: str):
    query = question
    query_vector = get_embedding(query)
    points = search_matches(
        collection_name=collection_name,
        query_vector=query_vector,
        document_id=part_of,
    )

    # FETCH THOSE FRAGMENTS FROM POSTGRES BASED ON POINTS

    return points


async def init_qdrant():
    if client.collection_exists(collection_name=COLLECTION_NAME):
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=EMBEDDING_SIZE, distance=Distance.COSINE),
    )


async def add_doc_to_qdrant(doc_text: str, session: AsyncSession):
    doc = Document(content=doc_text)

    session.add(doc)
    await session.commit()
    await session.refresh(doc)

    # HW: SPLIT DOC TO FRAGMENTS
    # fragments = split with langchain splitter
    # THEN ADD FRAGMENTS TO QDRANT NOT DOC!
    # frag_points = []
    # for fragment_text in fragments:
    #     fragment = Fragment(text=fragment_text, document_id=doc.id)
    #     session.add(fragment)
    #     await session.commit()
    #     await session.refresh(fragment)
    #     embedding = get_embedding(fragment_text, model=EMBEDDING_MODEL)
    #     frag_point = PointStruct(
    #         id=fragment.id,
    #         vector=embedding,
    #         payload={
    #             "document_id": doc.id,
    #         }
    #     )
    #     frag_points.append(frag_point)
    # client.upsert(collection_name="fragments", points=frag_points)

    embedding = get_embedding(doc_text, model=EMBEDDING_MODEL)

    point = PointStruct(
        id=doc.id,
        vector=embedding,
        payload={
            "document_id": doc.id,
            # "doc_name": country.name,
            # "fragment_text": fragment.text,
        },
    )

    client.upsert(collection_name=COLLECTION_NAME, points=[point])
    return doc


def get_qdrant_client():
    """Returns the initialized Qdrant client."""
    return client


def close_qdrant_client():
    """Closes the Qdrant client if it's open."""
    global client
    if client:
        client.close()
