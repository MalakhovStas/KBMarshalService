from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.validators import validate_email
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _


def change_profile(request: HttpRequest, user: QuerySet):
    """Функция принимающая данные метода POST на странице профиля пользователя и вносящая изменение в модель User."""

    # изменение ФИО
    if request.POST.get('name'):
        fio = request.POST.get('name').split()
        while len(fio) < 3:
            fio.append('')
        user.update(
            first_name=fio[0],
            last_name=fio[1],
            surname=fio[2]
        )

    # изменение Никнейм
    if request.POST.get('username'):
        user.update(username=request.POST.get('username'))

    # изменение номера телефона
    if request.POST.get('phone'):
        phone = request.POST.get('phone')
        user.update(
            phone_number=phone
        )

    # изменение аватарки
    if request.FILES:
        file = request.FILES['avatar']
        file_system = FileSystemStorage()
        filename = file_system.save(file.name, file)
        user.update(
            photo=filename
        )

    # изменение электронной почты
    if request.POST.get('mail'):
        email = request.POST.get('mail')
        try:
            validate_email(email)
            user.update(
                email=email
            )

            password = user.values('password')[0].get('password')
            user_login = authenticate(email=email, password=password)
            login(request, user_login)
        except ValidationError:
            return _('Email does not meet the requirements!')

    # изменение пароля
    if request.POST.get('password') and request.POST.get('passwordReply'):
        password1 = request.POST.get('password')
        password2 = request.POST.get('passwordReply')
        if password1 == password2:
            user.update(
                password=make_password(password1)
            )
            email = user.values('email')[0].get('email')
            user_login = authenticate(email=email, password=password1)
            login(request, user_login)
        else:
            return _('Password mismatch!')
    return _('Profile changed successfully.')
