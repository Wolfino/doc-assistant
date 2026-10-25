from django.core.management.base import BaseCommand, CommandError

from manuals.ai import AIError
from manuals.services import create_manual_with_ai


class Command(BaseCommand):
    help = "Genera un manuale con l'AI a partire da un argomento."

    def add_arguments(self, parser):
        parser.add_argument("topic", help="Argomento del manuale, tra virgolette.")
        parser.add_argument("--sections", type=int, default=4, help="Numero di sezioni (default 4).")

    def handle(self, *args, **options):
        self.stdout.write(f"Generazione in corso: {options['topic']}...")
        try:
            manual = create_manual_with_ai(options["topic"], options["sections"])
        except AIError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(f"Creato e indicizzato: {manual.title}"))