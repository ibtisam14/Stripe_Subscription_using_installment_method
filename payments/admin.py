from django.contrib import admin
from .models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("email", "subscription_id", "status", "plan_type", "start_date", "end_date")
    search_fields = ("email", "subscription_id", "customer_id")
