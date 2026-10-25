from django.core.management.base import BaseCommand, CommandError

from manuals.ai import AIError
from manuals.services import create_manual_with_ai


class Command(BaseCommand):
    help = "Generate a manual with AI from a topic."

    def add_arguments(self, parser):
        parser.add_argument("topic", help="Topic of the manual, in quotes.")
        parser.add_argument("--sections", type=int, default=4, help="Number of sections (default 4).")

    def handle(self, *args, **options):
        self.stdout.write(f"Generating: {options['topic']}...")
        try:
            manual = create_manual_with_ai(options["topic"], options["sections"])
        except AIError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(f"Created and indexed: {manual.title}"))