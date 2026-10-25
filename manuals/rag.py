"""Retrieval-augmented generation: indexing, semantic search and grounded answers."""

from pgvector.django import CosineDistance

from .ai import chat, embed
from .models import Section

BATCH_SIZE = 32
MAX_DISTANCE = 0.6


def section_text(section):
    """Text used to compute a section's embedding: manual title, section title and content."""
    return f"{section.manual.title}\n{section.title}\n{section.content}"


def index_sections(queryset):
    """Compute and store embeddings for the given sections. Return how many were indexed."""
    sections = list(queryset.select_related("manual"))

    for start in range(0, len(sections), BATCH_SIZE):
        batch = sections[start:start + BATCH_SIZE]
        vectors = embed([section_text(section) for section in batch])
        for section, vector in zip(batch, vectors):
            section.embedding = vector
        Section.objects.bulk_update(batch, ["embedding"])

    return len(sections)


def search_sections(question, k=4, manual=None, max_distance=MAX_DISTANCE):
    """Return the k sections closest in meaning to the question, within the distance threshold."""
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
    """Answer the question using only the retrieved sections. Return the answer and its sources."""
    sections = search_sections(question, k, manual)
    if not sections:
        return "I couldn't find any information about this in the manuals.", []

    sources = "\n\n".join(
        f"[{i}] {section.manual.title} - {section.title}\n{section.content}"
        for i, section in enumerate(sections, start=1)
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that answers questions about user manuals. "
                "Answer in the same language as the question, using ONLY the information in the sources. "
                "If the sources do not contain the answer, say so clearly without making anything up. "
                "Cite in square brackets only the sources you actually used, for example [1]."
            ),
        },
        {"role": "user", "content": f"Sources:\n{sources}\n\nQuestion: {question}"},
    ]

    answer = chat(messages, temperature=0.2)
    return answer, sections