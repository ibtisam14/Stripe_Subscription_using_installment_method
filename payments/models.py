from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    connected_account_id = models.CharField(max_length=255, blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='payments_user_groups',
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='payments_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.'
    )

class UserConnectedAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connected_accounts')
    account_id = models.CharField(max_length=50)
    description = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.account_id}"

class Subscription(models.Model):
    email = models.EmailField()
    customer_id = models.CharField(max_length=255)        
    subscription_id = models.CharField(max_length=255)     
    plan_type = models.CharField(max_length=50, default="installment")
    status = models.CharField(max_length=50, default="active")
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    billing_cycle_count = models.IntegerField(null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.status}"
