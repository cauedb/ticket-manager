import logging

from tickets.domain.entities import TicketPrioridade, TicketStatus
from tickets.domain.exceptions import (
    ClienteNaoEncontrado,
    DadosInvalidos,
    TicketNaoEncontrado,
)
from tickets.infrastructure.models import Cliente, Ticket
from tickets.infrastructure.repositories import ClienteRepository, TicketRepository

logger = logging.getLogger("tickets.application.services")

_STATUS_VALIDOS = {s.value for s in TicketStatus}
_PRIORIDADES_VALIDAS = {p.value for p in TicketPrioridade}


class TicketService:
    def __init__(self) -> None:
        self.tickets = TicketRepository()
        self.clientes = ClienteRepository()

    # --- Validacao interna ---

    def _validar_dados_ticket(self, titulo: str, status: str, prioridade: str) -> None:
        """Valida campos obrigatorios antes de persistir. Lanca DadosInvalidos
        se qualquer campo estiver ausente ou fora do conjunto de valores aceitos."""
        if not titulo or not titulo.strip():
            raise DadosInvalidos("O título do ticket não pode ser vazio.")
        if status not in _STATUS_VALIDOS:
            raise DadosInvalidos(
                f"Status '{status}' inválido. Valores aceitos: {sorted(_STATUS_VALIDOS)}."
            )
        if prioridade not in _PRIORIDADES_VALIDAS:
            raise DadosInvalidos(
                f"Prioridade '{prioridade}' inválida. Valores aceitos: {sorted(_PRIORIDADES_VALIDAS)}."
            )

    # --- Clientes ---

    def listar_clientes_ativos(self) -> list[Cliente]:
        """Retorna clientes ativos para popular o <select> do formulário."""
        clientes = self.clientes.list_ativos()
        logger.debug("Listando clientes ativos — total: %d", len(clientes))
        return clientes

    def obter_cliente(self, cliente_id) -> Cliente:
        cliente = self.clientes.get_by_id(cliente_id)
        if cliente is None:
            logger.warning("Cliente nao encontrado — id: %s", cliente_id)
            raise ClienteNaoEncontrado(f"Cliente {cliente_id} não encontrado.")
        return cliente

    # --- Tickets ---

    def listar_tickets(self) -> list[Ticket]:
        tickets = self.tickets.list_all()
        logger.debug("Listando tickets — total: %d", len(tickets))
        return tickets

    def obter_ticket(self, ticket_id) -> Ticket:
        ticket = self.tickets.get_by_id(ticket_id)
        if ticket is None:
            logger.warning("Ticket nao encontrado — id: %s", ticket_id)
            raise TicketNaoEncontrado(f"Ticket {ticket_id} não encontrado.")
        return ticket

    def criar_ticket(self, titulo: str, cliente_id, status: str, prioridade: str, descricao: str = "") -> Ticket:
        self._validar_dados_ticket(titulo, status, prioridade)
        # garante que o cliente existe antes de persistir o ticket
        self.obter_cliente(cliente_id)
        ticket = self.tickets.create(
            titulo=titulo,
            cliente_id=cliente_id,
            status=status,
            prioridade=prioridade,
            descricao=descricao,
        )
        logger.info("Ticket criado — id: %s | titulo: %r | cliente: %s | status: %s | prioridade: %s",
                    ticket.id, titulo, cliente_id, status, prioridade)
        return ticket

    def atualizar_ticket(self, ticket_id, titulo: str, status: str, prioridade: str, descricao: str = "") -> Ticket:
        self._validar_dados_ticket(titulo, status, prioridade)
        # garante que o ticket existe; cliente não pode ser alterado após criação
        self.obter_ticket(ticket_id)
        ticket = self.tickets.update(
            ticket_id=ticket_id,
            titulo=titulo,
            status=status,
            prioridade=prioridade,
            descricao=descricao,
        )
        logger.info("Ticket atualizado — id: %s | titulo: %r | status: %s | prioridade: %s",
                    ticket_id, titulo, status, prioridade)
        return ticket

    def deletar_ticket(self, ticket_id) -> None:
        # garante que o ticket existe antes de tentar deletar
        self.obter_ticket(ticket_id)
        self.tickets.delete(ticket_id)
        logger.info("Ticket deletado — id: %s", ticket_id)
