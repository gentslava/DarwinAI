from django import forms

class UploadForm(forms.Form):
    file = forms.FileField(
        label = "Выберите файлы",
        label_suffix = "",
        widget = forms.FileInput(attrs={'id': 'audio-input', 'accept': 'audio/*', 'multiple': 'true' }),
    )

class AddManagerForm(forms.Form):
    first_name = forms.CharField(
        label = "",
        label_suffix = "",
        widget=forms.TextInput(attrs={'pattern': '^[A-Za-zА-Яа-яЁё]+$'}),
    )
    last_name = forms.CharField(
        label = "",
        label_suffix = "",
        widget=forms.TextInput(attrs={'pattern': '^[A-Za-zА-Яа-яЁё]+$'}),
    )
    department = forms.CharField(
        label = "",
        label_suffix = "",
        widget=forms.TextInput(attrs={}),
    )

class CustomRegistrationForm(forms.Form):
    login = forms.CharField(
        label = "",
        label_suffix = "",
        max_length = 255,
        widget=forms.TextInput(attrs={'placeholder': 'Login'}),
    )
    email = forms.EmailField(
        label = "",
        label_suffix = "",
        max_length = 255,
        widget=forms.TextInput(attrs={'placeholder': 'E-mail'}),
    )
    password = forms.CharField(
        label = "",
        label_suffix = "",
        max_length = 255,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
    )

class WordsForm(forms.Form):
    word = forms.CharField(
        label = "",
        label_suffix = "",
        max_length = 255,
        widget=forms.TextInput(attrs={'placeholder': 'Введите фразу или слово'}),
    )

class AddScriptForm(forms.Form):
    name = forms.CharField(
        label = "",
        label_suffix = "",
        widget=forms.TextInput(attrs={}),
    )
    product = forms.CharField(
        label = "",
        label_suffix = "",
        required = False,
        widget=forms.TextInput(attrs={}),
    )