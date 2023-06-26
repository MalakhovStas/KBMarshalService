from django.db import models
from django.utils.translation import gettext_lazy as _


class Debtor(models.Model):
    """ Модель Debtor(должник), для хранения информации о должниках """

    surname = models.CharField(max_length=256, null=True, blank=True, verbose_name=_('surname'))
    name = models.CharField(max_length=256, null=True, blank=True, verbose_name=_('name'))
    patronymic = models.CharField(max_length=256, null=True, blank=True, verbose_name=_('patronymic'))
    date_birth = models.DateTimeField(verbose_name=_('birthdate'))
    ser_num_pass = models.CharField(
        max_length=256, unique=True, null=True, blank=True, verbose_name=_('series passport number'))
    date_issue_pass = models.DateTimeField(verbose_name=_('passport issue date'))
    name_org_pass = models.CharField(
        max_length=256, null=True, blank=True, verbose_name=_('name of the organization issuing the passport'))
    inn = models.IntegerField(verbose_name='INN')
    isp_prs = models.JSONField(verbose_name=_('enforcement proceedings'))

    class Meta:
        verbose_name = _('debtor')
        verbose_name_plural = _('debtors')
        ordering = 'surname', 'name', 'patronymic'

    def __str__(self):
        """Переопределение __str__, для отображения модели."""
        return f'{self.surname} {self.name} {self.patronymic} | {_("INN")}: {self.inn}'
