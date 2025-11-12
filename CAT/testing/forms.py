from django import forms
from .models import Questions, Topic

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Questions
        fields = ['text_question', 'topic', 'difficulty', 'discrimination', 'guessing']
        widgets = {
            'text_question': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите текст вопроса',
                'rows': 3
            }),
            'topic': forms.Select(attrs={
                'class': 'form-select'
            }),
            'difficulty': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.5'
            }),
            'discrimination': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '1.0'
            }),
            'guessing': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.25'
            }),
        }
