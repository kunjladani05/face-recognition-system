from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    """
        A Django form for creating and updating UserProfile instances.

        Fields:
            - image: Profile picture of the user.
            - name: Full name of the user.
            - phone_number: Contact number of the user.
            - email: Email address of the user.
            - address: Residential address of the user.
            - date_of_birth: Date of birth of the user (input as a date picker).
            - age: Age of the user.
            - gender: Gender of the user.
            - height: Height of the user.
            - weight: Weight of the user.

        Widgets:
            - date_of_birth: Rendered as a date input.
            - address: Rendered as a textarea with 3 rows.
    """
    class Meta:
        model = UserProfile
        fields = ['image', 'name', 'phone_number', 'email', 'address', 'date_of_birth', 'age', 'gender', 'height', 'weight']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

