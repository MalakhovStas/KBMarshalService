from django.urls import path

from .views import \
    RegisterView, \
    LoginUserView, \
    PasswordResetRequestView, \
    SetNewPasswordView, \
    LogoutUserView

app_name = 'users'

urlpatterns = [
    path('register_user/', RegisterView.as_view(), name='register_user'),
    path('login_user/', LoginUserView.as_view(), name='login_user'),
    path('logout_user/', LogoutUserView.as_view(), name='logout_user'),
    path('password_reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('set_new_password/<uidb64>/<token>/', SetNewPasswordView.as_view(), name='set_new_password'),
]
