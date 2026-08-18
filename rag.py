from config import SYSTEM_PROMPT


def build_context_block(matches: list) -> str:
    """Format retrieved chunks into a numbered, cited context block."""
    if not matches:
        return "(no documents retrieved)"
    lines = []
    for i, match in enumerate(matches, start=1):
        # Label each chunk so the model (and the user) can cite "Source 1", etc.
        lines.append(
            f"[Source {i} | file: {match['source']} | "
            f"relevance: {match['similarity']:.2f}]\n{match['document']}"
        )
    # A blank line between sources keeps the prompt readable for the model.
    return "\n\n".join(lines)


def build_messages(question: str, matches: list, history: list) -> list:
    """Assemble the messages list for Groq: system + past turns + grounded question.

    `history` is the running chat (a list of {"role","content"} dicts, minus the
    current question) so the bot can follow up on earlier turns.
    """
    context_block = build_context_block(matches)

    # 1. The system message sets the rules (answer only from context) - config.py.
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # 2. Prior turns give the model conversational memory (Day 16 idea).
    messages.extend(history)

    # 3. The current question, AUGMENTED with the retrieved context. This fused
    #    "context + question" message is the heart of RAG.
    messages.append({
        "role": "user",
        "content": (
            f"Context from the user's documents:\n{context_block}\n\n"
            f"Question: {question}"
        ),
    })
    return messages


# Self-test: no LLM or embeddings needed - just prove the prompt is well-formed.
if __name__ == "__main__":
    fake_matches = [
        {"document": "Refunds take 5 business days.", "source": "faq.txt", "similarity": 0.81},
        {"document": "Support is open Mon-Fri.", "source": "faq.txt", "similarity": 0.44},
    ]
    msgs = build_messages("How long for a refund?", fake_matches, history=[])
    for m in msgs:
        print(f"--- {m['role']} ---")
        print(m["content"])
        print()