from django.urls import path
from .views import (
    CreateSingleCheckoutSessionView,
    CreateOrderCheckoutSessionView,
    SuccessView,
    CancelView,
    IndexView,
    stripe_webhook,
    StripeIntentView,
    CustomPaymentView,
    add_to_cart,
    delete_from_cart,
    ShowCart,
    ItemPageView,
)

app_name = 'items'

urlpatterns = [
    path('cart/add/<pk>/', add_to_cart, name='add-to-cart'),
    path('cart/delete/<pk>/', delete_from_cart, name='delete-from-cart'),
    path('cart/', ShowCart.as_view(), name='cart'),
    path('cancel/', CancelView.as_view(), name='cancel'),
    path('success/', SuccessView.as_view(), name='success'),
    path('buy/<pk>/', CreateSingleCheckoutSessionView.as_view(), name='buy'),
    path('get/<pk>/', ItemPageView.as_view(), name='get-item'),
    path('order/<pk>/', CreateOrderCheckoutSessionView.as_view(),
         name='buy-order'),
    path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
    path('create-payment-intent/<pk>/', StripeIntentView.as_view(),
         name='create-payment-intent'),
    path('custom-payment/', CustomPaymentView.as_view(),
         name='custom-payment'),
    path('', IndexView.as_view(), name='index'),
]
