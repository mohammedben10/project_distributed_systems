from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

# --- 1. Formulaire d'inscription (Corrigé) ---
class CustomUserCreationForm(UserCreationForm):
    avatar = forms.ImageField(required=False)
    pay = forms.CharField(max_length=50, label="Pays")
    ville = forms.CharField(max_length=50, label="Ville")

    class Meta:
        model = User
        # On ne met QUE les champs qui existent vraiment dans User
        fields = ['username', 'last_name', 'email'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = None
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Création du profil associé
            avatar = self.cleaned_data.get('avatar')
            Profile.objects.create(
                user=user,
                avatar=avatar if avatar else 'avatars/default.jpg',
                pay=self.cleaned_data['pay'],
                ville=self.cleaned_data['ville']
            )
        return user

# --- 2. Formulaire de mise à jour User (Que tu avais perdu) ---
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

# --- 3. Formulaire de mise à jour Profile (Que tu avais perdu) ---
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