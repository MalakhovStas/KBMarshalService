from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from .forms import CustomSetPasswordForm
from .models import User

from utils.time_utils import get_time_left
from django.views.generic import DetailView, TemplateView


class HomePageView(TemplateView):
    """ Отображение главной страницы сайта """
    template_name = "home.j2"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days, hours, minutes, seconds = get_time_left()
        # context['banners'] = Banner.objects.get_active_banners()
        # context['top_products'] = get_top_products()
        # context["offer_of_the_day"] = get_offer_of_the_day()
        context["days"] = days
        context["hours"] = hours
        context["minutes"] = minutes
        context["seconds"] = seconds
        # context["hot_deals"] = hot_deals()
        # context["limited_edition_products"] = limited_edition_products()
        return context


class LoginUserView(SuccessMessageMixin, LoginView):
    """Аутентификация пользователя"""
    template_name = 'users/login.j2'
    success_url = reverse_lazy('users:home')

    def post(self, request, *args, **kwargs):
        """Метод, проверяющий существование пользователя и перенаправляющий его на соответствующую страницу."""
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(self.success_url)

        messages.add_message(
            self.request, messages.INFO, _('Неверный логин или пароль. Проверьте введённые данные'))
        return HttpResponseRedirect(reverse('users:login_user'))


class LogoutUserView(LogoutView):
    """Представления для выхода пользователя из аккаунта."""
    template_name = 'includes/header/wrap.j2'


class RegisterView(SuccessMessageMixin, FormView):
    """Регистрация пользователя. При методе POST, функция сохраняет полученные данные в кастомной модели User."""
    template_name = 'users/register.j2'
    form_class = UserCreationForm
    queryset = User.objects.all()
    success_url = reverse_lazy('users:login_user')

    def post(self, request, *args, **kwargs):
        """После регистрации, пользователю добавляется группа с разрешениями "покупатель"."""
        username = request.POST.get('username')
        email = request.POST.get('login')
        password = request.POST.get('pass')

        try:
            with transaction.atomic():
                user = User.objects.create(
                    username=username,
                    email=email,
                    password=make_password(password)
                )
                user_auth = authenticate(email=email, password=password)
                login(request, user_auth)
                group = Group.objects.get(name='buyer')
                user.groups.add(group)
                messages.add_message(
                    self.request, messages.INFO,
                    _('Вы успешно зарегистрированы! Введите пожалуйста ФИО.')
                )
                return HttpResponseRedirect(reverse('account:profile_user', kwargs={'pk': user.pk}))
        except ObjectDoesNotExist:
            messages.add_message(self.request, messages.INFO, _('К сожалению запрос не удался, попробуйте позже!'))
            return HttpResponseRedirect(reverse('users:register_user'))
        except IntegrityError:
            messages.add_message(self.request, messages.INFO, _('Вы уже зарегистрированы!'))
            return HttpResponseRedirect(self.success_url)


class PasswordResetRequestView(SuccessMessageMixin, PasswordResetView):
    """Представление по сбросу пароля по почте."""
    template_name = 'users/e-mail.j2'
    success_url = reverse_lazy('users:password_reset')
    subject_template_name = 'users/email/password_subject_reset_mail.txt'
    email_template_name = 'users/email/password_reset_mail.html'
    success_message = _('Письмо для восстановления пароля отправлено Вам на почту.')


class SetNewPasswordView(SuccessMessageMixin, PasswordResetConfirmView):
    """Представление установки нового пароля."""
    form_class = CustomSetPasswordForm
    template_name = 'users/password.j2'
    success_url = reverse_lazy('users:login_user')
    success_message = _('Пароль успешно изменён')
