class TicketManagerException(Exception):
    """Base de todas as excecoes do dominio. Permite capturar qualquer erro
    de negocio com um unico except quando necessario."""
    pass


class ClienteNaoEncontrado(TicketManagerException):
    pass


class TicketNaoEncontrado(TicketManagerException):
    pass


class EmailJaCadastrado(TicketManagerException):
    pass


class DadosInvalidos(TicketManagerException):
    """Lancada quando os dados fornecidos pelo usuario nao passam na
    validacao de negocio (ex: titulo vazio, status desconhecido)."""
    pass
