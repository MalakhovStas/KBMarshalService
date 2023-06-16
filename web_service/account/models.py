# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from users.models import User
#
#
# class HistorySearch(models.Model):
#     """ История просмотров пользователя """
#     user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('пользователь'), related_name='history')
#     product = models.ManyToManyField(
#         Product, through="HistorySearchProduct", related_name='history', verbose_name=_("продукт")
#     )
#
#     class Meta:
#         verbose_name = _('история просмотров')
#         verbose_name_plural = _('история просмотров')
#
#     def __str__(self):
#         return f'{self.user}'
#
#
# class HistorySearchProduct(models.Model):
#     """ Объект истории просмотра пользователя """
#     history = models.ForeignKey(
#         HistorySearch, on_delete=models.CASCADE, verbose_name=_("история"), related_name='history_products')
#     product = models.ForeignKey(
#         Product, on_delete=models.CASCADE, verbose_name=_("продукт"), related_name='history_products')
#     date = models.DateTimeField(auto_now_add=True, verbose_name=_('дата'))
#
#     class Meta:
#         verbose_name = _('история просмотра продукта')
#         verbose_name_plural = _('история просмотра продуктов')
#
#     def __str__(self):
#         return f'{self.history} | {self.date} | {self.product}'