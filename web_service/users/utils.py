from users.models import User


def create_user(password, user_data):
    """ Функция принимающая данные метода POST на странице оформления заказа и создающая экземпляр модели User """

    last_name, first_name, surname = user_data['full_name'].split(' ')
    User.objects.create_user(
        email=user_data['email'],
        password=password,
        last_name=last_name,
        first_name=first_name,
        surname=surname,
        phone_number=user_data['phone_number']
    )
