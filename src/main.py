# src/main.py
"""Entry: Build index, start API. Run UI separately."""
import glob
import os
from .core.vector_store import build_vector_store
from .utils.logger import logger
import uvicorn

if __name__ == "__main__":
    # Check if index already exists (for production)
    index_path = "data/processed/faiss_index"
    data_paths = glob.glob("data/raw/*.csv")

    if not os.path.exists(index_path) and data_paths:
        logger.info("Building vector store...")
        build_vector_store(data_paths)
        logger.info("Index built successfully.")
    elif os.path.exists(index_path):
        logger.info("Using existing vector store index.")
    else:
        logger.error("No data files found and no existing index. Please ensure data files are present.")

    # Start API server
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting API server on port {port}...")
    uvicorn.run("src.api.app:app", host="0.0.0.0", port=port)