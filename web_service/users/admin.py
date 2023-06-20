from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


class UserRegAdmin(UserAdmin):
    """Регистрация модели User в админке"""

    list_display = 'email', 'is_superuser', 'is_staff', 'is_active',
    fieldsets = (
        (None, {'fields': ('email', 'password',)}),
        (_('персональная информация'),
         {'fields': ('username', 'first_name', 'last_name', 'surname', 'phone_number', 'photo',)}),
        (
            _('разрешения'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        (_('важные даты'), {'fields': ('last_login', 'date_joined',)}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2',),
            },
        ),
    )
    ordering = '-is_superuser', '-is_staff',
    search_fields = ("username",)


admin.site.register(User, UserRegAdmin)
AdminSite.site_header = 'Административная панель "КБ Маршал" сервис'