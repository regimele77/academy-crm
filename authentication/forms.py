from django import forms

from .models import CRMUserModel

ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
MAX_PROFILE_PICTURE_BYTES = 5 * 1024 * 1024


class ContactProfileForm(forms.ModelForm):
    class Meta:
        model = CRMUserModel
        fields = ['first_name', 'last_name', 'email', 'phone', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'First name',
                'autocomplete': 'given-name',
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Last name',
                'autocomplete': 'family-name',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'you@example.com',
                'autocomplete': 'email',
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Phone number',
                'autocomplete': 'tel',
            }),
            'profile_picture': forms.FileInput(attrs={
                'accept': 'image/jpeg,image/png,image/webp,image/gif',
                'data-profile-input': 'true',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].label = 'First name'
        self.fields['last_name'].label = 'Last name'
        self.fields['email'].label = 'Email'
        self.fields['phone'].label = 'Phone'
        self.fields['profile_picture'].label = 'Profile picture'
        self.fields['profile_picture'].required = False

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if not picture or not hasattr(picture, 'content_type'):
            return picture

        if picture.content_type not in ALLOWED_IMAGE_TYPES:
            raise forms.ValidationError('Use a JPEG, PNG, WebP, or GIF image.')

        if picture.size > MAX_PROFILE_PICTURE_BYTES:
            raise forms.ValidationError('Profile picture must be 5 MB or smaller.')

        return picture
