import uuid

from django.contrib.auth.hashers import make_password
from django.db import models


class Cliente(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        db_table = "clientes"

    def __str__(self) -> str:
        return self.nome


class Ticket(models.Model):
    class Status(models.TextChoices):
        NOVO = "Novo", "Novo"
        EM_ANDAMENTO = "Em Andamento", "Em Andamento"
        RESOLVIDO = "Resolvido", "Resolvido"

    class Prioridade(models.TextChoices):
        BAIXA = "Baixa", "Baixa"
        MEDIA = "Média", "Média"
        ALTA = "Alta", "Alta"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.NOVO
    )
    prioridade = models.CharField(
        max_length=10, choices=Prioridade.choices, default=Prioridade.BAIXA
    )
    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, related_name="tickets"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        db_table = "tickets"

    def __str__(self) -> str:
        return self.titulo


class Usuario(models.Model):
    class Tipo(models.TextChoices):
        ADMIN = "Admin", "Admin"
        AGENTE = "Agente", "Agente"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=255)
    tipo = models.CharField(
        max_length=10, choices=Tipo.choices, default=Tipo.AGENTE
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def set_senha(self, senha_plana: str) -> None:
        self.senha = make_password(senha_plana)

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        db_table = "usuarios"

    def __str__(self) -> str:
        return self.nome
