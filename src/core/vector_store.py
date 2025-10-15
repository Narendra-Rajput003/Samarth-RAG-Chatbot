# src/core/vector_store.py
"""FAISS vector store for semantic retrieval. Local and scalable."""
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict
from src.core.data_loader import load_and_chunk_data
from src.utils.logger import logger
from src.config.settings import settings

embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)

def build_vector_store(data_paths: List[str]) -> FAISS:
    all_chunks = []
    for path in data_paths:
        all_chunks.extend(load_and_chunk_data(path))
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=settings.max_chunk_size, chunk_overlap=100)
    texts = [chunk["text"] for chunk in all_chunks]
    metadatas = [chunk["metadata"] for chunk in all_chunks]
    split_texts = []
    for text in texts:
        split_texts.extend(splitter.split_text(text))
    
    vectorstore = FAISS.from_texts(split_texts, embeddings, metadatas=metadatas)
    vectorstore.save_local("data/processed/faiss_index")
    logger.info("Vector store built")
    return vectorstore

def retrieve_docs(query: str, k: int = 5) -> List[Dict]:
    vectorstore = FAISS.load_local("data/processed/faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = vectorstore.similarity_search(query, k=k)
    return [{"text": doc.page_content, "metadata": doc.metadata} for doc in docs]