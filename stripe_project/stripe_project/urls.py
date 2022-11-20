from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from items.views import (
    CreateSingleCheckoutSessionView,
    CreateOrderCheckoutSessionView,
    SuccessView,
    CancelView,
    ItemLandingPageView,
    stripe_webhook,
    StripeIntentView,
    CustomPaymentView,
    add_to_cart,
    ShowCart,
    ItemPageView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cart/<pk>/', add_to_cart, name='add-to-cart'),
    path('cart/', ShowCart.as_view(), name='cart'),
    path('cancel/', CancelView.as_view(), name='cancel'),
    path('success/', SuccessView.as_view(), name='success'),
    path('buy/<pk>/', CreateSingleCheckoutSessionView.as_view(), name='buy'),
    path('get/<pk>/', ItemPageView.as_view(), name='get-item'),
    path('order/<pk>/', CreateOrderCheckoutSessionView.as_view(), name='buy-order'),
    path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
    path('create-payment-intent/<pk>/', StripeIntentView.as_view(), name='create-payment-intent'),
    path('custom-payment/', CustomPaymentView.as_view(), name='custom-payment'),
    path('', ItemLandingPageView.as_view(), name='landing'),
]

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()

urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )