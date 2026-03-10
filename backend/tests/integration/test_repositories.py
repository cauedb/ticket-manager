"""
Testes de integracao para a camada infrastructure (repositorios).
Usam banco de dados SQLite em memoria criado automaticamente pelo pytest-django.
O decorator @pytest.mark.django_db habilita acesso ao banco em cada teste.
"""
import pytest

from tickets.infrastructure.models import Cliente, Ticket
from tickets.infrastructure.repositories import ClienteRepository, TicketRepository


# ---------------------------------------------------------------------------
# Fixtures reutilizaveis
# ---------------------------------------------------------------------------


@pytest.fixture
def cliente(db):
    return Cliente.objects.create(
        nome="Ana Silva",
        email="ana@example.com",
        ativo=True,
    )


@pytest.fixture
def cliente_inativo(db):
    return Cliente.objects.create(
        nome="Bruno Inativo",
        email="bruno@example.com",
        ativo=False,
    )


@pytest.fixture
def ticket(cliente):
    return Ticket.objects.create(
        titulo="Problema no login",
        descricao="Nao consigo acessar o sistema",
        status=Ticket.Status.NOVO,
        prioridade=Ticket.Prioridade.ALTA,
        cliente=cliente,
    )


# ---------------------------------------------------------------------------
# ClienteRepository
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestClienteRepositoryListAtivos:
    def test_retorna_apenas_clientes_ativos(self, cliente, cliente_inativo):
        repo = ClienteRepository()
        resultado = repo.list_ativos()
        ids = [c.id for c in resultado]
        assert cliente.id in ids
        assert cliente_inativo.id not in ids

    def test_retorna_lista_vazia_quando_sem_clientes_ativos(self, cliente_inativo):
        repo = ClienteRepository()
        resultado = repo.list_ativos()
        assert resultado == []

    def test_ordena_por_nome(self, db):
        Cliente.objects.create(nome="Zelia", email="zelia@example.com", ativo=True)
        Cliente.objects.create(nome="Ana", email="ana2@example.com", ativo=True)
        Cliente.objects.create(nome="Maria", email="maria@example.com", ativo=True)
        repo = ClienteRepository()
        nomes = [c.nome for c in repo.list_ativos()]
        assert nomes == sorted(nomes)


@pytest.mark.django_db
class TestClienteRepositoryGetById:
    def test_retorna_cliente_quando_existe(self, cliente):
        repo = ClienteRepository()
        resultado = repo.get_by_id(cliente.id)
        assert resultado is not None
        assert resultado.id == cliente.id
        assert resultado.nome == "Ana Silva"

    def test_retorna_none_quando_nao_existe(self, db):
        from uuid import uuid4
        repo = ClienteRepository()
        resultado = repo.get_by_id(uuid4())
        assert resultado is None


# ---------------------------------------------------------------------------
# TicketRepository
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTicketRepositoryListAll:
    def test_retorna_todos_os_tickets(self, ticket, cliente):
        Ticket.objects.create(
            titulo="Segundo ticket",
            status=Ticket.Status.EM_ANDAMENTO,
            prioridade=Ticket.Prioridade.BAIXA,
            cliente=cliente,
        )
        repo = TicketRepository()
        resultado = repo.list_all()
        assert len(resultado) == 2

    def test_retorna_lista_vazia_sem_tickets(self, db):
        repo = TicketRepository()
        assert repo.list_all() == []

    def test_inclui_dados_do_cliente(self, ticket):
        repo = TicketRepository()
        resultado = repo.list_all()
        assert resultado[0].cliente.nome == "Ana Silva"

    def test_ordena_por_criado_em_decrescente(self, cliente):
        t1 = Ticket.objects.create(
            titulo="Primeiro", status="Novo", prioridade="Baixa", cliente=cliente
        )
        t2 = Ticket.objects.create(
            titulo="Segundo", status="Novo", prioridade="Baixa", cliente=cliente
        )
        repo = TicketRepository()
        titulos = [t.titulo for t in repo.list_all()]
        assert titulos[0] == "Segundo"
        assert titulos[1] == "Primeiro"


