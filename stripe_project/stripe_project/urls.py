from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from items.views import (
    CreateCheckoutSessionView,
    SuccessView,
    CancelView,
    ItemLandingPageView,
    stripe_webhook,
    StripeIntentView,
    CustomPaymentView,
    AddToCart,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('add-to-cart/', AddToCart.as_view(), name='cart',),
    path('cancel/', CancelView.as_view(), name='cancel'),
    path('success/', SuccessView.as_view(), name='success'),
    path('create-checkout-session/<pk>/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
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