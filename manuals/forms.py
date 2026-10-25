from django import forms

from .models import Manual


class GenerateManualForm(forms.Form):
    topic = forms.CharField(
        label="Argomento",
        max_length=200,
        widget=forms.TextInput(attrs={"placeholder": "Es. macchina del caffè automatica"}),
    )
    sections = forms.IntegerField(label="Numero di sezioni", min_value=1, max_value=10, initial=4)


class AskForm(forms.Form):
    question = forms.CharField(
        label="Domanda",
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Es. come si ripristina il router?"}),
    )
    manual = forms.ModelChoiceField(
        label="Cerca in",
        queryset=Manual.objects.order_by("title"),
        required=False,
        empty_label="Tutti i manuali",
    )