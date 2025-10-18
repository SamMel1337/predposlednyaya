from django.core.exceptions import PermissionDenied


def is_moderator(user):
    """Проверяет, является ли пользователь модератором"""
    return (
        user.groups.filter(name="moderators").exists()
        if user.is_authenticated
        else False
    )


def is_owner(user, obj):
    """Проверяет, является ли пользователь владельцем объекта"""
    return user.is_authenticated and obj.owner == user


def check_product_permissions(user, product, action):
    """Проверяет права доступа для действий с продуктом"""
    if not user.is_authenticated:
        raise PermissionDenied("Требуется авторизация")

    # Модераторы могут все
    if is_moderator(user):
        return True

    # Владелец может редактировать/удалять свои продукты
    if is_owner(user, product):
        return True

    # Все остальные случаи - доступ запрещен
    raise PermissionDenied(f"У вас нет прав для {action} этого продукта")
