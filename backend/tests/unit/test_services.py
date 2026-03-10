"""
Testes unitarios para a camada application (TicketService).
Os repositorios sao substituidos por mocks — nenhuma query real e executada.
"""
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from tickets.application.services import TicketService
from tickets.domain.exceptions import ClienteNaoEncontrado, DadosInvalidos, TicketNaoEncontrado


def _make_service(mock_ticket_repo=None, mock_cliente_repo=None):
    """Cria um TicketService com repositorios mockados."""
    service = TicketService.__new__(TicketService)
    service.tickets = mock_ticket_repo or MagicMock()
    service.clientes = mock_cliente_repo or MagicMock()
    return service


# ---------------------------------------------------------------------------
# Validacao de dados
# ---------------------------------------------------------------------------


class TestValidarDadosTicket:
    def test_titulo_vazio_lanca_dados_invalidos(self):
        service = _make_service()
        with pytest.raises(DadosInvalidos, match="título"):
            service._validar_dados_ticket("", "Novo", "Baixa")

    def test_titulo_apenas_espacos_lanca_dados_invalidos(self):
        service = _make_service()
        with pytest.raises(DadosInvalidos, match="título"):
            service._validar_dados_ticket("   ", "Novo", "Baixa")

    def test_status_invalido_lanca_dados_invalidos(self):
        service = _make_service()
        with pytest.raises(DadosInvalidos, match="Status"):
            service._validar_dados_ticket("Titulo", "StatusInventado", "Baixa")

    def test_prioridade_invalida_lanca_dados_invalidos(self):
        service = _make_service()
        with pytest.raises(DadosInvalidos, match="Prioridade"):
            service._validar_dados_ticket("Titulo", "Novo", "PrioridadeInventada")

    def test_dados_validos_nao_lanca_excecao(self):
        service = _make_service()
        # nao deve lancar nada
        service._validar_dados_ticket("Titulo valido", "Novo", "Alta")

    def test_todos_status_validos_sao_aceitos(self):
        service = _make_service()
        for status in ("Novo", "Em Andamento", "Resolvido"):
            service._validar_dados_ticket("Titulo", status, "Baixa")

    def test_todas_prioridades_validas_sao_aceitas(self):
        service = _make_service()
        for prioridade in ("Baixa", "Média", "Alta"):
            service._validar_dados_ticket("Titulo", "Novo", prioridade)


# ---------------------------------------------------------------------------
# Clientes
# ---------------------------------------------------------------------------


class TestListarClientesAtivos:
    def test_delega_para_repositorio(self):
        cliente_repo = MagicMock()
        cliente_repo.list_ativos.return_value = ["cliente1", "cliente2"]
        service = _make_service(mock_cliente_repo=cliente_repo)

        resultado = service.listar_clientes_ativos()

        cliente_repo.list_ativos.assert_called_once()
        assert resultado == ["cliente1", "cliente2"]


class TestObterCliente:
    def test_retorna_cliente_quando_encontrado(self):
        cliente_mock = MagicMock()
        cliente_repo = MagicMock()
        cliente_repo.get_by_id.return_value = cliente_mock
        service = _make_service(mock_cliente_repo=cliente_repo)

        resultado = service.obter_cliente(uuid4())

        assert resultado == cliente_mock

    def test_lanca_excecao_quando_nao_encontrado(self):
        cliente_repo = MagicMock()
        cliente_repo.get_by_id.return_value = None
        service = _make_service(mock_cliente_repo=cliente_repo)

        with pytest.raises(ClienteNaoEncontrado):
            service.obter_cliente(uuid4())


# ---------------------------------------------------------------------------
# Tickets
# ---------------------------------------------------------------------------


class TestListarTickets:
    def test_delega_para_repositorio(self):
        ticket_repo = MagicMock()
        ticket_repo.list_all.return_value = ["t1", "t2", "t3"]
        service = _make_service(mock_ticket_repo=ticket_repo)

        resultado = service.listar_tickets()

        ticket_repo.list_all.assert_called_once()
        assert resultado == ["t1", "t2", "t3"]


