from django.urls import path
from tickets.presentation.views import HomeView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
]
