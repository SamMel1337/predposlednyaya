from django import forms
from .models import Mailing, Message, Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["email", "full_name", "comment"]
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 3}),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["subject", "body"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 5}),
        }


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = [
            "name",
            "clients",
            "message",
            "start_time",
            "end_time",
            "frequency",
            "status",
            "is_active",
        ]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "clients": forms.SelectMultiple(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            # Ограничиваем выбор клиентов и сообщений только теми, которые принадлежат пользователю
            self.fields["clients"].queryset = Client.objects.filter(owner=user)
            self.fields["message"].queryset = Message.objects.filter(owner=user)
