import re

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from datetime import datetime, time

from .models import BookingRequest, Profile, Review, Room


class RegisterForm(forms.Form):
    username = forms.CharField(
        label='Логин',
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Например: user123'
        })
    )

    password = forms.CharField(
        label='Пароль',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input password-field',
            'placeholder': 'Минимум 8 символов'
        })
    )

    full_name = forms.CharField(
        label='ФИО',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Иванов Иван Иванович'
        })
    )

    phone = forms.CharField(
        label='Телефон',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '8(999)123-45-67'
        })
    )

    email = forms.EmailField(
        label='Электронная почта',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'example@mail.ru'
        })
    )

    def clean_username(self):
        username = self.cleaned_data['username']

        if not re.match(r'^[A-Za-z0-9]{6,}$', username):
            raise forms.ValidationError(
                'Логин должен содержать только латинские буквы и цифры, минимум 6 символов.'
            )

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует.')

        return username

    def clean_full_name(self):
        full_name = self.cleaned_data['full_name']

        if not re.match(r'^[А-Яа-яЁё\s-]+$', full_name):
            raise forms.ValidationError(
                'ФИО должно содержать только кириллицу, пробелы и дефис.'
            )

        return full_name

    def clean_phone(self):
        phone = self.cleaned_data['phone']

        if not re.match(r'^8\(\d{3}\)\d{3}-\d{2}-\d{2}$', phone):
            raise forms.ValidationError(
                'Телефон должен быть в формате 8(XXX)XXX-XX-XX.'
            )

        return phone

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email']
        )

        Profile.objects.create(
            user=user,
            full_name=self.cleaned_data['full_name'],
            phone=self.cleaned_data['phone'],
            email=self.cleaned_data['email']
        )

        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите логин'
        })
    )

    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input password-field',
            'placeholder': 'Введите пароль'
        })
    )


class BookingRequestForm(forms.ModelForm):
    event_date = forms.DateField(
        label='Дата проведения',
        input_formats=['%Y-%m-%d', '%d.%m.%Y'],
        widget=forms.DateInput(attrs={
            'class': 'form-input pr-12 custom-date-input',
            'type': 'date',
            'autocomplete': 'off',
        })
)

    class Meta:
        model = BookingRequest
        fields = ['room', 'event_date', 'payment_method', 'comment']

        widgets = {
            'room': forms.Select(attrs={
                'class': 'form-input'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-input'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Комментарий к заявке, если требуется'
            }),
        }

        labels = {
            'room': 'Помещение',
            'payment_method': 'Способ оплаты',
            'comment': 'Комментарий',
        }

    def __init__(self, *args, **kwargs):
        selected_room = kwargs.pop('selected_room', None)
        super().__init__(*args, **kwargs)

        self.fields['room'].queryset = Room.objects.filter(is_active=True)

        if selected_room:
            self.fields['room'].initial = selected_room
            self.fields['room'].disabled = True

            
class BookingRequestForm(forms.ModelForm):
    event_date = forms.DateField(
        label='Дата проведения',
        input_formats=['%Y-%m-%d', '%d.%m.%Y'],
        widget=forms.DateInput(attrs={
            'class': 'form-input pr-12 custom-date-input',
            'type': 'date',
            'autocomplete': 'off',
        })
    )

    start_time = forms.TimeField(
        label='Время начала',
        required=True,
        widget=forms.TimeInput(attrs={
            'class': 'form-input',
            'type': 'time',
            'step': '900',
        })
    )

    class Meta:
        model = BookingRequest
        fields = ['room', 'event_date', 'payment_method', 'comment']

        widgets = {
            'room': forms.Select(attrs={
                'class': 'form-input'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-input'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Комментарий к заявке, если требуется'
            }),
        }

        labels = {
            'room': 'Помещение',
            'payment_method': 'Способ оплаты',
            'comment': 'Комментарий',
        }

    def __init__(self, *args, **kwargs):
        selected_room = kwargs.pop('selected_room', None)
        super().__init__(*args, **kwargs)

        self.fields['room'].queryset = Room.objects.filter(is_active=True)

        if selected_room:
            self.fields['room'].initial = selected_room
            self.fields['room'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        event_date = cleaned_data.get('event_date')
        start_time = cleaned_data.get('start_time')
        
        if event_date and start_time:
            from django.utils import timezone
            from datetime import datetime
            naive_datetime = datetime.combine(event_date, start_time)
            conference_start = timezone.make_aware(naive_datetime)
            self.instance.conference_start = conference_start
        
        return cleaned_data
    

class BookingRequestForm(forms.ModelForm):
    event_date = forms.DateField(
        label='Дата проведения',
        input_formats=['%Y-%m-%d', '%d.%m.%Y'],
        widget=forms.DateInput(attrs={
            'class': 'form-input pr-12 custom-date-input',
            'type': 'date',
            'autocomplete': 'off',
        })
    )

    start_time = forms.TimeField(
        label='Время начала',
        required=True,
        widget=forms.TimeInput(attrs={
            'class': 'form-input',
            'type': 'time',
            'step': '900',
        })
    )

    class Meta:
        model = BookingRequest
        fields = ['room', 'event_date', 'payment_method', 'comment']

        widgets = {
            'room': forms.Select(attrs={
                'class': 'form-input'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-input'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Комментарий к заявке, если требуется'
            }),
        }

        labels = {
            'room': 'Помещение',
            'payment_method': 'Способ оплаты',
            'comment': 'Комментарий',
        }

    def __init__(self, *args, **kwargs):
        selected_room = kwargs.pop('selected_room', None)
        super().__init__(*args, **kwargs)

        self.fields['room'].queryset = Room.objects.filter(is_active=True)

        if selected_room:
            self.fields['room'].initial = selected_room
            self.fields['room'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        event_date = cleaned_data.get('event_date')
        start_time = cleaned_data.get('start_time')
        
        if event_date and start_time:
            from django.utils import timezone
            from datetime import datetime, date
            
            naive_datetime = datetime.combine(event_date, start_time)
            conference_start = timezone.make_aware(naive_datetime)
            self.instance.conference_start = conference_start
            
            now = timezone.now()
            today = now.date()
            
            if event_date < today:
                raise forms.ValidationError('Нельзя выбрать дату в прошлом.')
            
            if event_date == today and start_time <= now.time():
                raise forms.ValidationError(f'Нельзя выбрать время в прошлом. Текущее время: {now.strftime("%H:%M")}')
        
        return cleaned_data

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']

        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Напишите отзыв о мероприятии'
            }),
            'rating': forms.Select(
                attrs={'class': 'form-input'},
                choices=[
                    (5, '5 — отлично'),
                    (4, '4 — хорошо'),
                    (3, '3 — нормально'),
                    (2, '2 — плохо'),
                    (1, '1 — очень плохо'),
                ]
            ),
        }

        labels = {
            'text': 'Отзыв',
            'rating': 'Оценка',
        }
        

class AdminStatusForm(forms.ModelForm):
    class Meta:
        model = BookingRequest
        fields = ['status']

        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-input'
            })
        }

        labels = {
            'status': 'Статус заявки'
        }


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'capacity', 'description']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Например: Конференц-зал №1'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Например: 60',
                'min': '1'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Краткое описание помещения'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 rounded border-slate-300 text-blue-600'
            }),
        }

        labels = {
            'name': 'Название зала',
            'capacity': 'Вместимость',
            'description': 'Описание',
            'is_active': 'Доступен для бронирования',
        }

