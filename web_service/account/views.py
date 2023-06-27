from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView

from users.models import User
# from account.models import HistorySearch
from .services import change_profile
from datetime import datetime


class AccountUser(DetailView):
    """Представления для отображения информации о пользователе на странице аккаунта. """
    template_name = 'account/account.j2'
    context_object_name = 'user'
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(pk=self.request.user.pk)
        context['date_joined'] = datetime.strftime(user.date_joined, '%d.%m.%Y-%H:%M')
        return context


class ProfileUser(SuccessMessageMixin, View):
    """Представления для редактирования профиля пользователя. """
    template_name = 'account/profile.j2'

    def get_success_url(self):
        """Возвращаемый URL при успешном выполнении методов."""
        return reverse_lazy('account:profile_user', kwargs={'pk': self.kwargs['pk']})

    def get_queryset(self):
        """Queryset модели пользователя."""
        user = User.objects.filter(pk=self.request.user.pk)
        return user

    def get(self, request, *args, **kwargs):
        """Получение страницы для редактирования профиля."""
        context = {'user': self.get_queryset().get()}
        return render(self.request, template_name=self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        """Метод изменения данных пользователя."""
        info = change_profile(request, self.get_queryset())
        messages.add_message(self.request, messages.INFO, info)
        return HttpResponseRedirect(self.get_success_url())


# class HistorySearchView(ListView):
#     """ Представление для отображения страницы истории просмотров пользователя """
#     template_name = 'account/history.j2'
#     context_object_name = 'history'
#
#     def get_queryset(self):
#         queryset = HistorySearch.objects.get(user=self.request.user.pk)
#         return queryset
