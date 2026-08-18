"""
docchat/vector_store.py - store chunk embeddings and retrieve the best matches.

This is the Day 18 Chroma workflow, wrapped in a small class so the rest of the
app can just call .add_texts(...) and .search(...) without touching Chroma's API.

We use an IN-MEMORY Chroma client (EphemeralClient) here: each browser session
starts with an empty store and "Clear documents" wipes it instantly. That fits a
chatbot where you upload fresh files each time. To keep documents on disk between
runs instead, swap EphemeralClient() for PersistentClient(path=...) - exactly the
Day 18 code.
"""

import chromadb

from config import COLLECTION_NAME


class VectorStore:
    """A thin wrapper over a Chroma collection: add chunks, search by meaning."""

    def __init__(self, embedder):
        # `embedder` is a loaded SentenceTransformer (passed in so we don't reload
        # the model every time - the app caches it once; see app.py).
        self._embedder = embedder
        # An in-memory Chroma client: nothing is written to disk.
        self._client = chromadb.EphemeralClient()
        # A counter that gives every chunk a unique id across many add() calls.
        self._next_id = 0
        self._make_collection()

    def _make_collection(self):
        # cosine distance matches how we compared embeddings on Days 17-18.
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def add_texts(self, chunks: list, source: str) -> int:
        """Embed `chunks` and store them, tagged with their `source` filename."""
        if not chunks:
            return 0
        # text -> vectors (Day 17). .tolist() converts numpy arrays for Chroma.
        embeddings = self._embedder.encode(chunks).tolist()
        # Build a unique id for each chunk so re-uploads never clash.
        ids = []
        for _ in chunks:
            ids.append(f"chunk-{self._next_id}")
            self._next_id += 1
        self._collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            # Metadata rides along with each vector - we use it to show sources.
            metadatas=[{"source": source} for _ in chunks],
        )
        return len(chunks)

    def search(self, query: str, k: int) -> list:
        """Return the `k` chunks most similar to `query`, best first."""
        if self.count() == 0:
            return []
        query_vec = self._embedder.encode(query).tolist()
        result = self._collection.query(
            query_embeddings=[query_vec],
            # Never ask for more results than we actually stored.
            n_results=min(k, self.count()),
            include=["documents", "metadatas", "distances"],
        )
        # Chroma nests everything one level deep (one list per query). Flatten it
        # into a simple list of dicts the rest of the app can use directly.
        matches = []
        for document, metadata, distance in zip(
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        ):
            matches.append({
                "document": document,
                "source": metadata.get("source", "unknown"),
                # cosine distance -> a friendlier 0..1 similarity for display.
                "similarity": 1 - distance,
            })
        return matches

    def count(self) -> int:
        """How many chunks are currently stored."""
        return self._collection.count()

    def reset(self) -> None:
        """Delete everything - powers the sidebar's 'Clear documents' button."""
        self._client.delete_collection(COLLECTION_NAME)
        self._next_id = 0
        self._make_collection()


# Self-test: needs the embedding model, so it runs a tiny end-to-end check.
if __name__ == "__main__":
    from sentence_transformers import SentenceTransformer
    from config import EMBED_MODEL_NAME

    store = VectorStore(SentenceTransformer(EMBED_MODEL_NAME))
    store.add_texts(
        ["Refunds are processed within 5 business days.",
         "Our office is open Monday to Friday.",
         "You can reset your password from the settings page."],
        source="faq.txt",
    )
    print("stored chunks:", store.count())
    for m in store.search("how long does getting money back take?", k=2):
        print(f"  {m['similarity']:.3f}  [{m['source']}]  {m['document']}")