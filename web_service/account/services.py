from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.validators import validate_email
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

# from shops.models import Shop
from users.models import User


def change_profile(request: HttpRequest, user: QuerySet):
    """Функция принимающая данные метода POST на странице профиля пользователя и вносящая изменение в модель User."""

    # изменение ФИО
    if request.POST.get('name'):
        data = request.POST.get('name').split()
        user.update(
            last_name=data[0],
            first_name=data[1],
            surname=data[2]
        )

    # изменение номера телефона
    if request.POST.get('phone'):
        phone = request.POST.get('phone')
        user.update(
            phone_number=phone
        )

    # изменение аватарки
    if request.FILES:
        file = request.FILES['avatar']
        fail_system = FileSystemStorage()
        filename = fail_system.save(file.name, file)
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
            return _('Email не соответствует требованиям!')

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
            return _('Пароли не совпадают!')
    return _('Профиль успешно изменён.')


# class ShopManager:
#     """Класс для добавления или редактирования магазина."""
#
#     def __init__(self, data, user_pk):
#         """Инициализация класса."""
#         self.name = data.get('name')
#         self.description = data.get('description')
#         self.phone_number = data.get('phone')
#         self.address = data.get('address')
#         self.email = data.get('mail')
#         self.user = User.objects.get(pk=user_pk)
#
#     def create(self):
#         """Добавление магазина."""
#         Shop.objects.create(
#             name=self.name,
#             description=self.description,
#             phone_number=self.phone_number,
#             address=self.address,
#             email=self.email,
#             user=self.user
#         )
#         group = Group.objects.get(name='seller')
#         self.user.groups.add(group)
#         return _('Магазин успешно добавлен!')
#
#     def update(self):
#         """Редактирование магазина."""
#         try:
#             validate_email(self.email)
#             Shop.objects.filter(user_id=self.user).update(
#                 name=self.name,
#                 email=self.email,
#                 description=self.description,
#                 phone_number=self.phone_number,
#                 address=self.address
#             )
#         except ValidationError:
#             return _('Email не соответствует требованиям!')
#         return _('Магазин успешно редактирован')
