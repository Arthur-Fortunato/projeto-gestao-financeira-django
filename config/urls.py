from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.landing.urls')),
    path('conta/', include('apps.accounts.urls')),
    path('financas/', include('apps.finances.urls'))
]
