from django.urls import path, include
from .views import SignUp


app_name = 'users'

urlpatterns = [
    path('signup/', SignUp.as_view(), name='signup'),
    path('', include('django.contrib.auth.urls')),
]
