from django.db import models
from django.utils.translation import gettext_lazy as _


class Debtor(models.Model):
    """ Модель Debtor(должник), для хранения информации о должниках """
    id_credit = models.CharField(max_length=12, null=True, blank=True, verbose_name=_('id credit'))
    surname = models.CharField(max_length=256, null=False, verbose_name=_('surname'))
    name = models.CharField(max_length=256, null=False, verbose_name=_('name'))
    patronymic = models.CharField(max_length=256, null=True, blank=True, verbose_name=_('patronymic'))
    date_birth = models.DateField(null=False, verbose_name=_('date birth'))
    ser_num_pass = models.CharField(max_length=10, unique=True, null=False, verbose_name=_('series passport number'))
    date_issue_pass = models.DateField(null=True, blank=True, verbose_name=_('passport issue date'))
    name_org_pass = models.CharField(max_length=512, null=True, blank=True,
                                     verbose_name=_('name of the organization issuing the passport'))
    inn = models.CharField(null=True, blank=True, max_length=12, verbose_name=_('INN'))
    isp_prs = models.JSONField(null=True, blank=True, verbose_name=_('enforcement proceedings'))
    date_added = models.DateTimeField(auto_now_add=True, verbose_name=_('date added'))
    modification_date = models.DateTimeField(auto_now=True, verbose_name=_('modification date'))

    class Meta:
        verbose_name = _('debtor')
        verbose_name_plural = _('debtors')
        ordering = 'surname', 'name', 'patronymic'

    def __repr__(self):
        """Переопределение __repr__, для отображения модели."""
        return _("Debtor") + f': {self.surname} {self.name} {self.patronymic} | ' + _("INN") + f': {self.inn}'

    def __str__(self):
        """Переопределение __str__, для отображения модели."""
        return _("Debtor") + f': {self.surname} {self.name} {self.patronymic} | ' + _("INN") + f': {self.inn}'
