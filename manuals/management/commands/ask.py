from django.core.management.base import BaseCommand, CommandError

from manuals.models import Manual
from manuals.ai import AIError
from manuals.rag import answer_question


class Command(BaseCommand):
    help = "Fa una domanda ai manuali."

    def add_arguments(self, parser):
        parser.add_argument("question", help="La domanda, tra virgolette.")
        parser.add_argument("--k", type=int, default=4, help="Quante sezioni usare come fonti (default 4).")
        parser.add_argument("--manual", type=int, help="ID del manuale in cui cercare.")

    def handle(self, *args, **options):
        manual = None
        if options["manual"]:
            try:
                manual = Manual.objects.get(pk=options["manual"])
            except Manual.DoesNotExist:
                raise CommandError(f"Nessun manuale con ID {options['manual']}.")

        try:
            answer, sections = answer_question(options["question"], options["k"], manual)
        except AIError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(answer)
        self.stdout.write("\nFonti:")
        for i, section in enumerate(sections, start=1):
            self.stdout.write(f"[{i}] {section} (distanza {section.distance:.3f})")