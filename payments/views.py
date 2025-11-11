import stripe
import os
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import UserConnectedAccount

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
PRICE_ID = os.getenv("STRIPE_PRICE_ID")

User = get_user_model()

class CreateConnectedAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        description = request.data.get("description", "")

        existing_account = UserConnectedAccount.objects.filter(user=user).first()
        if existing_account:
            return Response({
                "success": False,
                "error": "User already has a connected account."
            }, status=400)

        try:
            account = stripe.Account.create(
                type="express",
                country="AE",
                email=user.email,
                capabilities={"transfers": {"requested": True}},
            )
            UserConnectedAccount.objects.create(
                user=user,
                account_id=account.id,
                description=description
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

class DeleteConnectedAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            connected_account_id = request.data.get("connected_account_id")
            if not connected_account_id:
                return Response({
                    "success": False,
                    "error": "Please provide connected_account_id in the payload."
                }, status=400)

            account = UserConnectedAccount.objects.filter(
                account_id=connected_account_id,
                user=request.user
            ).first()

            if not account:
                return Response({
                    "success": False,
                    "error": "Connected account not found for this user."
                }, status=404)

            deleted_account = stripe.Account.delete(connected_account_id)

            account.delete()

            if getattr(request.user, "connected_account_id", None) == connected_account_id:
                request.user.connected_account_id = None
                request.user.save()

            return Response({
                "success": True,
                "message": "Connected account deleted successfully.",
                "stripe_response": deleted_account
            })

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)

class TestTransferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            connected_account_id = request.data.get("connected_account_id")
            amount = request.data.get("amount")

            if not connected_account_id or not amount:
                return Response({"error": "connected_account_id and amount are required"}, status=400)

            account = UserConnectedAccount.objects.filter(
                account_id=connected_account_id,
                user=request.user
            ).first()

            if not account:
                return Response({"error": "Connected account not found for this user"}, status=404)

            transfer = stripe.Transfer.create(
                amount=int(amount),
                currency="aed",
                destination=connected_account_id
            )

            return Response({"success": True, "transfer": transfer})

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)

class TestPayoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            connected_account_id = request.data.get("connected_account_id")
            amount = request.data.get("amount")

            if not connected_account_id or not amount:
                return Response({"error": "connected_account_id and amount are required"}, status=400)

            account = UserConnectedAccount.objects.filter(
                account_id=connected_account_id,
                user=request.user
            ).first()

            if not account:
                return Response({"error": "Connected account not found for this user"}, status=404)

            payout = stripe.Payout.create(
                amount=int(amount),
                currency="aed",
                stripe_account=connected_account_id
            )

            return Response({"success": True, "payout": payout})

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)

class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
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
