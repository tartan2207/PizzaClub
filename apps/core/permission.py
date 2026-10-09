from rest_framework import permissions


class IsAdminOrOwnerReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Безопасные методы (GET, HEAD, OPTIONS) доступны всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Все остальные действия требуют авторизации
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Удаление — только для администраторов и суперюзеров
        if request.method == 'DELETE':
            return bool(
                request.user and (request.user.is_staff or request.user.is_superuser)
            )

        # Редактирование (PATCH/PUT) — только для владельца отзыва или админа
        return obj.user == request.user or request.user.is_staff or request.user.is_superuser