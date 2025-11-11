from django.urls import path
from .views import (
    test_payout,
    test_transfer,
    create_checkout_session,
    create_connected_account ,
    delete_connected_account,
)

urlpatterns = [
    path("payout/", test_payout, name="payout"),                    
    path("transfer/", test_transfer, name="transfer"),             
    path("checkout/", create_checkout_session, name="checkout"),   
    path("connected-account/", create_connected_account, name="connected-account"), 
    path("connected-account/delete/", delete_connected_account, name="delete-connected-account"),
]
