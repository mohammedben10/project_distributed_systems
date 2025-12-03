from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class CustomUserCreationForm(UserCreationForm):
    
    avatar = forms.ImageField(required=False)
    pay = forms.CharField(max_length=50)
    ville = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['username','last_name','email', 'password1', 'password2',
                  'avatar','pay','ville']
                  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.help_text = None
            field.widget.attrs.update({'class': 'form-control'})  # Add Bootstrap class

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            avatar = self.cleaned_data.get('avatar') or 'avatars/default.jpg'
            Profile.objects.create(
                user=user,
                avatar=avatar,
                pay=self.cleaned_data['pay'],
                ville=self.cleaned_data['ville']
            )
        return user

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'pay', 'ville']
        widgets = {
            'avatar': forms.FileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})