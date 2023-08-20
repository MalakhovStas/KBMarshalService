from django.db import models
from django.utils.translation import gettext_lazy as _


class Service(models.Model):
    """ Модель Service(Сервис) - для хранения данных сервиса """
    title = models.CharField(max_length=512, verbose_name=_('title'))
    description = models.TextField(max_length=4112, null=True, blank=True, verbose_name=_('description'))
    host = models.CharField(max_length=512, null=True, blank=True, verbose_name=_('host'))
    key = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_('key'))
    date_added = models.DateTimeField(auto_now_add=True, verbose_name=_('date added'))
    modification_date = models.DateTimeField(auto_now=True, verbose_name=_('modification date'))

    class Meta:
        verbose_name = _('service')
        verbose_name_plural = _('services')

    def __str__(self):
        """Переопределение __str__, для отображения модели."""
        return f"{_('Service')}: {self.title}"
