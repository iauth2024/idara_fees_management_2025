from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),  # Required for language switcher
]

urlpatterns += i18n_patterns(
    path('', include('fees_collection.urls')),
    path('leave/', include('leave_management.urls')),
)

