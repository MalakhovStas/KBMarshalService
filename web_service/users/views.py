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


class LoginUserView(SuccessMessageMixin, LoginView):
    """ Аутентификация пользователя """
    template_name = 'users/login.j2'
    success_url = reverse_lazy('home')

    def post(self, request, *args, **kwargs):
        """ Метод, проверяющий существование пользователя и перенаправляющий его на соответствующую страницу """
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(self.success_url)

        messages.add_message(
            self.request, messages.INFO, _('Wrong login or password. Check the entered data'))
        return HttpResponseRedirect(reverse('users:login_user'))


class LogoutUserView(LogoutView):
    """ Представления для выхода пользователя из аккаунта """
    template_name = 'includes/header/wrap.j2'


class RegisterView(SuccessMessageMixin, FormView):
    """ Регистрация пользователя. При методе POST, функция сохраняет полученные данные в кастомной модели User """
    template_name = 'users/register.j2'
    form_class = UserCreationForm
    queryset = User.objects.all()
    success_url = reverse_lazy('users:login_user')

    def post(self, request, *args, **kwargs):
        """ После регистрации, пользователю добавляется группа "гость" """
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
                # group = Group.objects.get(name='users')
                group = Group.objects.get(name='guests')
                user.groups.add(group)
                messages.add_message(
                    self.request, messages.INFO,
                    _('You have successfully registered! Please enter your full name.')
                )
                return HttpResponseRedirect(reverse('account:profile_user', kwargs={'pk': user.pk}))
        except ObjectDoesNotExist:
            messages.add_message(
                self.request, messages.INFO, _('Unfortunately, the request failed, please try again later!'))
            return HttpResponseRedirect(reverse('users:register_user'))
        except IntegrityError:
            messages.add_message(self.request, messages.INFO, _('You are already registered!'))
            return HttpResponseRedirect(self.success_url)


class PasswordResetRequestView(SuccessMessageMixin, PasswordResetView):
    """ Представление по сбросу пароля по почте """
    template_name = 'users/e-mail.j2'
    success_url = reverse_lazy('users:password_reset')
    subject_template_name = 'users/email/password_subject_reset_mail.txt'
    email_template_name = 'users/email/password_reset_mail.html'
    success_message = _('A password recovery email has been sent to your email.')


class SetNewPasswordView(SuccessMessageMixin, PasswordResetConfirmView):
    """ Представление установки нового пароля """
    form_class = CustomSetPasswordForm
    template_name = 'users/password.j2'
    success_url = reverse_lazy('users:login_user')
    success_message = _('Password changed successfully')
