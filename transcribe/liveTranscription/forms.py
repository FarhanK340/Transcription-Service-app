from django import forms
from .models import Session


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['session_name']
        widgets = {
            'session_name': forms.TextInput(attrs={
                'class': 'flex w-full p-2 border border-gray-300 rounded-md border-none outline-none',
                'placeholder':'Enter Session Name',
            }),
        }
