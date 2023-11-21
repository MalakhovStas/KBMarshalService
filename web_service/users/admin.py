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
        (_('personal information'),
         {'fields': (
             'username',
             'first_name',
             'last_name',
             'surname',
             'phone_number',
             'photo',
             "tg_user_id",
             "tg_username"
         )}),
        (
            _('permissions'),
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
        (_('important dates'), {'fields': ('last_login', 'date_joined',)}),
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
AdminSite.site_header = _('Admin panel "KB Marshal" service')
