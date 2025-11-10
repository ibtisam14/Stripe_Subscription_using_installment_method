from django.urls import path
from .views import (
    add_funds,
    test_payout,
    test_transfer,
    create_checkout_session,
    create_connected_account
)

urlpatterns = [
    path("funds/", add_funds, name="funds"),                        
    path("payout/", test_payout, name="payout"),                    
    path("transfer/", test_transfer, name="transfer"),             
    path("checkout/", create_checkout_session, name="checkout"),   
    path("connected-account/", create_connected_account, name="connected-account"), 
]
