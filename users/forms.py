from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.contrib.auth import authenticate
from .models import User


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    password1 = forms.CharField(
        label="Пароль", widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = User
        fields = ["email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False  # Пользователь не активен до подтверждения email
        user.email_verification_token = get_random_string(50)

        if commit:
            user.save()
            self.send_verification_email(user)

        return user

    def send_verification_email(self, user):
        subject = "Подтверждение регистрации"
        message = f"""
        Для подтверждения регистрации перейдите по ссылке:
        http://localhost:8000/users/verify/{user.email_verification_token}/
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(
        label="Пароль", widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    def clean(self):
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise ValidationError("Неверный email или пароль")
            if not user.is_active:
                raise ValidationError("Аккаунт не активирован. Проверьте вашу почту.")

        return super().clean()


class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email не найден")
        return email

    def send_reset_email(self, user):
        token = get_random_string(50)
        user.password_reset_token = token
        user.save()

        subject = "Восстановление пароля"
        message = f"""
        Для восстановления пароля перейдите по ссылке:
        http://localhost:8000/users/reset-password/{token}/
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


class PasswordResetConfirmForm(forms.Form):
    password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    def clean(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают")

        return self.cleaned_data


class UserProfileForm:
    pass
