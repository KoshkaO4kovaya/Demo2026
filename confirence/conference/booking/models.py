from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )

    full_name = models.CharField(
        max_length=150,
        verbose_name='ФИО',
        validators=[
            RegexValidator(
                regex=r'^[А-Яа-яЁё\s-]+$',
                message='ФИО должно содержать только кириллицу, пробелы и дефис'
            )
        ]
    )

    phone = models.CharField(
        max_length=16,
        verbose_name='Телефон',
        validators=[
            RegexValidator(
                regex=r'^8\(\d{3}\)\d{3}-\d{2}-\d{2}$',
                message='Телефон должен быть в формате 8(XXX)XXX-XX-XX'
            )
        ]
    )

    email = models.EmailField(
        verbose_name='Электронная почта'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата регистрации'
    )

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'


class Room(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название помещения'
    )

    capacity = models.PositiveIntegerField(
        verbose_name='Вместимость'
    )

    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Доступно для бронирования'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Помещение'
        verbose_name_plural = 'Помещения'
        ordering = ['name']


class BookingRequest(models.Model):
    STATUS_NEW = 'new'
    STATUS_ASSIGNED = 'assigned'
    STATUS_COMPLETED = 'completed'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_NEW, 'Новая'),
        (STATUS_ASSIGNED, 'Мероприятие назначено'),
        (STATUS_COMPLETED, 'Мероприятие завершено'),
        (STATUS_REJECTED, 'Отклонена'),
    ]

    PAYMENT_CARD = 'card'
    PAYMENT_TRANSFER = 'transfer'
    PAYMENT_QR = 'qrcode'

    PAYMENT_CHOICES = [
        (PAYMENT_CARD, 'Оплата картой МИР'),
        (PAYMENT_TRANSFER, 'Постоплата в офисе организации'),
        (PAYMENT_QR, 'Предоплата по QR-коду'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='booking_requests',
        verbose_name='Пользователь'
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name='booking_requests',
        verbose_name='Помещение'
    )

    event_date = models.DateField(
        verbose_name='Дата проведения конференции'
    )

    conference_start = models.DateTimeField(
        verbose_name='Предпочтительное время начала конференции',
        null=True,
        blank=True 
        )


    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        verbose_name='Способ оплаты'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
        verbose_name='Статус заявки'
    )

    comment = models.TextField(
        blank=True,
        verbose_name='Комментарий к заявке'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания заявки'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления заявки'
    )

    def can_leave_review(self):
        return self.status == self.STATUS_COMPLETED

    def __str__(self):
        return f'Заявка №{self.id} — {self.user.username}'

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']


class Review(models.Model):
    booking_request = models.OneToOneField(
        BookingRequest,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='Заявка'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Пользователь'
    )

    text = models.TextField(
        verbose_name='Текст отзыва'
    )

    rating = models.PositiveSmallIntegerField(
        default=5,
        verbose_name='Оценка'
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата отзыва'
    )

    def __str__(self):
        return f'Отзыв к заявке №{self.booking_request.id}'

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

