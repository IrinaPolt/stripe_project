import json
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from .models import Price, Item, Order, PriceInOrder, Discount
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

stripe.api_key = settings.STRIPE_SECRET_KEY

DOMAIN = 'http://51.250.84.171:8000'


class SuccessView(TemplateView):
    template_name = 'items/success.html'


class CancelView(TemplateView):
    template_name = 'items/cancel.html'


class CreateSingleCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        price = Price.objects.get(id=self.kwargs['pk'])
        discount = price.discount.stripe_coupon_id
        currency = request.POST.get('currency')
        domain = DOMAIN
        if settings.DEBUG:
            domain = 'http://127.0.0.1:8000'
        if currency == 'usd':
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': price.stripe_price_id_usd,
                        'quantity': 1,
                    },
                ],
                mode='payment',
                discounts=[{'coupon': discount}],
                automatic_tax={'enabled': True},
                shipping_address_collection={
                    'allowed_countries': ['US'],
                },
                success_url=domain + '/success/',
                cancel_url=domain + '/cancel/',
            )
        else:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': price.stripe_price_id_eur,
                        'quantity': 1,
                    },
                ],
                mode='payment',
                discounts=[{'coupon': discount}],
                automatic_tax={'enabled': True},
                shipping_address_collection={
                    'allowed_countries': ['US'],
                },
                success_url=domain + '/success/',
                cancel_url=domain + '/cancel/',
            )
        return redirect(checkout_session.url)


class CreateOrderCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        order = Order.objects.get(id=self.kwargs['pk'])
        prices = PriceInOrder.objects.filter(order=order)
        discount = Discount.objects.get(pk=1).stripe_coupon_id
        currency = request.POST.get('currency')
        line_items_list = []
        if currency == 'usd':
            for price in prices:
                line_items_list.append(
                    {
                        'price': price.price.stripe_price_id_usd,
                        'quantity': price.quantity,
                    }
                )
        else:
            for price in prices:
                line_items_list.append(
                    {
                        'price': price.price.stripe_price_id_eur,
                        'quantity': price.quantity,
                    }
                )
        domain = DOMAIN
        if settings.DEBUG:
            domain = 'http://127.0.0.1:8000'
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items_list,
            mode='payment',
            discounts=[{'coupon': discount}],
            automatic_tax={'enabled': True},
            shipping_address_collection={
                    'allowed_countries': ['US'],
                },
            success_url=domain + '/success/',
            cancel_url=domain + '/cancel/',
        )
        return redirect(checkout_session.url)


class IndexView(TemplateView):
    template_name = 'items/index.html'

    def get_context_data(self, **kwargs):
        prices = Price.objects.all()
        context = super(IndexView,
                        self).get_context_data(**kwargs)
        context.update({
            "prices": prices,
        })
        return context


class ItemPageView(TemplateView):
    template_name = 'items/item.html'

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
                currency='usd',
                customer=customer['id'],
                metadata={
                    'price_id': price.id
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
    order, created = Order.objects.get_or_create(user=request.user)
    price = get_object_or_404(Price, pk=pk)
    pricesinorder, created = PriceInOrder.objects.get_or_create(price=price, order=order)
    pricesinorder.quantity += 1
    pricesinorder.save()
    return redirect('items:cart')

def delete_from_cart(request, pk):
    order = get_object_or_404(Order, user=request.user)
    price = get_object_or_404(Price, pk=pk)
    priceinorder = get_object_or_404(PriceInOrder, price=price, order=order)
    priceinorder.quantity -= 1
    if priceinorder.quantity > 0:
        priceinorder.save()
    else:
        priceinorder.delete()
    messages.success(request, 'Cart updated!')
    return redirect('items:cart')


class ShowCart(TemplateView):
    template_name='items/cart.html'

    def get_context_data(self, **kwargs):
        order = Order.objects.get(user=self.request.user)
        prices = PriceInOrder.objects.filter(order=order)
        total_usd = 0
        total_eur = 0
        for i in prices:
            total_usd += float(i.get_cost_usd())
            total_eur += float(i.get_cost_eur())
        order.total_usd = total_usd
        order.total_eur = total_eur
        context = super(ShowCart,
                        self).get_context_data(**kwargs)
        context.update({
            'order': order,
            'prices': prices,
            'total_usd': "{:.2f}".format(total_usd),
            'total_eur': "{:.2f}".format(total_eur),
        })
        return context
