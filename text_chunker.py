"""
docchat/chunker.py - split a long document into small overlapping chunks.

Why chunk at all? Two reasons:
  1. Retrieval works best on small, focused passages. Embedding a whole 5-page
     PDF into ONE vector blurs every topic together; embedding paragraph-sized
     chunks lets us retrieve just the relevant piece.
  2. We only feed the few retrieved chunks to the LLM, not the whole document -
     that keeps prompts small, fast and cheap.

Why OVERLAP? A sentence explaining an idea might land right on a chunk boundary.
Sharing a few words between neighbouring chunks means an idea is never cut in
half with no chunk containing the whole thing.

We chunk by WORDS here (simple and predictable). Day 21 covers smarter chunking
(recursive, semantic, parent-document).
"""

from config import CHUNK_OVERLAP_WORDS, CHUNK_SIZE_WORDS


def chunk_text(text: str, size: int = CHUNK_SIZE_WORDS,
               overlap: int = CHUNK_OVERLAP_WORDS) -> list:
    """Split `text` into chunks of ~`size` words that overlap by `overlap` words."""
    # Split into words once. (.split() collapses all whitespace for us.)
    words = text.split()
    if not words:
        return []

    # The window slides forward by (size - overlap) each step, so consecutive
    # chunks share `overlap` words. step must be > 0 or we'd loop forever.
    step = max(1, size - overlap)

    chunks = []
    for start in range(0, len(words), step):
        # Take a window of `size` words starting at `start`.
        window = words[start:start + size]
        chunks.append(" ".join(window))
        # If this window already reached the end, stop (avoids a tiny trailing
        # chunk that is fully contained in the previous one).
        if start + size >= len(words):
            break
    return chunks


# Self-test: chunk a numbered string so the overlap is easy to see.
if __name__ == "__main__":
    sample = " ".join(f"w{i}" for i in range(1, 26))   # w1 w2 ... w25
    pieces = chunk_text(sample, size=10, overlap=3)
    print(f"{len(pieces)} chunks from 25 words (size=10, overlap=3):")
    for i, piece in enumerate(pieces, 1):
        print(f"  chunk {i}: {piece}")