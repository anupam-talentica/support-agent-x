"""
RAG (Retrieval Augmented Generation) script using ChromaDB in client-server mode.

Prerequisites:
1. Start ChromaDB server: chroma run --host localhost --port 8000 --path ./db
2. Set OPENAI_API_KEY environment variable (for LLM responses)
3. Install dependencies: pip install -r requirements.txt

Usage:
    python rag.py
"""

from typing import Optional

import chromadb
from chromadb.config import Settings
from openai import OpenAI


class ChromaRAG:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8000,
        collection_name: str = "documents",
    ):
        self.client = chromadb.HttpClient(host=host, port=port)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}, 
        )
        self.openai_client = OpenAI()

    def add_documents(
        self,
        documents: list[str],
        ids: Optional[list[str]] = None,
        metadatas: Optional[list[dict]] = None,
    ) -> None:
        if ids is None:
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
        n_results: int = 3,
    ) -> dict:
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
        )
        return results

    def generate_response(
        self,
        query: str,
        n_context_docs: int = 3,
        model: str = "gpt-4o-mini",
    ) -> str:
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
        return self.collection.get()

    def delete_collection(self) -> None:
        self.client.delete_collection(self.collection.name)
        print(f"Deleted collection: {self.collection.name}")


def main():
    # Initialize RAG system
    rag = ChromaRAG(
        host="localhost",
        port=8000,
        collection_name="support-agent-x",
    )

    # Sample documents to add
    sample_docs = [
        # "Python is a high-level programming language known for its simplicity and readability. It was created by Guido van Rossum and first released in 1991.",
        # "ChromaDB is an open-source embedding database designed for AI applications. It makes it easy to build LLM apps by storing and querying embeddings.",
        # "RAG (Retrieval Augmented Generation) is a technique that combines information retrieval with text generation. It helps LLMs provide more accurate and up-to-date responses.",
        # "Vector databases store data as high-dimensional vectors, enabling semantic search capabilities. They are essential for modern AI applications.",
        # "OpenAI's GPT models are large language models that can generate human-like text. They are trained on vast amounts of internet text data.",

        "our operating hours are between 12am to 4pm",
        "maximum refund amout is 200 rs"
    ]

    # Add documents
    print("Adding sample documents...")
    rag.add_documents(sample_docs)

    # result = rag.query("what is chroma db", n_results=2)
    # print(result)


if __name__ == "__main__":
    main()
