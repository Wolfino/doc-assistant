from django import forms

from .models import Manual


class GenerateManualForm(forms.Form):
    topic = forms.CharField(
        label="Topic",
        max_length=200,
        widget=forms.TextInput(attrs={"placeholder": "e.g. automatic coffee machine with built-in grinder"}),
    )
    sections = forms.IntegerField(label="Number of sections", min_value=1, max_value=10, initial=4)


class AskForm(forms.Form):
    question = forms.CharField(
        label="Question",
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "e.g. How do I reset the router?"}),
    )
    manual = forms.ModelChoiceField(
        label="Search in",
        queryset=Manual.objects.order_by("title"),
        required=False,
        empty_label="All manuals",
    )