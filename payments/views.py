import stripe
import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import UserConnectedAccount

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
PRICE_ID = os.getenv("STRIPE_PRICE_ID")

User = get_user_model()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_connected_account(request):
    user = request.user
    description = request.data.get("description", "")

    try:
        account = stripe.Account.create(
            type="express",
            country="AE",
            email=user.email,
            capabilities={"transfers": {"requested": True}},
        )

        # Save in UserConnectedAccount table
        UserConnectedAccount.objects.create(
            user=user,
            account_id=account.id,
            description=description
        )

        # Optionally save the last connected account in user
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


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_connected_account(request):
    try:
        db_id = request.data.get("db_id")  # DB row ID
        if not db_id:
            return Response({
                "success": False,
                "error": "Please provide db_id in the payload."
            }, status=400)

        account = UserConnectedAccount.objects.filter(id=db_id, user=request.user).first()
        if not account:
            return Response({"success": False, "error": "Connected account not found"}, status=404)

        # Delete from Stripe
        deleted_account = stripe.Account.delete(account.account_id)

        # Delete from DB
        account.delete()

        # Update user's last connected account if needed
        user = request.user
        if getattr(user, "connected_account_id", None) == account.account_id:
            user.connected_account_id = None
            user.save()

        return Response({
            "success": True,
            "message": "Connected account deleted successfully.",
            "stripe_response": deleted_account
        })
    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def test_transfer(request):
    try:
        db_id = request.data.get("db_id")  # DB row ID
        amount = request.data.get("amount")
        if not db_id or not amount:
            return Response({"error": "db_id and amount are required"}, status=400)

        # Lookup Stripe account ID from DB
        account = UserConnectedAccount.objects.filter(id=db_id, user=request.user).first()
        if not account:
            return Response({"error": "Connected account not found"}, status=404)

        transfer = stripe.Transfer.create(
            amount=int(amount),
            currency="aed",
            destination=account.account_id  # Stripe account ID from DB
        )

        return Response({"success": True, "transfer": transfer})
    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def test_payout(request):
    try:
        db_id = request.data.get("db_id")  # DB row ID
        amount = request.data.get("amount")
        if not db_id or not amount:
            return Response({"error": "db_id and amount are required"}, status=400)

        # Lookup Stripe account ID from DB
        account = UserConnectedAccount.objects.filter(id=db_id, user=request.user).first()
        if not account:
            return Response({"error": "Connected account not found"}, status=404)

        payout = stripe.Payout.create(
            amount=int(amount),
            currency="aed",
            stripe_account=account.account_id  # Stripe account ID from DB
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
