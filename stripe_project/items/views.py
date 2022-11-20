import json
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.shortcuts import redirect, render
from .models import Price, Item, Order
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

stripe.api_key = settings.STRIPE_SECRET_KEY


class SuccessView(TemplateView):
    template_name = "success.html"


class CancelView(TemplateView):
    template_name = "cancel.html"


class CreateSingleCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        price = Price.objects.get(id=self.kwargs['pk'])
        domain = 'https://yourdomain.com'
        if settings.DEBUG:
            domain = 'http://127.0.0.1:8000'
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price.stripe_price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=domain + '/success/',
            cancel_url=domain + '/cancel/',
        )
        return redirect(checkout_session.url)


class CreateOrderCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        order = Order.objects.get(id=self.kwargs['pk'])
        prices = order.prices
        domain = 'https://yourdomain.com'
        if settings.DEBUG:
            domain = 'http://127.0.0.1:8000'
        for price in prices:
            checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price.stripe_price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=domain + '/success/',
            cancel_url=domain + '/cancel/',
        )
        return redirect(checkout_session.url)


class ItemLandingPageView(TemplateView):
    template_name = "landing.html"

    def get_context_data(self, **kwargs):
        prices = Price.objects.all()
        context = super(ItemLandingPageView,
                        self).get_context_data(**kwargs)
        context.update({
            "prices": prices,
        })
        return context


class ItemPageView(TemplateView):
    template_name = "item.html"

    def get_context_data(self, **kwargs):
        price = Price.objects.get(id=self.kwargs['pk'])
        context = super(ItemPageView,
                        self).get_context_data(**kwargs)
        context.update({
            "price": price,
        })
        return context


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session["customer_details"]["email"]
        payment_intent = session["payment_intent"]

        # TODO - send an email to the customer

    elif event["type"] == "payment_intent.succeeded":
        intent = event['data']['object']
        stripe_customer_id = intent["customer"]
        stripe_customer = stripe.Customer.retrieve(stripe_customer_id)
        customer_email = stripe_customer['email']
        price_id = intent["metadata"]["price_id"]
        price = Price.objects.get(id=price_id)
        item = price.item

    return HttpResponse(status=200)


class StripeIntentView(View):
    def post(self, request, *args, **kwargs):
        try:
            req_json = json.loads(request.body)
            customer = stripe.Customer.create(email=req_json['email'])
            price = Price.objects.get(id=self.kwargs["pk"])
            intent = stripe.PaymentIntent.create(
                amount=price.price,
                currency1='usd',
                currency2='eur',
                customer=customer['id'],
                metadata={
                    "price_id": price.id
                }
            )
            return JsonResponse({
                'clientSecret': intent['client_secret']
            })
        except Exception as e:
            return JsonResponse({'error': str(e)})


class CustomPaymentView(TemplateView):
    template_name = 'custom_payment.html'

    def get_context_data(self, **kwargs):
        item = Item.objects.get(name=self.name)
        prices = Price.objects.filter(item=item)
        context = super(CustomPaymentView, self).get_context_data(**kwargs)
        context.update({
            "item": item,
            "prices": prices,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
        })
        return context


def add_to_cart(request, pk):
    price = Price.objects.get(id=pk)
    order = Order.objects.get_or_create(user=request.user)
    context = {
        "price": price,
        "order": order,
        "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
    }
    return render(request, 'cart.html', context)


class ShowCart(View):
    template_name='cart.html'