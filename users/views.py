from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, FormView, TemplateView
from django.contrib.auth.views import LoginView
from django.contrib import messages
from .forms import (
    UserRegisterForm,
    UserProfileForm,
    UserLoginForm,
    PasswordResetForm,
    PasswordResetConfirmForm,
)
from .models import User


class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Регистрация успешна! Проверьте вашу почту для подтверждения email.",
        )
        return response


class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = "users/login.html"


class UserLogoutView(LoginRequiredMixin, FormView):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "Вы успешно вышли из системы.")
        return redirect("mailing:base")


class VerifyEmailView(TemplateView):
    template_name = "users/verify_email.html"

    def get(self, request, *args, **kwargs):
        token = kwargs.get("token")
        try:
            user = User.objects.get(email_verification_token=token)
            user.email_verified = True
            user.email_verification_token = None
            user.save()
            messages.success(
                request, "Email успешно подтвержден! Теперь вы можете войти в систему."
            )
            return redirect("users:login")
        except User.DoesNotExist:
            messages.error(request, "Неверная ссылка подтверждения.")
            return redirect("mailing:base")


class PasswordResetView(FormView):
    form_class = PasswordResetForm
    template_name = "users/password_reset.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        user = User.objects.get(email=email)
        form.send_reset_email(user)
        messages.success(
            self.request, "Инструкции по восстановлению пароля отправлены на ваш email."
        )
        return super().form_valid(form)


class PasswordResetConfirmView(FormView):
    form_class = PasswordResetConfirmForm
    template_name = "users/password_reset_confirm.html"
    success_url = reverse_lazy("users:login")

    def get(self, request, *args, **kwargs):
        token = kwargs.get("token")
        if not User.objects.filter(password_reset_token=token).exists():
            messages.error(request, "Неверная ссылка восстановления пароля.")
            return redirect("mailing:base")
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        token = self.kwargs.get("token")
        user = get_object_or_404(User, password_reset_token=token)
        user.set_password(form.cleaned_data["password1"])
        user.password_reset_token = None
        user.save()
        messages.success(self.request, "Пароль успешно изменен!")
        return super().form_valid(form)
