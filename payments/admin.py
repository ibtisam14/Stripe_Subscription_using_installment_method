from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserConnectedAccount, Subscription

class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('username', 'email', 'connected_account_id', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ('username', 'email', 'connected_account_id')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'connected_account_id')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

class UserConnectedAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_id', 'description', 'created_at')
    search_fields = ('user__username', 'account_id', 'description')
    list_filter = ('created_at',)

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'customer_id', 'subscription_id', 'plan_type', 'status', 'start_date', 'end_date', 'created_at')
    search_fields = ('email', 'customer_id', 'subscription_id')
    list_filter = ('plan_type', 'status', 'created_at')

admin.site.register(User, UserAdmin)
admin.site.register(UserConnectedAccount, UserConnectedAccountAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
