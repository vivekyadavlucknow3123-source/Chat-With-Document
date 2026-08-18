import os

from groq import Groq


def make_client():
    """Return a Groq client, or None if no API key is configured.

    Returning None (instead of crashing) lets the UI show a friendly 'add your
    key' message instead of a traceback.
    """
    if not os.getenv("GROQ_API_KEY"):
        return None
    return Groq()


def stream_answer(client, model: str, messages: list,
                  temperature: float, max_tokens: int):
    """Yield the answer token-by-token as Groq generates it.

    This is a generator: Streamlit's st.write_stream consumes it to type the
    reply onto the page live. `temperature` and `max_tokens` come straight from
    the sidebar sliders, so the user controls the model's behaviour.
    """
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,   # send the answer in pieces as it is produced
    )
    for chunk in stream:
        # Some chunks (like the final one) carry no text; skip those.
        piece = chunk.choices[0].delta.content
        if piece:
            yield piece


def complete_answer(client, model: str, messages: list,
                    temperature: float, max_tokens: int) -> str:
    """Non-streaming version: return the whole answer as one string.

    Handy for scripts/tests where you don't need live typing.
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content or ""


# Self-test: only runs if a GROQ_API_KEY is present in the environment/.env.
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    client = make_client()
    if client is None:
        print("No GROQ_API_KEY set - skipping live test (this is fine).")
    else:
        msgs = [{"role": "user", "content": "Say 'llm.py works' and nothing else."}]
        print(complete_answer(client, "openai/gpt-oss-20b", msgs, 0.0, 20))