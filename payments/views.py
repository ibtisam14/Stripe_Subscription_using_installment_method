import stripe
import os
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

PRICE_ID = os.getenv("STRIPE_PRICE_ID")
CONNECTED_ACCOUNT_ID = "acct_1SQlMsIVBvIGjqRr"

@csrf_exempt
def add_funds(request):
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=20000,
            currency="usd",
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
            amount=10000,  # $100
            currency="usd",
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

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception:
        return HttpResponse(status=400)

    if event["type"] == "customer.subscription.created":
        subscription = event["data"]["object"]
        print("✅ Installment subscription started:", subscription["id"])

    if event["type"] == "invoice.payment_succeeded":
        print("✅ Installment payment received (no transfer triggered)")

    if event["type"] == "customer.subscription.deleted":
        print("✅ Installment plan ended")

    return HttpResponse(status=200)
