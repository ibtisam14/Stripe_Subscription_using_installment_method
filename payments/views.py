import stripe
import os
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
PRICE_ID = os.getenv("STRIPE_PRICE_ID")


@csrf_exempt
@require_POST
def create_checkout_session(request):
    try:
        checkout_session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": PRICE_ID, "quantity": 1}],
            subscription_data={
                "metadata": {"plan_type": "installment"},
            },
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
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
    
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
    
        return HttpResponse(status=400)

    if event["type"] == "customer.subscription.created":
        subscription = event["data"]["object"]
        print("✅ Installment subscription started:", subscription["id"])


    if event["type"] == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        print("✅ Installment payment received")

    if event["type"] == "customer.subscription.deleted":
        print("✅ Installment plan completed / subscription ended")

    return HttpResponse(status=200)
