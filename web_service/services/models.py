from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


def validate_num_person_in_group_request(value):
    if value < 1:
        raise ValidationError(
            _("Value must be more than 0"),
            params={"value": value},
        )


class Service(models.Model):
    """ Модель Service(Сервис) - для хранения данных сервиса """
    title = models.CharField(max_length=64, verbose_name=_('title'))
    description = models.TextField(max_length=2056, null=True, blank=True, verbose_name=_('description'))
    host = models.CharField(max_length=2056, null=True, blank=True, verbose_name=_('host'))
    key = models.CharField(max_length=2056, null=True, blank=True, verbose_name=_('key'))
    num_person_in_group_request = models.SmallIntegerField(
        verbose_name=_('max persons for group request'), default=1, validators=[validate_num_person_in_group_request])
    date_added = models.DateTimeField(auto_now_add=True, verbose_name=_('date added'))
    modification_date = models.DateTimeField(auto_now=True, verbose_name=_('modification date'))

    class Meta:
        verbose_name = _('service')
        verbose_name_plural = _('services')

    def __str__(self):
        """Переопределение __str__, для отображения модели."""
        return f"{_('Service')}: {self.title} |  {_('host')}: {self.host}"


class Method(models.Model):
    """Метод для обращения к сервису"""
    service = models.ForeignKey(to=Service,  on_delete=models.CASCADE, related_name='methods', verbose_name=_('service'))
    title = models.CharField(max_length=64, verbose_name=_('title'))
    type = models.CharField(max_length=64, verbose_name=_('type'))
    url = models.CharField(max_length=2056, verbose_name=_('url'))
    params = models.JSONField(blank=True, null=True, verbose_name=_('parameters'))
    description = models.CharField(blank=True, null=True, max_length=2056, verbose_name=_('description'))

    class Meta:
        verbose_name = _('method')
        verbose_name_plural = _('methods')

    def __str__(self):
        """Переопределение __str__, для отображения модели."""
        return f"{_('title')}: {self.title} | url: {self.url}"

    def generate_url(self, **kwargs):
        """Формирует url с учётом типа, метода, параметров и их значений для обращения к сервису"""
        url = _('url generation error')
        if self.type.upper() == "GET":
            url = f'{self.service.host}{self.url}?{"&".join([f"{param}={kwargs[param]}" for param in self.params])}'
        if self.type.upper() == "POST":
            pass
        return url


# class Param(models.Model):
#     """Параметр метода для обращения к сервису"""
#     title = models.CharField(max_length=64, verbose_name=_('title'))
#     type_value = models.CharField(max_length=64, verbose_name=_('type value'))
#     description = models.CharField(blank=True, null=True, max_length=2056, verbose_name=_('description'))
#
#     # param = models.ForeignKey(to='Param', on_delete=models.CASCADE, related_name='params', verbose_name=_('parameter'))
#
#     class Meta:
#         verbose_name = _('parameter')
#         verbose_name_plural = _('parameters')
#
#     def __str__(self):
#         """Переопределение __str__, для отображения модели."""
#         return f"{_('title')}: {self.title} | {_('type')}: {self.type_value}"
