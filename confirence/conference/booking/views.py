from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import *
from .models import Room, BookingRequest, Review


def is_admin_user(user):
    return user.is_superuser or user.username == 'Admin'


def home(request):
    return render(request, 'index.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    form = RegisterForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('profile')

        messages.error(request, 'Проверьте правильность заполнения формы.')

    return render(request, 'auth/register.html', {
        'form': form
    })


class UserLoginView(LoginView):
    template_name = 'auth/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        if is_admin_user(self.request.user):
            return '/admin-panel/'

        return '/profile/'

    def form_valid(self, form):
        messages.success(self.request, 'Вы успешно вошли в систему.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Неверный логин или пароль.')
        return super().form_invalid(form)


login_view = UserLoginView.as_view()


@login_required
def profile_view(request):
    if is_admin_user(request.user):
        return redirect('admin_panel')

    requests = (
        BookingRequest.objects
        .filter(user=request.user)
        .select_related('room')
        .order_by('-created_at')
    )

    return render(request, 'user/profile.html', {
        'requests': requests
    })


def room_list_view(request):
    rooms = Room.objects.filter(is_active=True)

    search = request.GET.get('search', '')
    capacity = request.GET.get('capacity', '')
    sort = request.GET.get('sort', 'name')

    if search:
        rooms = rooms.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    if capacity:
        rooms = rooms.filter(capacity__gte=capacity)

    if sort == 'capacity':
        rooms = rooms.order_by('capacity')
    elif sort == '-capacity':
        rooms = rooms.order_by('-capacity')
    else:
        rooms = rooms.order_by('name')

    paginator = Paginator(rooms, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'rooms/list.html', {
        'page_obj': page_obj,
        'search': search,
        'capacity': capacity,
        'sort': sort,
    })


@login_required
def create_request_view(request, room_id=None):
    if is_admin_user(request.user):
        messages.error(request, 'Администратор не создает заявки.')
        return redirect('admin_panel')

    selected_room = None

    if room_id:
        selected_room = get_object_or_404(Room, id=room_id, is_active=True)

    form = BookingRequestForm(
        request.POST or None,
        selected_room=selected_room
    )

    if request.method == 'POST':
        if form.is_valid():
            booking_request = form.save(commit=False)
            booking_request.user = request.user

            if selected_room:
                booking_request.room = selected_room

            booking_request.save()

            messages.success(request, 'Заявка успешно отправлена администратору.')
            return redirect('profile')

        messages.error(request, 'Проверьте правильность заполнения заявки.')

    return render(request, 'user/create_request.html', {
        'form': form,
        'selected_room': selected_room
    })


@login_required
def create_review_view(request, request_id):
    booking_request = get_object_or_404(
        BookingRequest,
        id=request_id,
        user=request.user
    )

    if booking_request.status != BookingRequest.STATUS_COMPLETED:
        messages.error(request, 'Отзыв можно оставить только после завершения мероприятия.')
        return redirect('profile')

    if hasattr(booking_request, 'review'):
        messages.error(request, 'Вы уже оставили отзыв по этой заявке.')
        return redirect('profile')

    form = ReviewForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.booking_request = booking_request
            review.save()

            messages.success(request, 'Спасибо! Ваш отзыв сохранен.')
            return redirect('profile')

        messages.error(request, 'Проверьте правильность заполнения отзыва.')

    return render(request, 'user/review.html', {
        'form': form,
        'booking_request': booking_request
    })


@login_required
def admin_panel_view(request):
    if not is_admin_user(request.user):
        messages.error(request, 'У вас нет доступа к панели администратора.')
        return redirect('profile')

    requests = BookingRequest.objects.select_related('user', 'room').all()

    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', '-created_at')

    if status:
        requests = requests.filter(status=status)

    if search:
        requests = requests.filter(
            Q(user__username__icontains=search) |
            Q(room__name__icontains=search)
        )

    if sort in ['created_at', '-created_at', 'event_date', '-event_date', 'status']:
        requests = requests.order_by(sort)
    else:
        requests = requests.order_by('-created_at')

    paginator = Paginator(requests, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin/dashboard.html', {
        'page_obj': page_obj,
        'status': status,
        'search': search,
        'sort': sort,
    })


@login_required
def admin_request_detail_view(request, request_id):
    if not is_admin_user(request.user):
        messages.error(request, 'У вас нет доступа к панели администратора.')
        return redirect('profile')

    booking_request = get_object_or_404(
        BookingRequest.objects.select_related('user', 'room'),
        id=request_id
    )

    form = AdminStatusForm(instance=booking_request)

    return render(request, 'admin/request_detail.html', {
        'booking_request': booking_request,
        'form': form
    })


@login_required
def admin_change_status_view(request, request_id):
    if not is_admin_user(request.user):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Нет доступа.'
            }, status=403)

        messages.error(request, 'У вас нет доступа к панели администратора.')
        return redirect('profile')

    booking_request = get_object_or_404(BookingRequest, id=request_id)

    if request.method == 'POST':
        form = AdminStatusForm(request.POST, instance=booking_request)

        if form.is_valid():
            form.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Статус изменен.',
                    'status': booking_request.status,
                    'status_display': booking_request.get_status_display(),
                })

            messages.success(request, 'Статус заявки успешно изменен.')
            return redirect('admin_panel')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'message': 'Не удалось изменить статус.'
        }, status=400)

    messages.error(request, 'Не удалось изменить статус заявки.')
    return redirect('admin_panel')

@login_required
def admin_room_create_view(request):
    if not is_admin_user(request.user):
        messages.error(request, 'У вас нет доступа к панели администратора.')
        return redirect('profile')

    form = RoomForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Зал успешно добавлен.')
            return redirect('room_list')

        messages.error(request, 'Проверьте правильность заполнения формы.')

    return render(request, 'admin/room_create.html', {
        'form': form
    })

def review_list_view(request):
    reviews = (
        Review.objects
        .select_related(
            'user',
            'user__profile',
            'booking_request',
            'booking_request__room'
        )
        .filter(booking_request__status=BookingRequest.STATUS_COMPLETED)
        .order_by('-created_at')
    )

    paginator = Paginator(reviews, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'rooms/list_reviews.html', {
        'page_obj': page_obj
    })