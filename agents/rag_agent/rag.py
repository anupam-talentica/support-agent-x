"""
RAG (Retrieval Augmented Generation) script using ChromaDB in client-server mode.

Prerequisites:
1. Start ChromaDB server: chroma run --host localhost --port 8000 --path ./db
2. Set OPENAI_API_KEY environment variable (for LLM responses and query embeddings)
3. Install dependencies: pip install -r requirements.txt

Usage:
    python rag.py
"""

import logging
import os
from typing import Optional

import chromadb
from chromadb.config import Settings
from openai import OpenAI

logger = logging.getLogger(__name__)


class ChromaRAG:
    """RAG system using ChromaDB as vector store."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8000,
        collection_name: str = "support-agent-x-openai",  # override via CHROMA_COLLECTION in .env
    ):
        """
        Initialize the RAG system.

        Args:
            host: ChromaDB server host
            port: ChromaDB server port
            collection_name: Name of the collection to use
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Connecting to ChromaDB at {host}:{port}...")
        try:
            self.client = chromadb.HttpClient(host=host, port=port)
            logger.info(f"ChromaDB client created, getting collection '{collection_name}'...")
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}, 
            )
            logger.info(f"Collection '{collection_name}' ready. Current count: {self.collection.count()}")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB at {host}:{port}: {e}")
            logger.error(f"Make sure ChromaDB is running and accessible from this container.")
            logger.error(f"On Mac, use 'host.docker.internal' as the host if ChromaDB is on the host machine.")
            raise

        # Initialize OpenAI client for LLM and embeddings (must match ingest: text-embedding-3-small, 1536 dim)
        api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = OpenAI(api_key=api_key) if api_key else OpenAI()
        self._embedding_model = "text-embedding-3-small"

    def _embed_query(self, text: str) -> Optional[list[float]]:
        """Compute query embedding via OpenAI to match ingest dimension (1536). Returns None if unavailable."""
        if not os.getenv("OPENAI_API_KEY"):
            logger.warning("OPENAI_API_KEY not set; RAG query will use Chroma default embedder (384 dim). Collection may expect 1536.")
            return None
        try:
            r = self.openai_client.embeddings.create(model=self._embedding_model, input=[text])
            if r.data:
                return r.data[0].embedding
        except Exception as e:
            logger.warning("OpenAI embedding failed (%s); falling back to query_texts (384 dim). Expect 1536/384 mismatch if ingest used OpenAI.", e)
        return None

    def add_documents(
        self,
        documents: list[str],
        ids: Optional[list[str]] = None,
        metadatas: Optional[list[dict]] = None,
    ) -> None:
        """
        Add documents to the vector store.

        Args:
            documents: List of document texts to add
            ids: Optional list of unique IDs for each document
            metadatas: Optional list of metadata dicts for each document
        """
        if ids is None:
            # Generate IDs based on existing count
            existing_count = self.collection.count()
            ids = [f"doc_{existing_count + i}" for i in range(len(documents))]

        self.collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas,
        )
        print(f"Added {len(documents)} documents to collection")

    def query(
        self,
        query_text: str,
        n_results: int = 1,
    ) -> dict:
        """
        Query the vector store for relevant documents.

        Uses OpenAI embedding for the query when available so dimension matches
        ingest (1536). Falls back to query_texts for 384-dim collections.

        Args:
            query_text: The query string
            n_results: Number of results to return

        Returns:
            Query results from ChromaDB
        """
        embedding = self._embed_query(query_text)
        if embedding is not None:
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=n_results,
            )
        else:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
            )
        return results

    def generate_response(
        self,
        query: str,
        n_context_docs: int = 1,
        model: str = "gpt-4o-mini",
    ) -> str:
        """
        Answer a user question using RAG. Call this tool with the user's question.
        
        Args:
            query: The user's question to answer
            n_context_docs: Number of context documents to retrieve
            model: OpenAI model to use for generation

        Returns:
            Generated response
        """
        print(f"generate response is called with query {query}")
        # Retrieve relevant documents
        results = self.query(query, n_results=n_context_docs)

        # Build context from retrieved documents
        context_docs = results.get("documents", [[]])[0]
        if not context_docs:
            context = "No relevant documents found."
        else:
            context = "\n\n---\n\n".join(context_docs)

        # Create prompt with context
        system_prompt = """You are a helpful assistant that answers questions based on the provided context.
Use only the information from the context to answer. If the context doesn't contain
relevant information, say so clearly."""

        user_prompt = f"""Context:
{context}

Question: {query}

Answer based on the context above:"""

        # Generate response using OpenAI
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=500,
        )

        return response.choices[0].message.content

    def list_documents(self) -> dict:
        """List all documents in the collection."""
        return self.collection.get()

    def delete_collection(self) -> None:
        """Delete the current collection."""
        self.client.delete_collection(self.collection.name)
        print(f"Deleted collection: {self.collection.name}")


def main():
    """Demo the RAG system."""
    # Initialize RAG system
    rag = ChromaRAG(
        host="localhost",
        port=8000,
        collection_name="demo_docs",
    )

    # Sample documents to add
    sample_docs = [
        "Python is a high-level programming language known for its simplicity and readability. It was created by Guido van Rossum and first released in 1991.",
        "ChromaDB is an open-source embedding database designed for AI applications. It makes it easy to build LLM apps by storing and querying embeddings.",
        "RAG (Retrieval Augmented Generation) is a technique that combines information retrieval with text generation. It helps LLMs provide more accurate and up-to-date responses.",
        "Vector databases store data as high-dimensional vectors, enabling semantic search capabilities. They are essential for modern AI applications.",
        "OpenAI's GPT models are large language models that can generate human-like text. They are trained on vast amounts of internet text data.",
    ]

    # Add documents
    print("Adding sample documents...")
    rag.add_documents(sample_docs)

    # Query example
    print("\n" + "=" * 50)
    query = "What is RAG and how does it work?"
    print(f"Query: {query}\n")

    # Show retrieved documents
    results = rag.query(query)
    print("Retrieved documents:")
    for i, doc in enumerate(results["documents"][0], 1):
        print(f"  {i}. {doc[:100]}...")

    # Generate response
    print("\nGenerating response...")
    response = rag.generate_response(query)
    print(f"\nResponse:\n{response}")


if __name__ == "__main__":
    main()
