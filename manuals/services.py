from django.db import transaction

from .ai import generate_manual_data
from .models import Manual, Section
from .rag import index_sections


def create_manual_with_ai(topic, sections=4):
    """Genera un manuale con l'AI, lo salva e indicizza le sezioni. Restituisce il manuale."""
    data = generate_manual_data(topic, sections)

    with transaction.atomic():
        manual = Manual.objects.create(title=data["title"], description=data["description"])
        for order, section in enumerate(data["sections"], start=1):
            Section.objects.create(
                manual=manual,
                title=section["title"],
                content=section["content"],
                order=order,
            )

    index_sections(manual.sections.all())
    return manual