from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import models
from django.contrib.auth.models import User
from .models import PatientData
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label="Имя Пользователя")
    password = forms.CharField(label = "Пароль", widget=forms.PasswordInput)


class RegistrationForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(label='Имя', max_length=100)
    last_name = forms.CharField(label='Фамилия', max_length=100)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name','last_name']


class ManualDataForm(forms.Form):
    date = forms.DateField(label='Дата')
    time = forms.TimeField(label='Время')
    spo2 = forms.IntegerField(label='SpO2')
    heart_rate = forms.IntegerField(label='Пульс')
    body_temperature = forms.FloatField(label='Температура тела')