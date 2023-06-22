from django.urls import path
from .views import ServiceFNSPageView, ServiceFSSPPageView

app_name = 'services'

urlpatterns = [
    path("fns/", ServiceFNSPageView.as_view(), name="fns_service"),
    path("fssp/", ServiceFSSPPageView.as_view(), name="fssp_service"),
]
