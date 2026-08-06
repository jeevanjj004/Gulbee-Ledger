from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

# NEW
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('income/', include('income.urls')),
    path('debit/', include('debit.urls')),
    path('user/', include('user.urls')),
    path('expense/', include('expense.urls')),
    path('emi/', include('emi.urls')),
    path('reports/', include('reports.urls')),

    # NEW - Service Worker
    path(
        "sw.js",
        TemplateView.as_view(
            template_name="sw.js",
            content_type="application/javascript",
        ),
        name="sw",
    ),

    path('', lambda request: redirect('user/', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)