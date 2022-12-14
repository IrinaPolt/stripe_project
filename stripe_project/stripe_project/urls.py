from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

static_urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,
            {'document_root': settings.STATIC_ROOT}),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls', namespace='users')),
    path('', include('items.urls', namespace='items')),
    path('', include(static_urlpatterns)),
]
