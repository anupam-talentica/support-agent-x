"""
RAG (Retrieval Augmented Generation) script using ChromaDB in client-server mode.

Ingests policy and FAQ documents from training-docs/ into ChromaDB:
- training-docs/policies/*.md  (policy documents)
- training-docs/faqs/*.md      (FAQ documents)

Prerequisites:
1. Start ChromaDB server: chroma run --host 0.0.0.0 --port 8000
2. Set CHROMA_COLLECTION in .env (same as RAG agent): support-agent-x-openai or support-agent-x.
3. Either: (a) use chromadb package (RAG-ingest venv with pydantic<2.1), or
   (b) script falls back to HTTP API (no chromadb import; works in main venv).
   For HTTP API, set OPENAI_API_KEY and have the openai package installed.

Usage:
    python scripts/ingest_rag_data.py
"""

from pathlib import Path
from typing import Optional

# Try chromadb package first; if it fails (e.g. Pydantic conflict), use HTTP-only fallback.
_CHROMADB_AVAILABLE = False
_chromadb = None

try:
    from pydantic import BaseSettings  # noqa: F401
except Exception:
    try:
        import pydantic
        from pydantic_settings import BaseSettings
        pydantic.BaseSettings = BaseSettings  # type: ignore[attr-defined]
    except ImportError:
        pass

try:
    import chromadb
    from chromadb.config import Settings  # noqa: F401
    _CHROMADB_AVAILABLE = True
    _chromadb = chromadb
except Exception:
    pass  # Use HTTP fallback below


def _make_rag_client(host: str, port: int, collection_name: str):
    """Use chromadb package if available, else HTTP-only client."""
    if _CHROMADB_AVAILABLE and _chromadb is not None:
        return _ChromaRAG(host, port, collection_name)
    return _ChromaRAGHTTP(host, port, collection_name)


class _ChromaRAGHTTP:
    """ChromaDB client via REST API only (no chromadb package). Works with any Pydantic."""

    def __init__(self, host: str = "localhost", port: int = 8000, collection_name: str = "documents"):
        self.base_url = f"http://{host}:{port}"
        # Collection name from CHROMA_COLLECTION in .env (e.g. support-agent-x or support-agent-x-openai)
        self.collection_name = collection_name
        self.collection_id: Optional[str] = None
        self._tenant = "default_tenant"
        self._database = "default_database"
        self._ensure_collection()

    def _path(self, *parts: str) -> str:
        return f"{self.base_url}/api/v2/tenants/{self._tenant}/databases/{self._database}/" + "/".join(parts)

    def _ensure_collection(self) -> None:
        import httpx
        # Create collection (idempotent: 409 = already exists, get id and proceed)
        url = self._path("collections")
        payload = {"name": self.collection_name, "metadata": {"hnsw:space": "cosine"}}
        with httpx.Client(timeout=30.0) as client:
            r = client.post(url, json=payload)
            if r.status_code in (200, 201):
                data = r.json()
                self.collection_id = data.get("id") or data.get("name") or self.collection_name
                return
            if r.status_code == 409:
                # Collection already exists; try to get its id from response or by listing
                try:
                    data = r.json()
                    self.collection_id = data.get("id") or data.get("name") or self.collection_name
                    if self.collection_id:
                        return
                except Exception:
                    pass
                # GET collections and find by name
                r2 = client.get(url)
                if r2.status_code == 200:
                    data = r2.json()
                    items = data if isinstance(data, list) else data.get("collections", data.get("data", []))
                    for c in (items or []):
                        name = c.get("name") if isinstance(c, dict) else getattr(c, "name", None)
                        if name == self.collection_name:
                            self.collection_id = c.get("id") if isinstance(c, dict) else getattr(c, "id", None) or self.collection_name
                            return
                self.collection_id = self.collection_name
                return
            # Try v1-style path
            url_v1 = f"{self.base_url}/api/v1/collections"
            r1 = client.post(url_v1, json=payload)
            if r1.status_code in (200, 201, 409):
                try:
                    data = r1.json()
                    self.collection_id = data.get("id") or data.get("name") or self.collection_name
                except Exception:
                    self.collection_id = self.collection_name
                return
            r.raise_for_status()

    def _embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Compute embeddings via OpenAI API. Requires OPENAI_API_KEY."""
        import os
        try:
            from openai import OpenAI
        except ImportError:
            raise RuntimeError(
                "ChromaDB HTTP API requires embeddings. Install openai and set OPENAI_API_KEY, "
                "or use the chromadb package in a RAG-ingest venv (pydantic<2.1)."
            )
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required for HTTP ingest (ChromaDB server expects embeddings).")
        client = OpenAI(api_key=api_key)
        # Use small embedding model; batch in chunks to avoid token limits
        embeddings = []
        for i in range(0, len(documents), 20):
            batch = documents[i : i + 20]
            r = client.embeddings.create(model="text-embedding-3-small", input=batch)
            for e in sorted(r.data, key=lambda x: x.index):
                embeddings.append(e.embedding)
        return embeddings

    def add_documents(
        self,
        documents: list[str],
        ids: Optional[list[str]] = None,
        metadatas: Optional[list[dict]] = None,
    ) -> None:
        import httpx
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
        metadatas = metadatas or [{}] * len(documents)
        # ChromaDB metadata values must be str, int, float, or bool only; omit None
        metadatas_clean = []
        for m in metadatas:
            clean = {k: (v if isinstance(v, (str, int, float, bool)) else str(v)) for k, v in (m or {}).items() if v is not None}
            metadatas_clean.append(clean)
        # ChromaDB v2 add API requires embeddings; compute via OpenAI
        print("Computing embeddings (OpenAI)...")
        embeddings = self._embed_documents(documents)
        payload = {
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas_clean,
            "embeddings": embeddings,
        }
        url = self._path("collections", self.collection_id or self.collection_name, "add")
        with httpx.Client(timeout=120.0) as client:
            r = client.post(url, json=payload)
            if r.status_code == 404:
                url_v1 = f"{self.base_url}/api/v1/collections/{self.collection_name}/add"
                r = client.post(url_v1, json=payload)
            if r.status_code in (400, 422):
                try:
                    err = r.json()
                    print(f"ChromaDB {r.status_code} response: {err}", file=__import__("sys").stderr)
                except Exception:
                    print(f"ChromaDB {r.status_code} response body: {r.text[:500]}", file=__import__("sys").stderr)
                # 400 often = embedding dimension mismatch; collection may exist with wrong dim
                if r.status_code == 400:
                    print("Tip: Set CHROMA_COLLECTION in .env (e.g. support-agent-x-openai for 1536-dim).", file=__import__("sys").stderr)
            r.raise_for_status()
        print(f"Added {len(documents)} documents to collection (HTTP)")


class _ChromaRAG:
    """ChromaDB client using chromadb package (requires Pydantic <2.1 in env)."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8000,
        collection_name: str = "documents",
    ):
        from openai import OpenAI
        self.client = _chromadb.HttpClient(host=host, port=port)
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


