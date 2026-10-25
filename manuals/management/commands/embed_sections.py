from django.core.management.base import BaseCommand, CommandError

from manuals.ai import AIError
from manuals.models import Section
from manuals.rag import index_sections


class Command(BaseCommand):
    help = "Calcola gli embedding delle sezioni che non li hanno ancora."

    def add_arguments(self, parser):
        parser.add_argument("--all", action="store_true", help="Ricalcola gli embedding di tutte le sezioni.")

    def handle(self, *args, **options):
        queryset = Section.objects.all() if options["all"] else Section.objects.filter(embedding__isnull=True)
        try:
            count = index_sections(queryset)
        except AIError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(f"Sezioni indicizzate: {count}"))