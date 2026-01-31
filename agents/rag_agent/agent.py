from rag import ChromaRAG

class RagAgent: 
    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']

    def __init__(self):
        self._rag = ChromaRAG()

    def get_processing_message(self) -> str:
        return 'Processing the rag request...'

    async def stream(self, query: str, session_id: str):
        yield {'is_task_complete': False, 'updates': 'Searching documents...'}
        
        response = self._rag.generate_response(query)
        yield {'is_task_complete': True, 'content': response}