class TestObterTicket:
    def test_retorna_ticket_quando_encontrado(self):
        ticket_mock = MagicMock()
        ticket_repo = MagicMock()
        ticket_repo.get_by_id.return_value = ticket_mock
        service = _make_service(mock_ticket_repo=ticket_repo)

        resultado = service.obter_ticket(uuid4())

        assert resultado == ticket_mock

    def test_lanca_excecao_quando_nao_encontrado(self):
        ticket_repo = MagicMock()
        ticket_repo.get_by_id.return_value = None
        service = _make_service(mock_ticket_repo=ticket_repo)

        with pytest.raises(TicketNaoEncontrado):
            service.obter_ticket(uuid4())


class TestCriarTicket:
    def test_lanca_dados_invalidos_para_titulo_vazio(self):
        service = _make_service()
        with pytest.raises(DadosInvalidos):
            service.criar_ticket(titulo="", cliente_id=uuid4(), status="Novo", prioridade="Baixa")

    def test_lanca_dados_invalidos_para_status_invalido(self):
        service = _make_service()
        with pytest.raises(DadosInvalidos):
            service.criar_ticket(titulo="Titulo", cliente_id=uuid4(), status="INVALIDO", prioridade="Baixa")

    def test_nao_consulta_repositorio_se_dados_invalidos(self):
        ticket_repo = MagicMock()
        cliente_repo = MagicMock()
        service = _make_service(mock_ticket_repo=ticket_repo, mock_cliente_repo=cliente_repo)
        with pytest.raises(DadosInvalidos):
            service.criar_ticket(titulo="", cliente_id=uuid4(), status="Novo", prioridade="Baixa")
        ticket_repo.create.assert_not_called()
        cliente_repo.get_by_id.assert_not_called()

    def test_cria_ticket_quando_cliente_existe(self):
        cliente_id = uuid4()
        cliente_mock = MagicMock()
        ticket_mock = MagicMock()

        cliente_repo = MagicMock()
        cliente_repo.get_by_id.return_value = cliente_mock

        ticket_repo = MagicMock()
        ticket_repo.create.return_value = ticket_mock

        service = _make_service(mock_ticket_repo=ticket_repo, mock_cliente_repo=cliente_repo)

        resultado = service.criar_ticket(
            titulo="Problema no sistema",
            cliente_id=cliente_id,
            status="Novo",
            prioridade="Alta",
            descricao="Descricao detalhada",
        )

        ticket_repo.create.assert_called_once_with(
            titulo="Problema no sistema",
            cliente_id=cliente_id,
            status="Novo",
            prioridade="Alta",
            descricao="Descricao detalhada",
        )
        assert resultado == ticket_mock

    def test_lanca_excecao_quando_cliente_nao_existe(self):
        cliente_repo = MagicMock()
        cliente_repo.get_by_id.return_value = None
        service = _make_service(mock_cliente_repo=cliente_repo)

        with pytest.raises(ClienteNaoEncontrado):
            service.criar_ticket(
                titulo="Ticket",
                cliente_id=uuid4(),
                status="Novo",
                prioridade="Baixa",
            )

    def test_nao_cria_ticket_se_cliente_nao_existe(self):
        cliente_repo = MagicMock()
        cliente_repo.get_by_id.return_value = None
        ticket_repo = MagicMock()
        service = _make_service(mock_ticket_repo=ticket_repo, mock_cliente_repo=cliente_repo)

        with pytest.raises(ClienteNaoEncontrado):
            service.criar_ticket(
                titulo="Ticket",
                cliente_id=uuid4(),
                status="Novo",
                prioridade="Baixa",
            )

        ticket_repo.create.assert_not_called()


