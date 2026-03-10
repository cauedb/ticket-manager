from django.urls import path

from tickets.presentation import views

urlpatterns = [
    path("", views.ticket_list, name="ticket_list"),
    path("tickets/novo/", views.ticket_create, name="ticket_create"),
    path("tickets/<uuid:ticket_id>/editar/", views.ticket_edit, name="ticket_edit"),
    path("tickets/<uuid:ticket_id>/excluir/", views.ticket_delete, name="ticket_delete"),
    path("tickets/<uuid:ticket_id>/detalhe/", views.ticket_detail, name="ticket_detail"),
]
