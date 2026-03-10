from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from tickets.application.services import TicketService
from tickets.domain.exceptions import ClienteNaoEncontrado, TicketNaoEncontrado
from tickets.infrastructure.models import Ticket

service = TicketService()


@require_GET
def ticket_list(request):
    tickets = service.listar_tickets()
    return render(request, "tickets/index.html", {"tickets": tickets})


@require_GET
def ticket_detail(request, ticket_id):
    try:
        ticket = service.obter_ticket(ticket_id)
    except TicketNaoEncontrado:
        return JsonResponse({"erro": "Ticket não encontrado."}, status=404)

    return JsonResponse({
        "id": str(ticket.id),
        "titulo": ticket.titulo,
        "descricao": ticket.descricao,
        "status": ticket.status,
        "prioridade": ticket.prioridade,
        "cliente": ticket.cliente.nome,
        "criado_em": ticket.criado_em.strftime("%d/%m/%Y %H:%M"),
        "atualizado_em": ticket.atualizado_em.strftime("%d/%m/%Y %H:%M"),
    })


def ticket_create(request):
    clientes = service.listar_clientes_ativos()

    if request.method == "GET":
        return render(request, "tickets/form.html", {
            "clientes": clientes,
            "status_choices": Ticket.Status.choices,
            "prioridade_choices": Ticket.Prioridade.choices,
            "titulo_pagina": "Novo Ticket",
        })

    try:
        service.criar_ticket(
            titulo=request.POST.get("titulo", "").strip(),
            cliente_id=request.POST.get("cliente_id"),
            status=request.POST.get("status"),
            prioridade=request.POST.get("prioridade"),
            descricao=request.POST.get("descricao", "").strip(),
        )
    except ClienteNaoEncontrado:
        return render(request, "tickets/form.html", {
            "clientes": clientes,
            "status_choices": Ticket.Status.choices,
            "prioridade_choices": Ticket.Prioridade.choices,
            "titulo_pagina": "Novo Ticket",
            "erro": "Cliente selecionado não encontrado.",
        })

    return redirect("ticket_list")


def ticket_edit(request, ticket_id):
    try:
        ticket = service.obter_ticket(ticket_id)
    except TicketNaoEncontrado:
        return redirect("ticket_list")

    if request.method == "GET":
        return render(request, "tickets/form.html", {
            "ticket": ticket,
            "status_choices": Ticket.Status.choices,
            "prioridade_choices": Ticket.Prioridade.choices,
            "titulo_pagina": "Editar Ticket",
        })

    try:
        service.atualizar_ticket(
            ticket_id=ticket_id,
            titulo=request.POST.get("titulo", "").strip(),
            status=request.POST.get("status"),
            prioridade=request.POST.get("prioridade"),
            descricao=request.POST.get("descricao", "").strip(),
        )
    except TicketNaoEncontrado as e:
        return render(request, "tickets/form.html", {
            "ticket": ticket,
            "status_choices": Ticket.Status.choices,
            "prioridade_choices": Ticket.Prioridade.choices,
            "titulo_pagina": "Editar Ticket",
            "erro": str(e),
        })

    return redirect("ticket_list")


@require_POST
def ticket_delete(request, ticket_id):
    try:
        service.deletar_ticket(ticket_id)
    except TicketNaoEncontrado:
        pass

    return redirect("ticket_list")
