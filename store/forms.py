from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox


class PartnershipForm(forms.Form):
    email = forms.EmailField(
        label='',
        widget=forms.EmailInput(
            attrs={
                'class': 'partnership__input',
                'placeholder': 'Email',
            }
        ),
        error_messages={
            'required': 'Укажите email, чтобы мы могли связаться с вами.',
            'invalid': 'Укажите корректный email.',
        },
    )
    comment = forms.CharField(
        label='',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'partnership__textarea',
                'placeholder': 'Комментарий',
                'rows': 10,
            }
        ),
    )
    captcha = ReCaptchaField(
        label='',
        widget=ReCaptchaV2Checkbox(),
        error_messages={
            'required': 'Подтвердите, что вы не робот.',
            'captcha_invalid': 'Не удалось пройти проверку reCAPTCHA. Попробуйте еще раз.',
            'captcha_error': 'Не удалось пройти проверку reCAPTCHA. Попробуйте еще раз.',
        },
    )
