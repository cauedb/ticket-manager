import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from tickets.application.services import TicketService
from tickets.domain.exceptions import (
    ClienteNaoEncontrado,
    DadosInvalidos,
    TicketNaoEncontrado,
)
from tickets.infrastructure.models import Ticket

logger = logging.getLogger("tickets.presentation.views")

service = TicketService()

_CONTEXTO_FORM_BASE = {
    "status_choices": Ticket.Status.choices,
    "prioridade_choices": Ticket.Prioridade.choices,
}


def _contexto_criar(**extra):
    return {**_CONTEXTO_FORM_BASE, "titulo_pagina": "Novo Ticket", **extra}


def _contexto_editar(**extra):
    return {**_CONTEXTO_FORM_BASE, "titulo_pagina": "Editar Ticket", **extra}


@login_required
@require_GET
def ticket_list(request):
    tickets = service.listar_tickets()
    return render(request, "tickets/index.html", {"tickets": tickets})


@login_required
@require_GET
def ticket_detail(request, ticket_id):
    try:
        ticket = service.obter_ticket(ticket_id)
    except TicketNaoEncontrado:
        return JsonResponse({"erro": "Ticket não encontrado."}, status=404)
    except Exception:
        logger.error("Erro inesperado ao buscar detalhe do ticket — id: %s", ticket_id, exc_info=True)
        return JsonResponse({"erro": "Erro inesperado ao buscar o ticket."}, status=500)

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


@login_required
def ticket_create(request):
    clientes = service.listar_clientes_ativos()

    if request.method == "GET":
        return render(request, "tickets/form.html", _contexto_criar(clientes=clientes))

    titulo = request.POST.get("titulo", "").strip()
    try:
        service.criar_ticket(
            titulo=titulo,
            cliente_id=request.POST.get("cliente_id"),
            status=request.POST.get("status"),
            prioridade=request.POST.get("prioridade"),
            descricao=request.POST.get("descricao", "").strip(),
        )
    except DadosInvalidos as e:
        logger.warning("Dados invalidos ao criar ticket — usuario: %s | erro: %s",
                       request.user.username, e)
        return render(request, "tickets/form.html", _contexto_criar(
            clientes=clientes,
            erro=str(e),
        ))
    except ClienteNaoEncontrado:
        logger.warning("Cliente nao encontrado ao criar ticket — usuario: %s | cliente_id: %s",
                       request.user.username, request.POST.get("cliente_id"))
        return render(request, "tickets/form.html", _contexto_criar(
            clientes=clientes,
            erro="Cliente selecionado não encontrado.",
        ))
    except Exception:
        logger.error("Erro inesperado ao criar ticket — usuario: %s | titulo: %r",
                     request.user.username, titulo, exc_info=True)
        return render(request, "tickets/form.html", _contexto_criar(
            clientes=clientes,
            erro="Erro inesperado ao criar o ticket. Tente novamente.",
        ))

    logger.info("Ticket criado com sucesso via view — usuario: %s | titulo: %r",
                request.user.username, titulo)
    return redirect("ticket_list")


@login_required
def ticket_edit(request, ticket_id):
    try:
        ticket = service.obter_ticket(ticket_id)
    except TicketNaoEncontrado:
        messages.error(request, "Ticket não encontrado.")
        return redirect("ticket_list")

    if request.method == "GET":
        return render(request, "tickets/form.html", _contexto_editar(ticket=ticket))

    titulo = request.POST.get("titulo", "").strip()
    try:
        service.atualizar_ticket(
            ticket_id=ticket_id,
            titulo=titulo,
            status=request.POST.get("status"),
            prioridade=request.POST.get("prioridade"),
            descricao=request.POST.get("descricao", "").strip(),
        )
    except DadosInvalidos as e:
        logger.warning("Dados invalidos ao editar ticket — usuario: %s | id: %s | erro: %s",
                       request.user.username, ticket_id, e)
        return render(request, "tickets/form.html", _contexto_editar(
            ticket=ticket,
            erro=str(e),
        ))
    except TicketNaoEncontrado:
        messages.error(request, "Ticket não encontrado.")
        return redirect("ticket_list")
    except Exception:
        logger.error("Erro inesperado ao editar ticket — usuario: %s | id: %s",
                     request.user.username, ticket_id, exc_info=True)
        return render(request, "tickets/form.html", _contexto_editar(
            ticket=ticket,
            erro="Erro inesperado ao salvar o ticket. Tente novamente.",
        ))

    logger.info("Ticket editado com sucesso — usuario: %s | id: %s | titulo: %r",
                request.user.username, ticket_id, titulo)
    return redirect("ticket_list")


@login_required
@require_POST
def ticket_delete(request, ticket_id):
    try:
        service.deletar_ticket(ticket_id)
        logger.info("Ticket deletado com sucesso — usuario: %s | id: %s",
                    request.user.username, ticket_id)
    except TicketNaoEncontrado:
        messages.error(request, "Ticket não encontrado.")
    except Exception:
        logger.error("Erro inesperado ao deletar ticket — usuario: %s | id: %s",
                     request.user.username, ticket_id, exc_info=True)
        messages.error(request, "Erro inesperado ao excluir o ticket.")

    return redirect("ticket_list")
