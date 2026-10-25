from django.core.management.base import BaseCommand, CommandError

from manuals.ai import AIError
from manuals.models import Manual
from manuals.rag import answer_question


class Command(BaseCommand):
    help = "Ask a question about the manuals."

    def add_arguments(self, parser):
        parser.add_argument("question", help="The question, in quotes.")
        parser.add_argument("--k", type=int, default=4, help="How many sections to use as sources (default 4).")
        parser.add_argument("--manual", type=int, help="ID of the manual to search in.")

    def handle(self, *args, **options):
        manual = None
        if options["manual"]:
            try:
                manual = Manual.objects.get(pk=options["manual"])
            except Manual.DoesNotExist:
                raise CommandError(f"No manual with ID {options['manual']}.")

        try:
            answer, sections = answer_question(options["question"], options["k"], manual)
        except AIError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(answer)
        if sections:
            self.stdout.write("\nSources:")
            for i, section in enumerate(sections, start=1):
                self.stdout.write(f"[{i}] {section} (distance {section.distance:.3f})")