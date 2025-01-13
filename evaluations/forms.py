from django import forms
from .models import Question, Evaluation, Option
from django_select2 import forms as s2forms
from django.contrib import admin

class EvaluationForm(forms.ModelForm):
    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.all(),
        widget=s2forms.Select2MultipleWidget,
        required=False
    )

    class Meta:
        model = Evaluation
        fields = '__all__'

from django.contrib.auth.models import User
from .models import UserProfile

class UserAdminForm(forms.ModelForm):
    grado = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'profile'):
            self.fields['grado'].initial = self.instance.profile.grado

    def save(self, commit=True):
        user = super().save(commit=False)
        grado = self.cleaned_data.get('grado')
        if commit:
            user.save()
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.grado = grado
            profile.save()
        return user

    class Meta:
        model = User
        fields = '__all__'

class QuestionAdminForm(forms.ModelForm):
    options = forms.ModelMultipleChoiceField(
        queryset=Option.objects.all(),
        widget=admin.widgets.FilteredSelectMultiple('Options', is_stacked=False),
        label="Options",
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['options'].label_from_instance = self.label_from_instance

    def label_from_instance(self, obj):
        return obj.text

    class Meta:
        model = Question
        fields = '__all__'
