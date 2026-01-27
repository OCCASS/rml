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


class OrderDetailsForm(forms.Form):
    full_name = forms.CharField(
        label='ФИО',
        widget=forms.TextInput(
            attrs={
                'class': 'checkout__input',
                'placeholder': 'ФИО',
                'autocomplete': 'name',
            }
        ),
        error_messages={'required': 'Укажите ФИО.'},
    )
    phone = forms.CharField(
        label='Номер телефона',
        widget=forms.TextInput(
            attrs={
                'class': 'checkout__input',
                'type': 'tel',
                'inputmode': 'numeric',
                'placeholder': 'Номер телефона',
                'autocomplete': 'tel',
            }
        ),
        error_messages={
            'required': 'Укажите номер телефона.',
            'invalid': 'Укажите корректный номер телефона.',
        },
    )
    address = forms.CharField(
        label='Адрес',
        widget=forms.TextInput(
            attrs={
                'class': 'checkout__input',
                'placeholder': 'Адрес',
                'autocomplete': 'street-address',
            }
        ),
        error_messages={'required': 'Укажите адрес доставки.'},
    )

    def clean_phone(self) -> str:
        value = self.cleaned_data.get('phone', '')
        digits = ''.join(ch for ch in value if ch.isdigit())
        if not digits:
            raise forms.ValidationError(self.fields['phone'].error_messages['required'])
        if digits[0] == '8':
            digits = '7' + digits[1:]
        elif digits[0] == '9':
            digits = '7' + digits
        digits = digits[:11]
        if len(digits) != 11 or digits[0] != '7':
            raise forms.ValidationError(self.fields['phone'].error_messages['invalid'])
        return f'+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}'
