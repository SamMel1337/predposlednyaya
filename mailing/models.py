from datetime import timezone
from django.db import models
from users.models import User


class Client(models.Model):
    email = models.EmailField(verbose_name="Email")
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    comment = models.TextField(verbose_name="Комментарий", blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец")

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        permissions = [
            ("view_all_clients", "Can view all clients"),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Тело письма")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        permissions = [
            ("view_all_messages", "Can view all messages"),
        ]

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    objects = None
    FREQUENCY_CHOICES = [
        ("daily", "Ежедневно"),
        ("weekly", "Еженедельно"),
        ("monthly", "Ежемесячно"),
    ]

    STATUS_CHOICES = [
        ("created", "Создана"),
        ("started", "Запущена"),
        ("completed", "Завершена"),
    ]

    name = models.CharField(max_length=100, verbose_name="Название рассылки")
    clients = models.ManyToManyField(Client, verbose_name="Клиенты")
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, verbose_name="Сообщение"
    )
    start_time = models.DateTimeField(verbose_name="Время начала")
    end_time = models.DateTimeField(verbose_name="Время окончания")
    frequency = models.CharField(
        max_length=10, choices=FREQUENCY_CHOICES, verbose_name="Периодичность"
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="created", verbose_name="Статус"
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        permissions = [
            ("view_all_mailings", "Can view all mailings"),
            ("disable_mailings", "Can disable mailings"),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Автоматическое обновление статуса при изменении времени
        now = timezone.now()
        if self.end_time and self.end_time < now:
            self.status = "completed"
        elif self.start_time and self.start_time <= now and self.status == "created":
            self.status = "started"
        super().save(*args, **kwargs)


class MailingAttempt(models.Model):
    STATUS_CHOICES = [
        ("success", "Успешно"),
        ("failure", "Неудача"),
    ]

    mailing = models.ForeignKey(
        Mailing, on_delete=models.CASCADE, verbose_name="Рассылка"
    )
    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name="Время попытки")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, verbose_name="Статус попытки"
    )
    server_response = models.TextField(blank=True, verbose_name="Ответ сервера")

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылки"

    def __str__(self):
        return f"{self.mailing} - {self.attempt_time}"
