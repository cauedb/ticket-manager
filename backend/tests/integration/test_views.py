"""
Testes de integracao para a camada presentation (views).
Usam o Client do Django para simular requisicoes HTTP reais,
incluindo autenticacao e banco de dados.
"""
import json

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from tickets.infrastructure.models import Cliente, Ticket


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def usuario(db):
    return User.objects.create_user(username="tester", password="senha123")


@pytest.fixture
def cliente_autenticado(client, usuario):
    client.login(username="tester", password="senha123")
    return client


@pytest.fixture
def cliente_db(db):
    return Cliente.objects.create(
        nome="Ana Silva",
        email="ana@example.com",
        ativo=True,
    )


@pytest.fixture
def ticket_db(cliente_db):
    return Ticket.objects.create(
        titulo="Problema no login",
        descricao="Nao consigo acessar",
        status=Ticket.Status.NOVO,
        prioridade=Ticket.Prioridade.ALTA,
        cliente=cliente_db,
    )


# ---------------------------------------------------------------------------
# Protecao por autenticacao
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAutenticacao:
    """Garante que todas as rotas redirecionam usuarios nao autenticados."""

    def test_ticket_list_redireciona_sem_login(self, client, db):
        response = client.get(reverse("ticket_list"))
        assert response.status_code == 302
        assert "/login/" in response["Location"]

    def test_ticket_create_redireciona_sem_login(self, client, db):
        response = client.get(reverse("ticket_create"))
        assert response.status_code == 302
        assert "/login/" in response["Location"]

    def test_ticket_edit_redireciona_sem_login(self, client, ticket_db):
        response = client.get(reverse("ticket_edit", args=[ticket_db.id]))
        assert response.status_code == 302
        assert "/login/" in response["Location"]

    def test_ticket_detail_redireciona_sem_login(self, client, ticket_db):
        response = client.get(reverse("ticket_detail", args=[ticket_db.id]))
        assert response.status_code == 302
        assert "/login/" in response["Location"]

    def test_ticket_delete_redireciona_sem_login(self, client, ticket_db):
        response = client.post(reverse("ticket_delete", args=[ticket_db.id]))
        assert response.status_code == 302
        assert "/login/" in response["Location"]


# ---------------------------------------------------------------------------
# ticket_list
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTicketList:
    def test_retorna_200_para_usuario_autenticado(self, cliente_autenticado, db):
        response = cliente_autenticado.get(reverse("ticket_list"))
        assert response.status_code == 200

    def test_exibe_tickets_cadastrados(self, cliente_autenticado, ticket_db):
        response = cliente_autenticado.get(reverse("ticket_list"))
        assert "Problema no login" in response.content.decode()

    def test_exibe_mensagem_quando_sem_tickets(self, cliente_autenticado, db):
        response = cliente_autenticado.get(reverse("ticket_list"))
        assert "Nenhum ticket cadastrado" in response.content.decode()


# ---------------------------------------------------------------------------
# ticket_create
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTicketCreate:
    def test_get_retorna_200(self, cliente_autenticado, db):
        response = cliente_autenticado.get(reverse("ticket_create"))
        assert response.status_code == 200

    def test_get_exibe_formulario(self, cliente_autenticado, db):
        response = cliente_autenticado.get(reverse("ticket_create"))
        assert "Novo Ticket" in response.content.decode()

    def test_post_cria_ticket_e_redireciona(self, cliente_autenticado, cliente_db):
        response = cliente_autenticado.post(
            reverse("ticket_create"),
            {
                "titulo": "Ticket via teste",
                "cliente_id": str(cliente_db.id),
                "status": "Novo",
                "prioridade": "Alta",
                "descricao": "Criado pelo teste",
            },
        )
        assert response.status_code == 302
        assert Ticket.objects.filter(titulo="Ticket via teste").exists()

    def test_post_com_cliente_invalido_retorna_formulario(self, cliente_autenticado, db):
        from uuid import uuid4
        response = cliente_autenticado.post(
            reverse("ticket_create"),
            {
                "titulo": "Ticket invalido",
                "cliente_id": str(uuid4()),
                "status": "Novo",
                "prioridade": "Baixa",
            },
        )
        assert response.status_code == 200
        assert "Cliente selecionado" in response.content.decode()

    def test_post_com_titulo_vazio_retorna_formulario_com_erro(self, cliente_autenticado, cliente_db):
        response = cliente_autenticado.post(
            reverse("ticket_create"),
            {
                "titulo": "",
                "cliente_id": str(cliente_db.id),
                "status": "Novo",
                "prioridade": "Baixa",
            },
        )
        assert response.status_code == 200
        assert "título" in response.content.decode()
        assert not Ticket.objects.exists()

    def test_post_com_status_invalido_retorna_formulario_com_erro(self, cliente_autenticado, cliente_db):
        response = cliente_autenticado.post(
            reverse("ticket_create"),
            {
                "titulo": "Titulo valido",
                "cliente_id": str(cliente_db.id),
                "status": "INVALIDO",
                "prioridade": "Baixa",
            },
        )
        assert response.status_code == 200
        assert "Status" in response.content.decode()
        assert not Ticket.objects.exists()


