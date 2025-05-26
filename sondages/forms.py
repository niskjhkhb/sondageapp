from django import forms
from .models import Sondage, Question, Choice
from django.forms import inlineformset_factory

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'required']


ChoiceFormSet = inlineformset_factory(
    Question,
    Choice,
    fields=('text',),
    extra=1,
    can_delete=True,
)


class SondageForm(forms.ModelForm):
    class Meta:
        model = Sondage
        fields = ['title', 'description']
       