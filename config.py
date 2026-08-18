"""
docchat/config.py - all the settings and constants in ONE place.

Why a config module? So the "knobs" of the app aren't scattered across ten
files. Want to add a model, change the chunk size, or tweak the grounding
prompt? You edit this file and nothing else. Every other module imports from
here instead of hard-coding values.
"""

# --- LLM (Groq) --------------------------------------------------------------
# The chat models the user can pick in the sidebar. All are free on Groq.
# Order matters: the first one is the default selection.
GROQ_MODELS = [
    "openai/gpt-oss-20b",         # fast + cheap, great default
    "openai/gpt-oss-120b",        # smarter, a little slower
    "llama-3.3-70b-versatile",    # a different model family to compare
]

# Sensible generation defaults (the sidebar can override these live).
DEFAULT_TEMPERATURE = 0.2         # low = focused/factual; high = creative
DEFAULT_MAX_TOKENS = 512          # cap on the length of each answer

# --- Embeddings (local, free) ------------------------------------------------
# The sentence-transformers model from Day 17. 384-dimensional, runs on CPU.
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

# --- Chunking (module: chunker.py) -------------------------------------------
# Long documents are split into overlapping windows before embedding.
CHUNK_SIZE_WORDS = 120            # words per chunk
CHUNK_OVERLAP_WORDS = 20         # words shared between neighbouring chunks

# --- Retrieval (module: vector_store.py / rag.py) ----------------------------
TOP_K = 4                         # how many chunks to retrieve per question
COLLECTION_NAME = "uploaded_docs"

# --- The grounding prompt (module: rag.py) -----------------------------------
# This is what turns a generic chatbot into a "chat with YOUR documents" bot:
# we order the model to answer only from the retrieved chunks.
SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions about the user's uploaded "
    "documents. Answer ONLY using the context provided below. If the context does "
    "not contain the answer, say: 'I couldn't find that in your documents.' "
    "Be concise and, where useful, mention which source the answer came from."
)