from tickets.infrastructure.models import Ticket


class TicketRepository:
    def list_all(self) -> list[Ticket]:
        # select_related evita N+1: traz o cliente junto na mesma query
        return list(Ticket.objects.select_related("cliente").order_by("-criado_em"))

    def get_by_id(self, ticket_id) -> Ticket | None:
        try:
            return Ticket.objects.select_related("cliente").get(id=ticket_id)
        except Ticket.DoesNotExist:
            return None

    def create(self, titulo: str, cliente_id, status: str, prioridade: str, descricao: str = "") -> Ticket:
        return Ticket.objects.create(
            titulo=titulo,
            descricao=descricao,
            status=status,
            prioridade=prioridade,
            cliente_id=cliente_id,
        )

    def update(self, ticket_id, titulo: str, status: str, prioridade: str, descricao: str = "") -> Ticket | None:
        ticket = self.get_by_id(ticket_id)
        if ticket is None:
            return None
        ticket.titulo = titulo
        ticket.descricao = descricao
        ticket.status = status
        ticket.prioridade = prioridade
        ticket.save()
        return ticket

    def delete(self, ticket_id) -> bool:
        ticket = self.get_by_id(ticket_id)
        if ticket is None:
            return False
        ticket.delete()
        return True