def get_training_docs_root() -> Path:
    """Return the path to training-docs (support_agents/training-docs)."""
    script_dir = Path(__file__).resolve().parent
    support_agents_root = script_dir.parent
    return support_agents_root / "training-docs"


def load_documents_from_dir(
    base_path: Path,
    subdir: str,
    doc_type: str,
) -> tuple[list[str], list[str], list[dict]]:
    """
    Load all .md files from base_path/subdir.
    Returns (documents, ids, metadatas).
    """
    dir_path = base_path / subdir
    if not dir_path.is_dir():
        return [], [], []

    documents = []
    ids = []
    metadatas = []

    for md_file in sorted(dir_path.glob("*.md")):
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Warning: could not read {md_file}: {e}")
            continue
        if not content.strip():
            continue
        doc_id = f"{doc_type}_{md_file.stem}"
        documents.append(content)
        ids.append(doc_id)
        metadatas.append({
            "doc_type": doc_type,
            "file_name": md_file.name,
            "source": str(md_file.relative_to(base_path)),
        })
        print(f"  Loaded: {md_file.name} -> {doc_id}")

    return documents, ids, metadatas


def main():
    import os
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    # Collection name from .env; same as RAG agent so ingest and queries use same collection
    chroma_host = os.getenv("CHROMA_HOST", "localhost")
    chroma_port = int(os.getenv("CHROMA_PORT", "8000"))
    collection_name = os.getenv("CHROMA_COLLECTION", "support-agent-x-openai")
    # Use chromadb package if available, else HTTP-only (works with any Pydantic)
    rag = _make_rag_client(
        host=chroma_host,
        port=chroma_port,
        collection_name=collection_name,
    )
    if not _CHROMADB_AVAILABLE:
        print("Using ChromaDB HTTP API (chromadb package not loaded due to Pydantic conflict).")

    training_root = get_training_docs_root()
    if not training_root.is_dir():
        print(f"ERROR: training-docs not found at {training_root}")
        print("Ensure support_agents/training-docs/ exists with policies/ and faqs/.")
        return

    all_documents = []
    all_ids = []
    all_metadatas = []

    # Load policy documents
    print("Loading policy documents...")
    policy_docs, policy_ids, policy_metas = load_documents_from_dir(
        training_root, "policies", "policy"
    )
    all_documents.extend(policy_docs)
    all_ids.extend(policy_ids)
    all_metadatas.extend(policy_metas)

    # Load FAQ documents
    print("Loading FAQ documents...")
    faq_docs, faq_ids, faq_metas = load_documents_from_dir(
        training_root, "faqs", "faq"
    )
    all_documents.extend(faq_docs)
    all_ids.extend(faq_ids)
    all_metadatas.extend(faq_metas)

    if not all_documents:
        print("No documents found. Check training-docs/policies/ and training-docs/faqs/.")
        return

    # Add documents to ChromaDB
    print(f"Adding {len(all_documents)} documents to collection...")
    rag.add_documents(
        documents=all_documents,
        ids=all_ids,
        metadatas=all_metadatas,
    )
    print("Ingestion complete.")


if __name__ == "__main__":
    main()
