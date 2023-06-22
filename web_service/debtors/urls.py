from django.urls import path
from .views import DebtorDetailPageView

app_name = 'debtors'

urlpatterns = [
    path("", DebtorDetailPageView.as_view(), name="debtor_detail")
]
