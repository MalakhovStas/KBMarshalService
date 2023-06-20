from django.contrib.auth import password_validation
from django.contrib.auth.forms import SetPasswordForm, forms
from django.utils.translation import gettext_lazy as _


class CustomSetPasswordForm(SetPasswordForm):
    """Кастомная форма установки нового пароля."""

    new_password1 = forms.CharField(
        label=_('Новый пароль'),
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-input',
                'autocomplete': 'new-password',
                'placeholder': _('новый пароль'),
            },
        ),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_('Повторите новый пароль'),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-input',
                'autocomplete': 'new-password',
                'placeholder': _('повторите новый пароль'),
            },
        ),
    )
