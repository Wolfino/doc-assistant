from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .ai import AIError
from .forms import AskForm, GenerateManualForm
from .models import Manual
from .rag import answer_question
from .services import create_manual_with_ai


def manual_list(request):
    manuals = Manual.objects.order_by("-created_at")
    return render(request, "manuals/manual_list.html", {"manuals": manuals})


def manual_detail(request, pk):
    manual = get_object_or_404(Manual, pk=pk)
    return render(request, "manuals/manual_detail.html", {"manual": manual})


def generate_manual(request):
    form = GenerateManualForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            manual = create_manual_with_ai(form.cleaned_data["topic"], form.cleaned_data["sections"])
        except AIError as exc:
            messages.error(request, f"Generazione non riuscita: {exc}")
        else:
            messages.success(request, "Manuale generato e indicizzato.")
            return redirect("manuals:detail", pk=manual.pk)
    return render(request, "manuals/generate.html", {"form": form})


def ask(request):
    form = AskForm(request.POST or None)
    answer, sources = None, []
    if request.method == "POST" and form.is_valid():
        try:
            answer, sources = answer_question(
                form.cleaned_data["question"],
                manual=form.cleaned_data["manual"],
            )
        except AIError as exc:
            messages.error(request, f"Risposta non riuscita: {exc}")
    return render(request, "manuals/ask.html", {"form": form, "answer": answer, "sources": sources})