from django.contrib import admin
from django.contrib.auth.hashers import make_password

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'first_name', 'last_name', 'email')
    search_fields = ('username',)
    list_filter = ('email', 'username')
    empty_value_display = '-пусто-'

    def save_model(self, request, obj, form, change):
        obj.password = make_password(obj.password)
        obj.user = request.user
        obj.save()
