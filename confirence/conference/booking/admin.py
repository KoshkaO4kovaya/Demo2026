from django.contrib import admin

from .models import Profile, Room, BookingRequest, Review


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'email', 'user', 'created_at')
    search_fields = ('full_name', 'phone', 'email', 'user__username')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'room', 'event_date', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'room')
    search_fields = ('user__username', 'room__name')
    ordering = ('-created_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('booking_request', 'user', 'rating', 'created_at')
    search_fields = ('user__username', 'text')