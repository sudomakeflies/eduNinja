from django import forms
from .models import Question, Evaluation
from django_select2 import forms as s2forms

class EvaluationForm(forms.ModelForm):
    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.all(),
        widget=s2forms.Select2MultipleWidget,
        required=False
    )

    class Meta:
        model = Evaluation
        fields = '__all__'
