# src/api/app.py
"""FastAPI: Simple RAG API without authentication."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.core.rag_pipeline import run_rag
from src.utils.logger import logger
from src.config.settings import settings

app = FastAPI(title="Samarth RAG API")
app.add_middleware(CORSMiddleware, allow_origins=["*"])

class QueryRequest(BaseModel):
    question: str

@app.post("/query")
async def query_rag(request: QueryRequest):
    try:
        response = run_rag(request.question)
        llm_used = "Gemini 2.0 Flash"
        logger.info(f"Query using {llm_used}: {request.question[:50]}")
        return {"answer": response, "llm_used": llm_used}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))