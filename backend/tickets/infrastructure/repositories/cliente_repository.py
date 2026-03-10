from tickets.infrastructure.models import Cliente


class ClienteRepository:
    def list_ativos(self) -> list[Cliente]:
        return list(Cliente.objects.filter(ativo=True).order_by("nome"))

    def get_by_id(self, cliente_id) -> Cliente | None:
        try:
            return Cliente.objects.get(id=cliente_id)
        except Cliente.DoesNotExist:
            return None