@pytest.mark.django_db
class TestTicketRepositoryGetById:
    def test_retorna_ticket_quando_existe(self, ticket):
        repo = TicketRepository()
        resultado = repo.get_by_id(ticket.id)
        assert resultado is not None
        assert resultado.id == ticket.id
        assert resultado.titulo == "Problema no login"

    def test_retorna_none_quando_nao_existe(self, db):
        from uuid import uuid4
        repo = TicketRepository()
        resultado = repo.get_by_id(uuid4())
        assert resultado is None

    def test_inclui_dados_do_cliente(self, ticket):
        repo = TicketRepository()
        resultado = repo.get_by_id(ticket.id)
        assert resultado.cliente.nome == "Ana Silva"


@pytest.mark.django_db
class TestTicketRepositoryCreate:
    def test_cria_ticket_no_banco(self, cliente):
        repo = TicketRepository()
        ticket = repo.create(
            titulo="Novo ticket",
            cliente_id=cliente.id,
            status="Novo",
            prioridade="Alta",
            descricao="Descricao do ticket",
        )
        assert Ticket.objects.filter(id=ticket.id).exists()

    def test_ticket_criado_com_dados_corretos(self, cliente):
        repo = TicketRepository()
        ticket = repo.create(
            titulo="Novo ticket",
            cliente_id=cliente.id,
            status="Em Andamento",
            prioridade="Média",
            descricao="Descricao",
        )
        assert ticket.titulo == "Novo ticket"
        assert ticket.status == "Em Andamento"
        assert ticket.prioridade == "Média"
        assert ticket.descricao == "Descricao"
        assert ticket.cliente_id == cliente.id

    def test_descricao_vazia_por_padrao(self, cliente):
        repo = TicketRepository()
        ticket = repo.create(
            titulo="Ticket sem descricao",
            cliente_id=cliente.id,
            status="Novo",
            prioridade="Baixa",
        )
        assert ticket.descricao == ""


@pytest.mark.django_db
class TestTicketRepositoryUpdate:
    def test_atualiza_campos_do_ticket(self, ticket):
        repo = TicketRepository()
        atualizado = repo.update(
            ticket_id=ticket.id,
            titulo="Titulo atualizado",
            status="Resolvido",
            prioridade="Baixa",
            descricao="Nova descricao",
        )
        assert atualizado.titulo == "Titulo atualizado"
        assert atualizado.status == "Resolvido"
        assert atualizado.prioridade == "Baixa"
        assert atualizado.descricao == "Nova descricao"

    def test_alteracoes_persistidas_no_banco(self, ticket):
        repo = TicketRepository()
        repo.update(
            ticket_id=ticket.id,
            titulo="Titulo persistido",
            status="Resolvido",
            prioridade="Alta",
        )
        ticket.refresh_from_db()
        assert ticket.titulo == "Titulo persistido"

    def test_retorna_none_para_ticket_inexistente(self, db):
        from uuid import uuid4
        repo = TicketRepository()
        resultado = repo.update(
            ticket_id=uuid4(),
            titulo="Qualquer",
            status="Novo",
            prioridade="Baixa",
        )
        assert resultado is None

    def test_cliente_nao_e_alterado(self, ticket, cliente):
        repo = TicketRepository()
        repo.update(
            ticket_id=ticket.id,
            titulo="Titulo",
            status="Novo",
            prioridade="Baixa",
        )
        ticket.refresh_from_db()
        assert ticket.cliente_id == cliente.id


@pytest.mark.django_db
class TestTicketRepositoryDelete:
    def test_remove_ticket_do_banco(self, ticket):
        repo = TicketRepository()
        repo.delete(ticket.id)
        assert not Ticket.objects.filter(id=ticket.id).exists()

    def test_retorna_true_quando_deletado(self, ticket):
        repo = TicketRepository()
        resultado = repo.delete(ticket.id)
        assert resultado is True

    def test_retorna_false_para_ticket_inexistente(self, db):
        from uuid import uuid4
        repo = TicketRepository()
        resultado = repo.delete(uuid4())
        assert resultado is False
