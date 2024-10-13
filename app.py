from contextlib import asynccontextmanager
import json
import os
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from openai import OpenAI
from dotenv import load_dotenv
from db import get_db, get_engine
from db.base import Base
from db.models import *


import documents
from qdrant import close_qdrant_client, init_qdrant


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await init_qdrant()

    yield

    close_qdrant_client()


app = FastAPI(lifespan=lifespan)
load_dotenv()


app.include_router(documents.router)


def ask_spell(description: str):
    system_prompt = """
    You are powerful wizard and you are creating a new spell for user spell desciption.
    
    ### Output Format
    Answer with JSON format and nothing else. 
    Use the specific format:
    {
        "spell_name": "string",
        "spell_description": "string",
        "spell_effect": "string"
    }
    """
    question_prompt = f"""User's spell description: {description}"""

    prompts = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question_prompt},
    ]

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=prompts,
        response_format={"type": "json_object"},
        temperature=0.000001,
    )

    answer = response.choices[0].message.content

    try:
        answer_dict: dict = json.loads(answer)
    except json.JSONDecodeError:
        print(answer)
        raise

    return answer


@app.get("/")
async def read_root(description: str, session: AsyncSession = Depends(get_db)):

    return ask_spell(description)
