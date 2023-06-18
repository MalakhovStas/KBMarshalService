from django.db import models
from django.utils.translation import gettext_lazy as _


class Debtor(models.Model):
    """ Модель Debtor(должник), для хранения информации о должниках """
    surname = models.CharField(max_length=256, null=True, blank=True, verbose_name=_('фамилия'))
    name = models.CharField(max_length=256, null=True, blank=True, verbose_name=_('имя'))
    patronymic = models.CharField(max_length=256, null=True, blank=True, verbose_name=_('отчество'))
    date_birth = models.DateTimeField(verbose_name=_('дата рождения'))
    ser_num_pass = models.CharField(max_length=256, unique=True, null=True, blank=True, verbose_name=_('серия номер паспорта'))
    date_issue_pass = models.DateTimeField(verbose_name=_('дата выдачи паспорта'))
    name_org_pass = models.CharField(max_length=256, null=True, blank=True, verbose_name=_('название организации выдывшей паспорт'))
    inn = models.IntegerField(verbose_name='ИНН')
    isp_prs = models.JSONField(verbose_name=_('исполнительные производства'))

    class Meta:
        """Класс, определяющий некоторые параметры модели."""
        verbose_name = _('должник')
        verbose_name_plural = _('должники')
        ordering = 'surname', 'name', 'patronymic'

    def __str__(self):
        """Переопределение __str__, для отображения модели."""
        return f'{self.surname} {self.name} {self.patronymic} | ИНН: {self}'
