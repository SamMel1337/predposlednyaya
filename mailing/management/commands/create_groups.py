from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Create user groups with permissions"

    def handle(self, *args, **options):
        # Создание группы менеджеров
        manager_group, created = Group.objects.get_or_create(name="Менеджеры")

        # Добавление прав для менеджеров
        permissions = Permission.objects.filter(
            codename__in=[
                "view_all_mailings",
                "view_all_messages",
                "view_all_clients",
                "disable_mailings",
            ]
        )

        manager_group.permissions.set(permissions)
        manager_group.save()

        self.stdout.write(self.style.SUCCESS("Groups created successfully"))
