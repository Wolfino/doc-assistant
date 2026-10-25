import json
import os

import requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
CHAT_MODEL = os.environ.get("OLLAMA_CHAT_MODEL", "qwen2.5:7b")
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
    """Errore nella comunicazione con il modello di AI."""


def chat(messages, schema=None, temperature=0.4, timeout=300):
    """Invia una conversazione a Ollama e restituisce il testo della risposta."""
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
        raise AIError(f"Impossibile contattare Ollama: {exc}") from exc

    return response.json()["message"]["content"]


def generate_manual_data(topic, sections=4):
    """Chiede al modello un manuale sul tema indicato e lo restituisce come dizionario."""
    messages = [
        {
            "role": "system",
            "content": (
                "Sei un redattore tecnico esperto. Scrivi manuali d'uso in italiano corretto, "
                "chiari e realistici. Rivolgiti sempre al lettore con il tu e l'imperativo "
                "(es. 'premi', 'inserisci'). Non inventare componenti assurdi: descrivi "
                "funzioni plausibili per il prodotto."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Scrivi un manuale d'uso per: {topic}.\n"
                f"- Una descrizione del manuale di 1-2 frasi.\n"
                f"- Esattamente {sections} sezioni.\n"
                "- Ogni sezione ha un titolo breve e un testo di 3-5 frasi con istruzioni "
                "pratiche e dettagli concreti, come valori, impostazioni e nomi dei menu.\n"
                "Rispondi solo con il JSON richiesto."
            ),
        },
    ]

    content = chat(messages, schema=MANUAL_SCHEMA)

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise AIError("Il modello non ha restituito un JSON valido.") from exc

    if not data.get("sections"):
        raise AIError("Il modello non ha generato nessuna sezione.")

    if not data.get("description", "").strip():
        raise AIError("Il modello non ha generato la descrizione.")

    data["sections"] = data["sections"][:sections]
    return data

def embed(texts, timeout=120):
    """Trasforma una lista di testi in una lista di vettori."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embed",
            json={"model": EMBED_MODEL, "input": texts},
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise AIError(f"Impossibile calcolare gli embedding: {exc}") from exc

    return response.json()["embeddings"]