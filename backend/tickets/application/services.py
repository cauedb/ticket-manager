from tickets.domain.exceptions import ClienteNaoEncontrado, TicketNaoEncontrado
from tickets.infrastructure.models import Cliente, Ticket
from tickets.infrastructure.repositories import ClienteRepository, TicketRepository


class TicketService:
    def __init__(self) -> None:
        self.tickets = TicketRepository()
        self.clientes = ClienteRepository()

    # --- Clientes ---

    def listar_clientes_ativos(self) -> list[Cliente]:
        """Retorna clientes ativos para popular o <select> do formulário."""
        return self.clientes.list_ativos()

    def obter_cliente(self, cliente_id) -> Cliente:
        cliente = self.clientes.get_by_id(cliente_id)
        if cliente is None:
            raise ClienteNaoEncontrado(f"Cliente {cliente_id} não encontrado.")
        return cliente

    # --- Tickets ---

    def listar_tickets(self) -> list[Ticket]:
        return self.tickets.list_all()

    def obter_ticket(self, ticket_id) -> Ticket:
        ticket = self.tickets.get_by_id(ticket_id)
        if ticket is None:
            raise TicketNaoEncontrado(f"Ticket {ticket_id} não encontrado.")
        return ticket

    def criar_ticket(self, titulo: str, cliente_id, status: str, prioridade: str, descricao: str = "") -> Ticket:
        # garante que o cliente existe antes de persistir o ticket
        self.obter_cliente(cliente_id)
        return self.tickets.create(
            titulo=titulo,
            cliente_id=cliente_id,
            status=status,
            prioridade=prioridade,
            descricao=descricao,
        )

    def atualizar_ticket(self, ticket_id, titulo: str, status: str, prioridade: str, descricao: str = "") -> Ticket:
        # garante que o ticket existe; cliente não pode ser alterado após criação
        self.obter_ticket(ticket_id)
        return self.tickets.update(
            ticket_id=ticket_id,
            titulo=titulo,
            status=status,
            prioridade=prioridade,
            descricao=descricao,
        )

    def deletar_ticket(self, ticket_id) -> None:
        # garante que o ticket existe antes de tentar deletar
        self.obter_ticket(ticket_id)
        self.tickets.delete(ticket_id)
