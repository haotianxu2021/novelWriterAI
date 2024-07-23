from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import NovelProject
from django import forms

class GptInputForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, label='Text to Generate')
    api_choice = forms.ChoiceField(choices=[('chatgpt', 'ChatGPT'), ('kimi', 'Kimi'), ('claude', 'Claude')], label='API Choice')
    novel_project = forms.ChoiceField(choices=[], required=False, label='Choose an existing project')
    new_project_title = forms.CharField(max_length=200, required=False, label='Or create a new project title')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(GptInputForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['novel_project'].choices = [('', 'Select a project')] + [(project.id, project.title) for project in NovelProject.objects.filter(user=user)]

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class TextGenerationForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)

class SummaryForm(forms.Form):
    response = forms.CharField(widget=forms.Textarea, label='Text to Save')
    api_choice = forms.ChoiceField(choices=[('chatgpt', 'ChatGPT'), ('kimi', 'Kimi'), ('claude', 'Claude')], label='API Choice')
    project_id = forms.ChoiceField(choices=[], required=False, label='Choose an existing project')
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        initial = kwargs.pop('initial', {})
        super(SummaryForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['project_id'].choices = [('', 'Select a project')] + [(project.id, project.title) for project in NovelProject.objects.filter(user=user)]
        self.data = initial