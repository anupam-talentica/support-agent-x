import os
import logging

from .rag import ChromaRAG

logger = logging.getLogger(__name__)


class RagAgent: 
    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']

    def __init__(self):
        # Initialize ChromaRAG with ChromaDB server connection
        # ChromaDB server should be running separately
        chroma_host = os.getenv('CHROMA_HOST', 'localhost')
        chroma_port = int(os.getenv('CHROMA_PORT', '8000'))
        collection_name = os.getenv('CHROMA_COLLECTION', 'support-agent-x')
        
        logger.info(f"Initializing RAG Agent with ChromaDB at {chroma_host}:{chroma_port}, collection: {collection_name}")
        
        try:
            self._rag = ChromaRAG(
                host=chroma_host,
                port=chroma_port,
                collection_name=collection_name,
            )
            logger.info(f"Successfully connected to ChromaDB at {chroma_host}:{chroma_port}")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB at {chroma_host}:{chroma_port}: {e}")
            raise

    def get_processing_message(self) -> str:
        return 'Processing the rag request...'

    async def stream(self, query: str, session_id: str):
        yield {'is_task_complete': False, 'updates': 'Searching documents...'}
        
        response = self._rag.generate_response(query)
        yield {'is_task_complete': True, 'content': response}
