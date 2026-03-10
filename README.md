# Ticket Manager

Sistema simples de gerenciamento de tickets de suporte, construído com Django e Django REST Framework.

---

## Funcionalidades

- **Autenticacao**: Login/logout via sistema nativo do Django; todas as rotas sao protegidas
- **Listagem de tickets**: Exibe ID (truncado), titulo e cliente em uma tabela
- **Detalhe do ticket**: Popup com todas as informacoes (titulo, cliente, status, prioridade, descricao, datas)
- **Criacao de ticket**: Formulario com selecao de cliente ativo, status e prioridade
- **Edicao de ticket**: Permite alterar titulo, status, prioridade e descricao; cliente e imutavel apos criacao
- **Exclusao de ticket**: Popup de confirmacao antes de remover o registro
- **Django Admin**: Interface administrativa para gerenciar Clientes e Tickets em `/admin/`

---

## Arquitetura

O projeto segue uma **arquitetura em camadas** inspirada na Clean Architecture, separando responsabilidades em quatro camadas:

```
tickets/
├── domain/          # Entidades puras (dataclasses) e excecoes de negocio
├── application/     # Servicos de aplicacao — orquestram os casos de uso
├── infrastructure/  # Models Django, repositorios (acesso ao banco de dados)
└── presentation/    # Views, URLs e templates HTML
```

### Camadas

| Camada | Responsabilidade |
|---|---|
| `domain` | Entidades (`TicketEntity`, `ClienteEntity`), enums (`TicketStatus`, `TicketPrioridade`) e excecoes de negocio |
| `application` | `TicketService` — orquestra operacoes usando os repositorios, aplica regras de negocio |
| `infrastructure` | Models Django ORM (`Cliente`, `Ticket`), repositorios (`ClienteRepository`, `TicketRepository`) |
| `presentation` | Views protegidas com `@login_required`, URLs e templates Django com JS vanilla para modais |

### Stack

- **Backend**: Python 3.12 + Django 5.1 + Django REST Framework 3.15
- **Banco de dados**: SQLite (arquivo local)
- **Frontend**: Django Templates + CSS e JavaScript vanilla
- **Container**: Docker + Docker Compose

---

## Instalacao e execucao

### Pre-requisitos

- [Docker](https://www.docker.com/) e Docker Compose **ou** Python 3.12+

---

### Com Docker (recomendado)

**1. Suba o container:**

```bash
docker-compose up --build -d
```

**2. Rode as migracoes:**

```bash
docker-compose exec web python manage.py makemigrations tickets
docker-compose exec web python manage.py migrate
```

**3. Crie o superusuario (necessario para acessar o sistema):**

```bash
docker-compose exec web python manage.py createsuperuser
```

**4. Acesse a aplicacao:**

- App: [http://localhost:8000](http://localhost:8000)
- Admin: [http://localhost:8000/admin](http://localhost:8000/admin)

**Para parar o container:**

```bash
docker-compose down
```

---

### Sem Docker (ambiente local)

**Pre-requisitos:** Python 3.12+ instalado.

**1. Crie e ative um ambiente virtual:**

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python -m venv .venv
source .venv/bin/activate
```

**2. Instale as dependencias:**

```bash
pip install -r backend/requirements.txt
```

**3. Rode as migracoes:**

```bash
cd backend
python manage.py makemigrations tickets
python manage.py migrate
```

**4. Crie o superusuario:**

```bash
python manage.py createsuperuser
```

**5. Inicie o servidor de desenvolvimento:**

```bash
python manage.py runserver
```

**6. Acesse a aplicacao:**

- App: [http://localhost:8000](http://localhost:8000)
- Admin: [http://localhost:8000/admin](http://localhost:8000/admin)

---

## Estrutura de pastas

```
ticket-manager/
├── Dockerfile
├── docker-compose.yml
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── tickets/
│       ├── admin.py
│       ├── domain/
│       │   ├── entities.py
│       │   └── exceptions.py
│       ├── application/
│       │   └── services.py
│       ├── infrastructure/
│       │   ├── models.py
│       │   └── repositories/
│       │       ├── cliente_repository.py
│       │       └── ticket_repository.py
│       └── presentation/
│           ├── urls.py
│           ├── views.py
│           └── templates/
│               ├── registration/
│               │   └── login.html
│               └── tickets/
│                   ├── base.html
│                   ├── index.html
│                   └── form.html
```

---

## Testes

O projeto usa **pytest** + **pytest-django**. Os testes estao organizados em duas categorias:

| Categoria | Camada testada | Banco de dados |
|---|---|---|
| `tests/unit/` | `domain` (entities) e `application` (services com mocks) | Nao usa |
| `tests/integration/` | `infrastructure` (repositories) e `presentation` (views HTTP) | SQLite em memoria |

### Executar com Docker

```bash
# Todos os testes
docker-compose exec web pytest

# Apenas unitarios (rapidos, sem banco)
docker-compose exec web pytest tests/unit/

# Apenas integracao
docker-compose exec web pytest tests/integration/

# Com output detalhado
docker-compose exec web pytest -v

# Parar no primeiro erro
docker-compose exec web pytest -x
```

> **Nota:** e necessario reconstruir a imagem antes de rodar os testes pela primeira vez,
> pois `pytest` e `pytest-django` foram adicionados ao `requirements.txt`:
> ```bash
> docker-compose up --build -d
> ```

### Executar sem Docker (ambiente local)

```bash
cd backend
pytest

# ou com output detalhado
pytest -v
```

---

## Rotas disponiveis

| Metodo | Rota | Descricao |
|---|---|---|
| GET | `/` | Listagem de tickets |
| GET/POST | `/tickets/novo/` | Criacao de ticket |
| GET/POST | `/tickets/<id>/editar/` | Edicao de ticket |
| POST | `/tickets/<id>/excluir/` | Exclusao de ticket |
| GET | `/tickets/<id>/detalhe/` | Detalhe do ticket (JSON) |
| GET/POST | `/login/` | Login |
| POST | `/logout/` | Logout |
| * | `/admin/` | Interface administrativa |
