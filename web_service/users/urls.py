from django.urls import path

from .views import \
    HomePageView, \
    RegisterView, \
    LoginUserView, \
    PasswordResetRequestView, \
    SetNewPasswordView, \
    LogoutUserView

app_name = 'users'

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path('users/register_user/', RegisterView.as_view(), name='register_user'),
    path('users/login_user/', LoginUserView.as_view(), name='login_user'),
    path('users/logout_user/', LogoutUserView.as_view(), name='logout_user'),
    path('users/password_reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('users/set_new_password/<uidb64>/<token>/', SetNewPasswordView.as_view(), name='set_new_password'),

]
