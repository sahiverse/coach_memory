# services/llm_service.py
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.3-70b-versatile"

def generate_response(system_prompt: str, messages: list[dict]) -> str:
    """
    Core LLM call. Takes a system prompt and conversation history.
    Returns the assistant's reply as a plain string.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            *messages
        ],
        temperature=0.7,
        max_tokens=1024,
    )
    return response.choices[0].message.content


def generate_structured_response(system_prompt: str, messages: list[dict]) -> str:
    """
    Same as generate_response but with lower temperature.
    Use this for feedback synthesis where consistency matters.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            *messages
        ],
        temperature=0.3,
        max_tokens=2048,
    )
    return response.choices[0].message.content