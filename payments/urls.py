from django.urls import path
from .views import (
    CreateConnectedAccountView,
    DeleteConnectedAccountView,
    TestTransferView,
    TestPayoutView,
    CreateCheckoutSessionView
)

urlpatterns = [
    path("connected-account/create/", CreateConnectedAccountView.as_view()),
    path("connected-account/delete/", DeleteConnectedAccountView.as_view()),
    path("transfer/", TestTransferView.as_view()),
    path("payout/", TestPayoutView.as_view()),
    path("checkout/", CreateCheckoutSessionView.as_view()),
]
