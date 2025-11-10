import stripe
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

PRICE_ID = os.getenv("STRIPE_PRICE_ID")
CONNECTED_ACCOUNT_ID = os.getenv("STRIPE_CONNECTED_ACCOUNT_ID")

@csrf_exempt
def create_connected_account(request):
    try:
        account = stripe.Account.create(
            type="express",
            country="AE",
            email="testuser@example.com",  
            capabilities={
                "transfers": {"requested": True},
            }
        )

        account_link = stripe.AccountLink.create(
            account=account.id,
            refresh_url="https://example.com/reauth",
            return_url="https://example.com/return",
            type="account_onboarding"
        )

        return JsonResponse({
            "success": True,
            "connected_account_id": account.id,
            "account_link_url": account_link.url
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


@csrf_exempt
def add_funds(request):
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=20000,
            currency="aed",
            payment_method_types=["card"],
            payment_method="pm_card_visa",
            confirm=True,
            automatic_payment_methods={"enabled": False}
        )
        return JsonResponse({"status": "funds added", "pi": payment_intent.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def test_transfer(request):
    try:
        transfer = stripe.Transfer.create(
            amount=10000, 
            currency="aed",
            destination=CONNECTED_ACCOUNT_ID
        )
        return JsonResponse({"success": True, "transfer": transfer})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


@csrf_exempt
def test_payout(request):
    try:
        payout = stripe.Payout.create(
            amount=5000,   
            currency="aed",
            stripe_account=CONNECTED_ACCOUNT_ID,
        )
        return JsonResponse({"success": True, "payout": payout})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


@csrf_exempt
@require_POST
def create_checkout_session(request):
    try:
        checkout_session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": PRICE_ID, "quantity": 1}],
            subscription_data={"metadata": {"plan_type": "installment"}},
            success_url="http://localhost:8000/success",
            cancel_url="http://localhost:8000/cancel",
        )
        return JsonResponse({"checkout_url": checkout_session.url})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
