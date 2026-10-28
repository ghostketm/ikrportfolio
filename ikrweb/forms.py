# ikrweb/forms.py
from django import forms
from .models import Contact


class ContactForm(forms.ModelForm):
    """
    Contact / consultation request form.
    Widgets include Bootstrap classes for consistent styling.
    """

    class Meta:
        model  = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'autocomplete': 'name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com',
                'autocomplete': 'email',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'What would you like to discuss?',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Tell me about your project or inquiry…',
            }),
        }
        labels = {
            'name':    'Your Name',
            'email':   'Email Address',
            'subject': 'Subject',
            'message': 'Message',
        }

    def clean_message(self):
        """Reject very short messages to reduce spam."""
        message = self.cleaned_data.get('message', '')
        if len(message.strip()) < 10:
            raise forms.ValidationError(
                "Please provide a more detailed message (at least 10 characters)."
            )
        return message