from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    View,
    TemplateView,
)
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Mailing, Message, Client, MailingAttempt, User
from .forms import MailingForm, MessageForm, ClientForm
from .services import send_mailing
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


# Клиенты
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "mailing/client_list.html"

    def get_queryset(self):
        if self.request.user.has_perm("mailing.view_all_clients"):
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("mailing:client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "mailing/client_form.html"
    success_url = reverse_lazy("mailing:client_list")

    def get_queryset(self):
        if self.request.user.has_perm("mailing.view_all_clients"):
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = "mailing/client_confirm_delete.html"
    success_url = reverse_lazy("mailing:client_list")

    def get_queryset(self):
        if self.request.user.has_perm("mailing.view_all_clients"):
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)


# Сообщения
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"

    def get_queryset(self):
        if self.request.user.has_perm("mailing.view_all_messages"):
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing/message_form.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_queryset(self):
        if self.request.user.has_perm("mailing.view_all_messages"):
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_queryset(self):
        if self.request.user.has_perm("mailing.view_all_messages"):
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


# Рассылки
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"

    def get_queryset(self):
        if self.request.user.has_perm("mailing.view_all_mailings"):
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing/mailing_form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_queryset(self):
        if self.request.user.has_perm("mailing.view_all_mailings"):
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_queryset(self):
        if self.request.user.has_perm("mailing.view_all_mailings"):
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailing/mailing_detail.html"

    def get_queryset(self):
        if self.request.user.has_perm("mailing.view_all_mailings"):
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)


# Отправка рассылки вручную
class SendMailingView(LoginRequiredMixin, View):
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        # Проверка прав доступа
        if not (
            request.user.has_perm("mailing.view_all_mailings")
            or mailing.owner == request.user
        ):
            messages.error(request, "У вас нет прав для отправки этой рассылки")
            return redirect("mailing:mailing_list")

        # Отправка рассылки
        success_count, total_count = send_mailing(mailing)

        if success_count > 0:
            messages.success(
                request, f"Рассылка отправлена. Успешно: {success_count}/{total_count}"
            )
        else:
            messages.error(
                request,
                f"Ошибка при отправке рассылки. Успешно: {success_count}/{total_count}",
            )

        return redirect("mailing:mailing_detail", pk=mailing.pk)


# Попытки рассылок
class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = "mailing/mailing_list.html"

    def get_queryset(self):
        if self.request.user.has_perm("mailing.view_all_mailings"):
            return MailingAttempt.objects.all()
        return MailingAttempt.objects.filter(mailing__owner=self.request.user)


class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.has_perm("mailing.view_all_mailings")


class UserManagerView(ManagerRequiredMixin, ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        return User.objects.all()


class BlockUserView(ManagerRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_blocked = not user.is_blocked
        user.save()

        action = "заблокирован" if user.is_blocked else "разблокирован"
        messages.success(request, f"Пользователь {user.email} {action}.")
        return redirect("users:user_list")


class DisableMailingView(ManagerRequiredMixin, View):
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.is_active = False
        mailing.save()

        messages.success(request, f'Рассылка "{mailing.name}" отключена.')
        return redirect("mailing:mailing_list")


class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = "mailing/statistics.html"

    @method_decorator(cache_page(60 * 15))  # Кеширование на 5 минут
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Получаем статистику из кеша или вычисляем
        cache_key = f"user_stats_{user.id}"
        stats = cache.get(cache_key)

        if not stats:
            mailings = Mailing.objects.filter(owner=user)
            attempts = MailingAttempt.objects.filter(mailing__owner=user)

            stats = {
                "total_mailings": mailings.count(),
                "active_mailings": mailings.filter(
                    status="started", is_active=True
                ).count(),
                "total_attempts": attempts.count(),
                "successful_attempts": attempts.filter(status="success").count(),
                "failed_attempts": attempts.filter(status="failure").count(),
                "success_rate": (
                    attempts.filter(status="success").count() / attempts.count() * 100
                    if attempts.count() > 0
                    else 0
                ),
                "mailings_by_status": mailings.values("status").annotate(
                    count=Count("id")
                ),
                "attempts_by_day": attempts.extra({"day": "date(attempt_time)"})
                .values("day")
                .annotate(count=Count("id"))
                .order_by("day"),
            }
            cache.set(cache_key, stats, 60 * 5)  # Кешируем на 5 минут

        context.update(stats)
        return context