class TestAtualizarTicket:
    def test_lanca_dados_invalidos_para_titulo_vazio(self):
        service = _make_service()
        with pytest.raises(DadosInvalidos):
            service.atualizar_ticket(ticket_id=uuid4(), titulo="", status="Novo", prioridade="Baixa")

    def test_lanca_dados_invalidos_para_prioridade_invalida(self):
        service = _make_service()
        with pytest.raises(DadosInvalidos):
            service.atualizar_ticket(ticket_id=uuid4(), titulo="Titulo", status="Novo", prioridade="INVALIDA")

    def test_nao_consulta_repositorio_se_dados_invalidos(self):
        ticket_repo = MagicMock()
        service = _make_service(mock_ticket_repo=ticket_repo)
        with pytest.raises(DadosInvalidos):
            service.atualizar_ticket(ticket_id=uuid4(), titulo="", status="Novo", prioridade="Baixa")
        ticket_repo.get_by_id.assert_not_called()
        ticket_repo.update.assert_not_called()

    def test_atualiza_quando_ticket_existe(self):
        ticket_id = uuid4()
        ticket_mock = MagicMock()
        ticket_atualizado = MagicMock()

        ticket_repo = MagicMock()
        ticket_repo.get_by_id.return_value = ticket_mock
        ticket_repo.update.return_value = ticket_atualizado

        service = _make_service(mock_ticket_repo=ticket_repo)

        resultado = service.atualizar_ticket(
            ticket_id=ticket_id,
            titulo="Novo titulo",
            status="Em Andamento",
            prioridade="Alta",
            descricao="Nova descricao",
        )

        ticket_repo.update.assert_called_once_with(
            ticket_id=ticket_id,
            titulo="Novo titulo",
            status="Em Andamento",
            prioridade="Alta",
            descricao="Nova descricao",
        )
        assert resultado == ticket_atualizado

    def test_lanca_excecao_quando_ticket_nao_existe(self):
        ticket_repo = MagicMock()
        ticket_repo.get_by_id.return_value = None
        service = _make_service(mock_ticket_repo=ticket_repo)

        with pytest.raises(TicketNaoEncontrado):
            service.atualizar_ticket(
                ticket_id=uuid4(),
                titulo="Titulo",
                status="Novo",
                prioridade="Baixa",
            )

    def test_cliente_nao_e_alterado_na_atualizacao(self):
        """atualizar_ticket nao recebe cliente_id — cliente e imutavel."""
        ticket_repo = MagicMock()
        ticket_repo.get_by_id.return_value = MagicMock()
        service = _make_service(mock_ticket_repo=ticket_repo)

        service.atualizar_ticket(
            ticket_id=uuid4(),
            titulo="Titulo",
            status="Novo",
            prioridade="Baixa",
        )

        call_kwargs = ticket_repo.update.call_args.kwargs
        assert "cliente_id" not in call_kwargs


class TestDeletarTicket:
    def test_deleta_quando_ticket_existe(self):
        ticket_id = uuid4()
        ticket_repo = MagicMock()
        ticket_repo.get_by_id.return_value = MagicMock()
        service = _make_service(mock_ticket_repo=ticket_repo)

        service.deletar_ticket(ticket_id)

        ticket_repo.delete.assert_called_once_with(ticket_id)

    def test_lanca_excecao_quando_ticket_nao_existe(self):
        ticket_repo = MagicMock()
        ticket_repo.get_by_id.return_value = None
        service = _make_service(mock_ticket_repo=ticket_repo)

        with pytest.raises(TicketNaoEncontrado):
            service.deletar_ticket(uuid4())

    def test_nao_deleta_se_ticket_nao_existe(self):
        ticket_repo = MagicMock()
        ticket_repo.get_by_id.return_value = None
        service = _make_service(mock_ticket_repo=ticket_repo)

        with pytest.raises(TicketNaoEncontrado):
            service.deletar_ticket(uuid4())

        ticket_repo.delete.assert_not_called()
