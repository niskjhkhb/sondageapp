from django import forms
from .models import Sondage, Question, Choice
from django.forms import inlineformset_factory

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'required']


class FilterForm(forms.Form):
    user = forms.CharField(required=False, label='User')
    date = forms.DateField(required=False, label='Date (YYYY-MM-DD)')

def apply_filters(responses, user, date):
    if user:
        responses = responses.filter(user__username__icontains=user)
    if date:
        responses = responses.filter(date__date=date)
    return responses

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
    
