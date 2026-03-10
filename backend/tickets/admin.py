from django.contrib import admin

from tickets.infrastructure.models import Cliente, Ticket


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "ativo")
    list_filter = ("ativo",)
    search_fields = ("nome", "email")
    ordering = ("nome",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("titulo", "cliente", "status", "prioridade", "criado_em")
    list_filter = ("status", "prioridade")
    search_fields = ("titulo", "cliente__nome")
    ordering = ("-criado_em",)
    readonly_fields = ("criado_em", "atualizado_em")
