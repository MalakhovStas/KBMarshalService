"""
URL configuration for web_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
import debug_toolbar
from .views import HomePageView, PrivacyPolicyPageView
urlpatterns = [
    path('i18n', include('django.conf.urls.i18n')),
    path('celery-progress/', include('celery_progress.urls')),
    path('admin/', admin.site.urls),
    path("", HomePageView.as_view(), name="home"),
    path("privacy_policy", PrivacyPolicyPageView.as_view(), name="privacy_policy"),
    path("users/", include("users.urls", namespace="users")),
    path("account/", include("account.urls", namespace="account")),
    path("debtors/", include("debtors.urls", namespace="debtors")),
    path("services/", include("services.urls", namespace="services")),

]

if settings.DEBUG:
    urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
    urlpatterns.extend(static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))
    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
