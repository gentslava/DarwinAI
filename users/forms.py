from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.forms import ModelForm
from django.contrib.auth import get_user_model
#from .models import CustomUser

User = get_user_model()

class CustomAuthenticationForm(forms.Form):
    login = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'id':'login', 'placeholder':'Login'}))
    password = forms.CharField(label='Пароль', max_length=255, widget=forms.PasswordInput(attrs={'id':'password', 'placeholder':'Password'}))

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                _("Аккаунт неактивен. Обратитесь к администратору"),
                code='inactive',
            )
            
class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'password')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'supermanager')
