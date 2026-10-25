from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from manuals.ai import AIError, generate_manual_data
from manuals.models import Manual, Section
from manuals.rag import index_sections


class Command(BaseCommand):
    help = "Genera un manuale con l'AI a partire da un argomento."

    def add_arguments(self, parser):
        parser.add_argument("topic", help="Argomento del manuale, tra virgolette.")
        parser.add_argument("--sections", type=int, default=4, help="Numero di sezioni (default 4).")

    def handle(self, *args, **options):
        self.stdout.write(f"Generazione in corso: {options['topic']}...")

        try:
            data = generate_manual_data(options["topic"], options["sections"])
        except AIError as exc:
            raise CommandError(str(exc)) from exc

        with transaction.atomic():
            manual = Manual.objects.create(title=data["title"], description=data["description"])
            for order, section in enumerate(data["sections"], start=1):
                Section.objects.create(
                    manual=manual,
                    title=section["title"],
                    content=section["content"],
                    order=order,
                )

        self.stdout.write(self.style.SUCCESS(f"Creato: {manual.title} ({len(data['sections'])} sezioni)"))

        try:
            count = index_sections(manual.sections.all())
            self.stdout.write(f"Sezioni indicizzate: {count}")
        except AIError as exc:
            self.stderr.write(f"Manuale salvato, ma indicizzazione non riuscita: {exc}")