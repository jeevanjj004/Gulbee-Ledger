
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('income/', include('income.urls')),
    path('debit/', include('debit.urls')),
    path('user/', include('user.urls')),
    path('expense/', include('expense.urls')),
    path('emi/', include('emi.urls')),
        path('reports/', include('reports.urls')),





]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)