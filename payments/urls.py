from django.urls import path
from .views import (
    add_funds,
    test_payout,
    test_transfer,
    create_checkout_session,
    create_connected_account
)

urlpatterns = [
    path("add-funds/", add_funds, name="add-funds"),
    path("test-payout/", test_payout, name="test-payout"),
    path("test-transfer/", test_transfer, name="test-transfer"),
    path("create-checkout-session/", create_checkout_session, name="create-checkout-session"),
    path("create-connected-account/", create_connected_account, name="create-connected-account"),
]
