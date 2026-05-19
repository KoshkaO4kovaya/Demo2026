from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views


urlpatterns = [
    path('', views.home, name='home'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    path('profile/', views.profile_view, name='profile'),

    path('rooms/', views.room_list_view, name='room_list'),

    path('requests/create/', views.create_request_view, name='create_request'),
    path('requests/create/<int:room_id>/', views.create_request_view, name='create_request_for_room'),
    path('requests/<int:request_id>/review/', views.create_review_view, name='create_review'),

    path('reviews/', views.review_list_view, name='review_list'),

    path('admin-panel/', views.admin_panel_view, name='admin_panel'),
    path('admin-panel/rooms/create/', views.admin_room_create_view, name='admin_room_create'),
    path('admin-panel/requests/<int:request_id>/', views.admin_request_detail_view, name='admin_request_detail'),
    path('admin-panel/requests/<int:request_id>/status/', views.admin_change_status_view, name='admin_change_status'),
]
