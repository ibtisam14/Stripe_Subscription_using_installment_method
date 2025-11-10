import stripe
import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

PRICE_ID = os.getenv("STRIPE_PRICE_ID") 

User = get_user_model()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_connected_account(request):
    user = request.user
    if getattr(user, "connected_account_id", None):
        return Response({
            "success": False,
            "error": "User already has a connected account"
        }, status=400)

    try:
        account = stripe.Account.create(
            type="express",
            country="AE",
            email=user.email,
            capabilities={"transfers": {"requested": True}},
        )
        user.connected_account_id = account.id
        user.save()

        account_link = stripe.AccountLink.create(
            account=account.id,
            refresh_url="https://example.com/reauth",
            return_url="https://example.com/return",
            type="account_onboarding",
        )

        return Response({
            "success": True,
            "connected_account_id": account.id,
            "account_link_url": account_link.url
        })
    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=400)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def test_transfer(request):
    user = request.user
    try:
        connected_account_id = request.data.get("connected_account_id") or getattr(user, "connected_account_id", None)
        if not connected_account_id:
            return Response({"error": "Connected account ID is required"}, status=400)

        amount = request.data.get("amount")
        if not amount:
            return Response({"error": "Amount is required"}, status=400)
        amount = int(amount)

        transfer = stripe.Transfer.create(
            amount=amount,
            currency="aed",
            destination=connected_account_id,
        )
        return Response({"success": True, "transfer": transfer})
    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def test_payout(request):
    user = request.user
    try:
        connected_account_id = request.data.get("connected_account_id") or getattr(user, "connected_account_id", None)
        if not connected_account_id:
            return Response({"error": "Connected account ID is required"}, status=400)

        amount = request.data.get("amount")
        if not amount:
            return Response({"error": "Amount is required"}, status=400)
        amount = int(amount)

        payout = stripe.Payout.create(
            amount=amount,
            currency="aed",
            stripe_account=connected_account_id,
        )
        return Response({"success": True, "payout": payout})
    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=400)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    try:
        checkout_session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": PRICE_ID, "quantity": 1}],
            subscription_data={"metadata": {"plan_type": "installment"}},
            success_url="http://localhost:8000/success",
            cancel_url="http://localhost:8000/cancel",
        )
        return Response({"checkout_url": checkout_session.url})
    except Exception as e:
        return Response({"error": str(e)}, status=400)