# ---------------------------------------------------------------------------
# ticket_edit
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTicketEdit:
    def test_get_retorna_200(self, cliente_autenticado, ticket_db):
        response = cliente_autenticado.get(reverse("ticket_edit", args=[ticket_db.id]))
        assert response.status_code == 200

    def test_get_exibe_dados_do_ticket(self, cliente_autenticado, ticket_db):
        response = cliente_autenticado.get(reverse("ticket_edit", args=[ticket_db.id]))
        assert "Problema no login" in response.content.decode()

    def test_post_atualiza_ticket_e_redireciona(self, cliente_autenticado, ticket_db):
        response = cliente_autenticado.post(
            reverse("ticket_edit", args=[ticket_db.id]),
            {
                "titulo": "Titulo atualizado",
                "status": "Resolvido",
                "prioridade": "Baixa",
                "descricao": "Atualizado pelo teste",
            },
        )
        assert response.status_code == 302
        ticket_db.refresh_from_db()
        assert ticket_db.titulo == "Titulo atualizado"
        assert ticket_db.status == "Resolvido"

    def test_cliente_nao_muda_na_edicao(self, cliente_autenticado, ticket_db, cliente_db):
        cliente_original_id = ticket_db.cliente_id
        cliente_autenticado.post(
            reverse("ticket_edit", args=[ticket_db.id]),
            {
                "titulo": "Novo titulo",
                "status": "Novo",
                "prioridade": "Alta",
            },
        )
        ticket_db.refresh_from_db()
        assert ticket_db.cliente_id == cliente_original_id

    def test_post_titulo_vazio_retorna_formulario_com_erro(self, cliente_autenticado, ticket_db):
        response = cliente_autenticado.post(
            reverse("ticket_edit", args=[ticket_db.id]),
            {
                "titulo": "",
                "status": "Novo",
                "prioridade": "Baixa",
            },
        )
        assert response.status_code == 200
        assert "título" in response.content.decode()
        ticket_db.refresh_from_db()
        assert ticket_db.titulo == "Problema no login"  # nao alterado

    def test_ticket_inexistente_redireciona_com_mensagem(self, cliente_autenticado, db):
        from uuid import uuid4
        response = cliente_autenticado.get(reverse("ticket_edit", args=[uuid4()]))
        assert response.status_code == 302
        # a mensagem de erro e exibida apos o redirecionamento na listagem
        response_listagem = cliente_autenticado.get(reverse("ticket_list"))
        assert "não encontrado" in response_listagem.content.decode()


# ---------------------------------------------------------------------------
# ticket_delete
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTicketDelete:
    def test_post_deleta_ticket_e_redireciona(self, cliente_autenticado, ticket_db):
        response = cliente_autenticado.post(
            reverse("ticket_delete", args=[ticket_db.id])
        )
        assert response.status_code == 302
        assert not Ticket.objects.filter(id=ticket_db.id).exists()

    def test_ticket_inexistente_redireciona_sem_erro(self, cliente_autenticado, db):
        from uuid import uuid4
        response = cliente_autenticado.post(
            reverse("ticket_delete", args=[uuid4()])
        )
        assert response.status_code == 302


# ---------------------------------------------------------------------------
# ticket_detail (JSON)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTicketDetail:
    def test_retorna_200_com_json(self, cliente_autenticado, ticket_db):
        response = cliente_autenticado.get(
            reverse("ticket_detail", args=[ticket_db.id])
        )
        assert response.status_code == 200
        assert response["Content-Type"] == "application/json"

    def test_json_contem_campos_esperados(self, cliente_autenticado, ticket_db):
        response = cliente_autenticado.get(
            reverse("ticket_detail", args=[ticket_db.id])
        )
        data = json.loads(response.content)
        assert data["id"] == str(ticket_db.id)
        assert data["titulo"] == "Problema no login"
        assert data["cliente"] == "Ana Silva"
        assert data["status"] == "Novo"
        assert data["prioridade"] == "Alta"
        assert "criado_em" in data
        assert "atualizado_em" in data

    def test_retorna_404_para_ticket_inexistente(self, cliente_autenticado, db):
        from uuid import uuid4
        response = cliente_autenticado.get(
            reverse("ticket_detail", args=[uuid4()])
        )
        assert response.status_code == 404
