import stripe
import os
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import UserConnectedAccount
from .utils.response_helper import success_response, error_response





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
            return error_response("User already has a connected account.", status_code=400)

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

            return success_response(
                "Connected account created successfully.",
                {
                    "connected_account_id": account.id,
                    "account_link_url": account_link.url
                },
                status_code=201
            )

        except Exception as e:
            return error_response(str(e), status_code=400)


class DeleteConnectedAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            connected_account_id = request.data.get("connected_account_id")
            if not connected_account_id:
                return error_response("Please provide connected_account_id in the payload.", status_code=400)

            account = UserConnectedAccount.objects.filter(
                account_id=connected_account_id,
                user=request.user
            ).first()

            if not account:
                return error_response("Connected account not found for this user.", status_code=404)

            deleted_account = stripe.Account.delete(connected_account_id)
            account.delete()

            if getattr(request.user, "connected_account_id", None) == connected_account_id:
                request.user.connected_account_id = None
                request.user.save()

            return success_response(
                "Connected account deleted successfully.",
                {"stripe_response": deleted_account},
                status_code=200
            )

        except Exception as e:
            return error_response(str(e), status_code=400)


class TestTransferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            connected_account_id = request.data.get("connected_account_id")
            amount = request.data.get("amount")

            if not connected_account_id or not amount:
                return error_response("connected_account_id and amount are required.", status_code=400)

            account = UserConnectedAccount.objects.filter(
                account_id=connected_account_id,
                user=request.user
            ).first()

            if not account:
                return error_response("Connected account not found for this user.", status_code=404)

            transfer = stripe.Transfer.create(
                amount=int(amount),
                currency="aed",
                destination=connected_account_id
            )

            return success_response(
                "Transfer created successfully.",
                {"transfer": transfer},
                status_code=200
            )

        except Exception as e:
            return error_response(str(e), status_code=400)


class TestPayoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            connected_account_id = request.data.get("connected_account_id")
            amount = request.data.get("amount")

            if not connected_account_id or not amount:
                return error_response("connected_account_id and amount are required.", status_code=400)

            account = UserConnectedAccount.objects.filter(
                account_id=connected_account_id,
                user=request.user
            ).first()

            if not account:
                return error_response("Connected account not found for this user.", status_code=404)

            payout = stripe.Payout.create(
                amount=int(amount),
                currency="aed",
                stripe_account=connected_account_id
            )

            return success_response(
                "Payout created successfully.",
                {"payout": payout},
                status_code=200
            )

        except Exception as e:
            return error_response(str(e), status_code=400)


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

            return success_response(
                "Checkout session created successfully.",
                {"checkout_url": checkout_session.url},
                status_code=200
            )

        except Exception as e:
            return error_response(str(e), status_code=400)
