from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class TicketStatus(str, Enum):
    NOVO = "Novo"
    EM_ANDAMENTO = "Em Andamento"
    RESOLVIDO = "Resolvido"


class TicketPrioridade(str, Enum):
    BAIXA = "Baixa"
    MEDIA = "Média"
    ALTA = "Alta"


class TipoUsuario(str, Enum):
    ADMIN = "Admin"
    AGENTE = "Agente"


@dataclass
class ClienteEntity:
    nome: str
    email: str
    ativo: bool = True
    id: UUID = field(default_factory=uuid4)


@dataclass
class TicketEntity:
    titulo: str
    cliente_id: UUID
    status: TicketStatus = TicketStatus.NOVO
    prioridade: TicketPrioridade = TicketPrioridade.BAIXA
    descricao: str = ""
    id: UUID = field(default_factory=uuid4)
    criado_em: datetime = field(default_factory=datetime.now)
    atualizado_em: datetime = field(default_factory=datetime.now)


@dataclass
class UsuarioEntity:
    nome: str
    email: str
    tipo: TipoUsuario = TipoUsuario.AGENTE
    id: UUID = field(default_factory=uuid4)
    criado_em: datetime = field(default_factory=datetime.now)
    atualizado_em: datetime = field(default_factory=datetime.now)
