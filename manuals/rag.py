from pgvector.django import CosineDistance

from .ai import chat, embed
from .models import Section

BATCH_SIZE = 32
MAX_DISTANCE = 0.6


def section_text(section):
    """Il testo da cui si calcola l'embedding: manuale, titolo e contenuto."""
    return f"{section.manual.title}\n{section.title}\n{section.content}"


def index_sections(queryset):
    """Calcola e salva gli embedding delle sezioni indicate. Restituisce quante ne ha indicizzate."""
    sections = list(queryset.select_related("manual"))

    for start in range(0, len(sections), BATCH_SIZE):
        batch = sections[start:start + BATCH_SIZE]
        vectors = embed([section_text(section) for section in batch])
        for section, vector in zip(batch, vectors):
            section.embedding = vector
        Section.objects.bulk_update(batch, ["embedding"])

    return len(sections)


def search_sections(question, k=4, manual=None, max_distance=MAX_DISTANCE):
    """Trova le k sezioni più vicine alla domanda, entro la distanza massima."""
    [question_vector] = embed([question])

    queryset = Section.objects.select_related("manual").exclude(embedding__isnull=True)
    if manual is not None:
        queryset = queryset.filter(manual=manual)

    return list(
        queryset.annotate(distance=CosineDistance("embedding", question_vector))
        .filter(distance__lt=max_distance)
        .order_by("distance")[:k]
    )


def answer_question(question, k=4, manual=None):
    """Risponde alla domanda usando solo le sezioni trovate. Restituisce risposta e fonti."""
    sections = search_sections(question, k, manual)
    if not sections:
        return "Non ho trovato informazioni su questo argomento nei manuali.", []

    sources = "\n\n".join(
        f"[{i}] {section.manual.title} - {section.title}\n{section.content}"
        for i, section in enumerate(sections, start=1)
    )

    messages = [
        {
            "role": "system",
            "content": (
                "Sei un assistente che risponde a domande sui manuali d'uso. "
                "Rispondi in italiano usando SOLO le informazioni contenute nelle fonti. "
                "Se le fonti non contengono la risposta, dillo chiaramente senza inventare. "
                "Cita tra parentesi quadre solo le fonti che hai usato davvero, ad esempio [1]."
            ),
        },
        {"role": "user", "content": f"Fonti:\n{sources}\n\nDomanda: {question}"},
    ]

    answer = chat(messages, temperature=0.2)
    return answer, sections