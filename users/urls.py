from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("accounts/login/", views.UserLoginView.as_view(), name="login"),
    path("accounts/logout/", views.UserLogoutView.as_view(), name="logout"),
    path("verify/<str:token>/", views.VerifyEmailView.as_view(), name="verify_email"),
    path("reset-password/", views.PasswordResetView.as_view(), name="reset_password"),
    path(
        "reset-password/<str:token>/",
        views.PasswordResetConfirmView.as_view(),
        name="reset_password_confirm",
    ),
]
