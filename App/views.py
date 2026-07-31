import stripe

# Create your views here.
from django.conf import settings
from django.shortcuts import redirect, render

from .models import Payment

# Set the secret key for the stripe module
stripe.api_key = settings.STRIPE_SECRET_KEY


def home(request):
    return render(request, "home.html")


# inside views.py

import stripe
from django.conf import settings

# Set API key at module level
stripe.api_key = settings.STRIPE_SECRET_KEY


def home(request):
    return render(request, "home.html")


def create_checkout_session(request):
    if request.method != "POST":
        return redirect("home")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Coffee",
                        },
                        "unit_amount": 1000,  # Integer in cents ($10.00)
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="http://127.0.0.1:8000/success/?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://127.0.0.1:8000/cancel/",
        )

        Payment.objects.create(
            stripe_session_id=session.id,
            amount=10,
            status="PENDING",
        )

        return redirect(session.url)

    except stripe.error.StripeError as e:
        # Catch and print the exact error returned by Stripe
        print(f"Stripe Error: {e}")
        return render(request, "home.html", {"error": str(e)})


def success(request):
    session_id = request.GET.get("session_id")
    if session_id:
        Payment.objects.filter(stripe_session_id=session_id).update(status="PAID")
    return render(request, "success.html")


def cancel(request):
    return render(request, "cancel.html")
