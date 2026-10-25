"""Client for the Ollama API: chat, embeddings and manual generation."""

import json
import os

import requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
CHAT_MODEL = os.environ.get("OLLAMA_CHAT_MODEL", "gemma3:12b")
EMBED_MODEL = os.environ.get("OLLAMA_EMBED_MODEL", "bge-m3")

MANUAL_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "description": {"type": "string"},
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["title", "content"],
            },
        },
    },
    "required": ["title", "description", "sections"],
}


class AIError(Exception):
    """Raised when the AI model cannot be reached or returns an invalid response."""


def chat(messages, schema=None, temperature=0.4, timeout=300):
    """Send a conversation to Ollama and return the response text."""
    payload = {
        "model": CHAT_MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature},
    }
    if schema:
        payload["format"] = schema

    try:
        response = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise AIError(f"Could not reach Ollama: {exc}") from exc

    return response.json()["message"]["content"]


def generate_manual_data(topic, sections=4):
    """Ask the model for a manual about the given topic and return it as a dict."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are an experienced technical writer. Write clear, realistic user manuals "
                "in correct English. Always address the reader directly using the imperative "
                "(e.g. 'press', 'insert'). Do not invent absurd components: describe features "
                "that are plausible for the product."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Write a user manual for: {topic}.\n"
                "- A 1-2 sentence description of the manual.\n"
                f"- Exactly {sections} sections.\n"
                "- Each section has a short title and 3-5 sentences of practical instructions "
                "with concrete details, such as values, settings and menu names.\n"
                "Reply only with the requested JSON."
            ),
        },
    ]

    content = chat(messages, schema=MANUAL_SCHEMA)

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise AIError("The model did not return valid JSON.") from exc

    if not data.get("sections"):
        raise AIError("The model did not generate any sections.")
    if not data.get("description", "").strip():
        raise AIError("The model did not generate a description.")

    data["sections"] = data["sections"][:sections]
    return data


def embed(texts, timeout=120):
    """Turn a list of texts into a list of embedding vectors."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embed",
            json={"model": EMBED_MODEL, "input": texts},
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise AIError(f"Could not compute embeddings: {exc}") from exc

    return response.json()["embeddings"]