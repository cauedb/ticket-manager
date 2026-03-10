"""
Testes unitarios para a camada domain.
Nao usam banco de dados nem Django — Python puro.
"""
from uuid import UUID

import pytest

from tickets.domain.entities import (
    ClienteEntity,
    TicketEntity,
    TicketPrioridade,
    TicketStatus,
)
from tickets.domain.exceptions import (
    ClienteNaoEncontrado,
    DadosInvalidos,
    EmailJaCadastrado,
    TicketManagerException,
    TicketNaoEncontrado,
)


class TestTicketStatus:
    def test_valores(self):
        assert TicketStatus.NOVO == "Novo"
        assert TicketStatus.EM_ANDAMENTO == "Em Andamento"
        assert TicketStatus.RESOLVIDO == "Resolvido"

    def test_e_string(self):
        assert isinstance(TicketStatus.NOVO, str)


class TestTicketPrioridade:
    def test_valores(self):
        assert TicketPrioridade.BAIXA == "Baixa"
        assert TicketPrioridade.MEDIA == "Média"
        assert TicketPrioridade.ALTA == "Alta"

    def test_e_string(self):
        assert isinstance(TicketPrioridade.ALTA, str)


class TestClienteEntity:
    def test_criacao_basica(self):
        cliente = ClienteEntity(nome="Ana Silva", email="ana@example.com")
        assert cliente.nome == "Ana Silva"
        assert cliente.email == "ana@example.com"

    def test_ativo_por_padrao(self):
        cliente = ClienteEntity(nome="Ana Silva", email="ana@example.com")
        assert cliente.ativo is True

    def test_id_uuid_gerado_automaticamente(self):
        cliente = ClienteEntity(nome="Ana Silva", email="ana@example.com")
        assert isinstance(cliente.id, UUID)

    def test_dois_clientes_tem_ids_diferentes(self):
        c1 = ClienteEntity(nome="Ana", email="ana@example.com")
        c2 = ClienteEntity(nome="Bruno", email="bruno@example.com")
        assert c1.id != c2.id

    def test_ativo_pode_ser_falso(self):
        cliente = ClienteEntity(nome="Ana", email="ana@example.com", ativo=False)
        assert cliente.ativo is False


class TestTicketEntity:
    def setup_method(self):
        self.cliente = ClienteEntity(nome="Ana Silva", email="ana@example.com")

    def test_criacao_basica(self):
        ticket = TicketEntity(titulo="Problema no login", cliente_id=self.cliente.id)
        assert ticket.titulo == "Problema no login"
        assert ticket.cliente_id == self.cliente.id

    def test_status_padrao_novo(self):
        ticket = TicketEntity(titulo="Ticket", cliente_id=self.cliente.id)
        assert ticket.status == TicketStatus.NOVO

    def test_prioridade_padrao_baixa(self):
        ticket = TicketEntity(titulo="Ticket", cliente_id=self.cliente.id)
        assert ticket.prioridade == TicketPrioridade.BAIXA

    def test_descricao_padrao_vazia(self):
        ticket = TicketEntity(titulo="Ticket", cliente_id=self.cliente.id)
        assert ticket.descricao == ""

    def test_id_uuid_gerado_automaticamente(self):
        ticket = TicketEntity(titulo="Ticket", cliente_id=self.cliente.id)
        assert isinstance(ticket.id, UUID)

    def test_dois_tickets_tem_ids_diferentes(self):
        t1 = TicketEntity(titulo="T1", cliente_id=self.cliente.id)
        t2 = TicketEntity(titulo="T2", cliente_id=self.cliente.id)
        assert t1.id != t2.id

    def test_status_personalizado(self):
        ticket = TicketEntity(
            titulo="Ticket",
            cliente_id=self.cliente.id,
            status=TicketStatus.RESOLVIDO,
        )
        assert ticket.status == TicketStatus.RESOLVIDO

    def test_prioridade_personalizada(self):
        ticket = TicketEntity(
            titulo="Ticket",
            cliente_id=self.cliente.id,
            prioridade=TicketPrioridade.ALTA,
        )
        assert ticket.prioridade == TicketPrioridade.ALTA


class TestExcecoes:
    def test_ticket_manager_exception_e_base_de_todas(self):
        assert issubclass(TicketManagerException, Exception)

    def test_cliente_nao_encontrado_herda_da_base(self):
        assert issubclass(ClienteNaoEncontrado, TicketManagerException)

    def test_ticket_nao_encontrado_herda_da_base(self):
        assert issubclass(TicketNaoEncontrado, TicketManagerException)

    def test_email_ja_cadastrado_herda_da_base(self):
        assert issubclass(EmailJaCadastrado, TicketManagerException)

    def test_dados_invalidos_herda_da_base(self):
        assert issubclass(DadosInvalidos, TicketManagerException)

    def test_todas_sao_capturadas_pela_base(self):
        """Garante que um except TicketManagerException captura qualquer erro de dominio."""
        for exc_class in (ClienteNaoEncontrado, TicketNaoEncontrado, EmailJaCadastrado, DadosInvalidos):
            with pytest.raises(TicketManagerException):
                raise exc_class("mensagem de teste")

    def test_lancamento_cliente_nao_encontrado(self):
        with pytest.raises(ClienteNaoEncontrado):
            raise ClienteNaoEncontrado("Cliente 123 nao encontrado")

    def test_lancamento_ticket_nao_encontrado(self):
        with pytest.raises(TicketNaoEncontrado):
            raise TicketNaoEncontrado("Ticket 456 nao encontrado")

    def test_lancamento_dados_invalidos(self):
        with pytest.raises(DadosInvalidos):
            raise DadosInvalidos("Titulo nao pode ser vazio")
