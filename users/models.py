from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    DoesNotExist = None
    username = None
    email = models.EmailField(unique=True, verbose_name="Email")
    avatar = models.ImageField(
        upload_to="users/", verbose_name="Аватар", null=True, blank=True
    )
    phone = models.CharField(
        max_length=20, verbose_name="Телефон", null=True, blank=True
    )
    country = models.CharField(
        max_length=100, verbose_name="Страна", null=True, blank=True
    )
    is_blocked = models.BooleanField(default=False, verbose_name="Заблокирован")
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    password_reset_token = models.CharField(max_length=100, blank=True, null=True)
    email_verified = models.BooleanField(
        default=False, verbose_name="Email подтвержден"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        permissions = [
            ("can_view_users", "Can view all users"),
            ("can_block_users", "Can block users"),
        ]

    def __str__(self):
        return self.email

    @property
    def is_active(self):
        """Переопределенное свойство is_active с кастомной логикой"""
        return self._is_active_original and not self.is_blocked and self.email_verified

    @is_active.setter
    def is_active(self, value):
        """Сеттер для is_active"""
        self._is_active_original = value
        # Дополнительная логика при изменении статуса
        if not value:
            self._handle_deactivation()

    def _handle_deactivation(self):
        """Обработка деактивации пользователя"""
        # Здесь можно добавить логику отправки email, логирования и т.д.
        print(f"Пользователь {self.username} деактивирован")

    def save(self, CustomUser=None, *args, **kwargs):
        """Дополнительная логика при сохранении"""
        if self.pk:
            # Проверяем изменения статуса
            old_user = CustomUser.objects.get(pk=self.pk)
            if old_user.is_active != self.is_active:
                self._notify_status_change()

        super().save(*args, **kwargs)
