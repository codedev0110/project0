from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    skill_level = forms.ChoiceField(
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        initial='beginner'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'skill_level', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.skill_level = self.cleaned_data['skill_level']
        if commit:
            user.save()
        return user

class ProfileForm(forms.ModelForm):
    preferred_languages = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Python, JavaScript, Go (comma-separated)'}),
        required=False,
        help_text='Enter programming languages you\'re interested in, separated by commas'
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'skill_level', 'preferred_languages']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_preferred_languages(self):
        languages_str = self.cleaned_data['preferred_languages']
        if languages_str:
            # Convert comma-separated string to list
            languages = [lang.strip() for lang in languages_str.split(',') if lang.strip()]
            return languages
        return []
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert list back to comma-separated string for display
        if self.instance and self.instance.preferred_languages:
            self.fields['preferred_languages'].initial = ', '.join(self.instance.preferred_languages)