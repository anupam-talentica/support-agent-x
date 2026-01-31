"""Mem0 configuration for memory agent."""

import os
from typing import Dict, Any


def get_mem0_config() -> Dict[str, Any]:
    """
    Get mem0 configuration using ChromaDB.
    
    Returns:
        Configuration dictionary for mem0
    """
    chroma_host = os.getenv('CHROMA_HOST', 'localhost')
    chroma_port = int(os.getenv('CHROMA_PORT', '8000'))
    
    config = {
        "llm": {
            "provider": "openai",
            "config": {
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "temperature": 0.2,  # Lower for consistent fact extraction
                "api_key": os.getenv("OPENAI_API_KEY"),
            }
        },
        "embedder": {
            "provider": "openai",
            "config": {
                "model": "text-embedding-3-small",
                "api_key": os.getenv("OPENAI_API_KEY"),
            }
        },
        "vector_store": {
            "provider": "chroma",
            "config": {
                "collection_name": "mem0_memories",
                "host": chroma_host,
                "port": chroma_port,
            }
        },
        "history_db_path": os.getenv("MEM0_HISTORY_DB_PATH", "./data/mem0_history.db")
    }
    
    return config
