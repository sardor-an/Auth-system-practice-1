from django.contrib import admin
from .models import User, UserConfirmation, OneTimeTokenConfirmation, SmartToken

admin.site.register(OneTimeTokenConfirmation)
admin.site.register(SmartToken)
admin.site.register(UserConfirmation)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'phone', 'is_active', 'is_staff', 'auth_status', 'date_joined')
    list_filter = ('is_active', 'auth_status', 'is_staff', 'date_joined')
    search_fields = ('email', 'phone')
    ordering = ('-date_joined',)
    list_editable = ('is_active', 'auth_status')
    readonly_fields = ('last_login',)

   