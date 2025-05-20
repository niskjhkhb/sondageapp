from django import forms
from .models import Survey, Question, Choice, Answer
from django.forms import modelformset_factory, BaseFormSet

class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['title', 'description', 'is_anonymous']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter survey title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter survey description',
                'rows': 4
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'title': 'Survey Title',
            'description': 'Survey Description',
            'is_anonymous': 'Make responses anonymous'
        }
        help_texts = {
            'is_anonymous': 'If checked, responses will not collect user information'
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question text'}),
            'question_type': forms.Select(attrs={'class': 'form-select'})
        }
        labels = {
            'text': 'Question Text',
            'question_type': 'Type'
        }

class OptionForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter option text'})
        }
        labels = {
            'text': 'Option Text'
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['selected_choices', 'text_answer', 'scale_value']
        widgets = {
            'selected_choices': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'text_answer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter answer (if applicable)'}),
            'scale_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Scale value'})
        }
        labels = {
            'selected_choices': 'Selected Choices',
            'text_answer': 'Answer Text (if open-ended)',
            'scale_value': 'Scale Value'
        }

class BaseAnswerFormSet(BaseFormSet):
    pass