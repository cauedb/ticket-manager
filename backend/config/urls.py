from django.urls import path, include

urlpatterns = [
    path("", include("tickets.presentation.urls")),
]
