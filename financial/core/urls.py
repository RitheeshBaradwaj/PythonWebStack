from django.urls import path
from . import views

urlpatterns = [
    path(route="financial_data/", view=views.FinancialDataAPIView.as_view()),
    path(
        route="financial_data",
        view=views.FinancialDataAPIView.as_view(),
        name="financial_data",
    ),
    path(route="statistics/", view=views.StatisticsAPIView.as_view()),
    path(route="statistics", view=views.StatisticsAPIView.as_view(), name="statistics"),
]
