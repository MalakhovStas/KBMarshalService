from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from .manager import CustomUserManager


class User(AbstractUser):
    """Абстрактная модель User, добавляет в стандартную модель дополнительные поля."""
    email = models.EmailField(unique=True, verbose_name=_('электронная почта'))
    username = models.CharField(max_length=256, unique=True, null=True, blank=True, verbose_name=_('никнейм'))
    surname = models.CharField(max_length=256, blank=True, null=True, verbose_name=_('отчество'))
    phone_number = PhoneNumberField(unique=False, null=True, blank=True, verbose_name=_('номер телефона'))
    photo = models.ImageField(upload_to='users_foto/', null=True, blank=True, verbose_name=_('фотография'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        """Класс, определяющий некоторые параметры модели."""
        verbose_name = _('пользователь')
        verbose_name_plural = _('пользователи')
        ordering = '-is_superuser', '-date_joined', '-is_active'

    def __str__(self):
        """Переопределение __str__, для отображения email в названии объекта."""
        return self.email
