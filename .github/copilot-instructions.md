# Copilot Instructions — Finito App Backend

## Visão Geral do Projeto

Backend em **Python + FastAPI** seguindo **Clean Architecture** e princípios **SOLID**.
Persistência em **MongoDB** via Motor (async). Autenticação dupla: **API Key** (header `X-API-Key`) + **JWT OAuth2** (Bearer).

---

## Arquitetura em Camadas

```
app/
├── api.py                          # Factory FastAPI + lifespan + middlewares
├── domain/                         # Núcleo da aplicação (sem dependências externas)
│   ├── entities/                   # Entidades Pydantic (herdam BaseEntity)
│   ├── enums/                      # Enumerações de domínio (str, Enum)
│   ├── interfaces/                 # Contratos abstratos (ABC)
│   └── dtos/                       # NamedTuples de entrada para use cases
├── use_cases/                      # Lógica de negócio (um arquivo por use case)
├── controllers/                    # Orquestração HTTP → use cases
├── routes/                         # Endpoints FastAPI (CBV com fastapi-utils)
├── models/                         # Schemas Pydantic (request/response)
├── infrastructure/                 # Implementações técnicas
│   ├── database/                   # Conexão MongoDB (Motor)
│   ├── repositories/               # Implementações concretas dos repositórios
│   ├── dependencies/               # Injeção de dependência via FastAPI Depends
│   ├── settings.py                 # Configurações (pydantic-settings + lru_cache)
│   └── logger.py                   # Logger centralizado (stdout)
└── services/                       # Serviços de infraestrutura (auth, oauth2)
```

**Regra de dependência:** `domain` → `use_cases` → `controllers` → `routes`.
A camada `domain` **nunca** importa de `infrastructure`, `controllers` ou `routes`.

---

## Convenções de Código

### 1. Entidades de Domínio (`app/domain/entities/`)

- Herdam de `BaseEntity` (que herda `pydantic.BaseModel`)
- `BaseEntity` provê: `id: Optional[str]`, `created_at`, `updated_at`, `update_timestamp()`
- Usar `Field(...)` com `description` em todos os campos
- Validadores com `@field_validator` e `mode="before"` quando necessário
- Config obrigatória: `populate_by_name = True`
- Sempre incluir `json_schema_extra` com exemplo

```python
from app.domain.entities.base_entity import BaseEntity
from pydantic import Field, field_validator

class MyEntity(BaseEntity):
    name: str = Field(..., min_length=1, max_length=200, description="...")

    class Config:
        populate_by_name = True
        json_schema_extra = {"example": {"id": "...", "name": "..."}}
```

### 2. Enumerações (`app/domain/enums/`)

- Herdar de `(str, Enum)` para serialização automática
- Sempre implementar `__str__` retornando `self.value`

```python
from enum import Enum

class MyEnum(str, Enum):
    OPTION_A = "option_a"

    def __str__(self) -> str:
        return self.value
```

### 3. Interfaces / Contratos (`app/domain/interfaces/`)

- Herdar de `ABC` + `Generic[T]` quando aplicável
- Todos os métodos são `@abstractmethod`
- Repositórios herdam de `BaseRepository[T]` e adicionam métodos específicos
- Use cases implementam `IUseCase[InputType, OutputType]`

```python
# Repositório específico
class IMyRepository(BaseRepository[MyEntity]):
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[MyEntity]: ...

# Use case
class MyUseCase(IUseCase[MyInput, MyOutput]):
    async def execute(self, input_data: MyInput) -> MyOutput: ...
```

### 4. DTOs (`app/domain/dtos/`)

- Usar `NamedTuple` (imutável, tipado, sem dependência externa)
- Um arquivo por domínio (`user_dtos.py`, `expense_dtos.py`)
- Nomenclatura: `<Ação><Domínio>Input` (ex: `GetAllUsersInput`, `UpdateExpenseInput`)

```python
from typing import NamedTuple
from app.models.user_schema import UserUpdate

class UpdateUserInput(NamedTuple):
    user_id: str
    user_data: UserUpdate
```

### 5. Use Cases (`app/use_cases/<domínio>/`)

- **Um arquivo por use case** (`create_user.py`, `delete_user.py`, etc.)
- Recebem o repositório via construtor (injeção de dependência)
- Único método público: `async def execute(...)`
- Logging obrigatório: `logger.info` no início, `logger.warning` para not-found, `logger.error` no except
- Levantar `ValueError` para erros de negócio, re-levantar exceções de infraestrutura

```python
from app.domain.interfaces.use_case import IUseCase
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)

class CreateXUseCase(IUseCase[XCreate, XResponse]):
    def __init__(self, repository: IXRepository):
        self.repository = repository

    async def execute(self, input_data: XCreate) -> XResponse:
        try:
            logger.info(f"Creating X: {input_data.name}")
            # lógica de negócio aqui
            result = await self.repository.create(entity)
            logger.info(f"X created with ID: {result.id}")
            return XResponse(**result.model_dump())
        except ValueError as ve:
            logger.warning(f"Validation error: {ve}")
            raise
        except Exception as e:
            logger.error(f"Error creating X: {e}")
            raise
```

### 6. Controllers (`app/controllers/`)

- Camada **fina** de orquestração — sem lógica de negócio
- Recebem repositório no `__init__` e instanciam os use cases
- Métodos delegam diretamente para o use case correspondente

```python
class MyController:
    def __init__(self, repository: IMyRepository):
        self.create_use_case = CreateMyUseCase(repository)
        self.get_use_case = GetMyUseCase(repository)

    async def create(self, data: MyCreate) -> MyResponse:
        return await self.create_use_case.execute(data)
```

### 7. Rotas (`app/routes/`)

- Usar **Class-Based Views** com `@cbv(router)` do `fastapi-utils`
- Injeção do controller e autenticações via atributos de classe com `Depends`/`Security`
- Tratar `ValueError` → HTTP 422, exceções genéricas → HTTP 400/500
- Verificar recurso não encontrado (`None`) → HTTP 404

```python
from fastapi import APIRouter, Depends, Security, HTTPException, status
from fastapi_utils.cbv import cbv

router = APIRouter(tags=["my_resource"], prefix="/my-resources")

@cbv(router)
class MyViews:
    controller: MyController = Depends(MyDependencies.get_controller)
    current_user: TokenData = Security(verify_oauth2_token)
    api_key: str = Security(verify_api_key)

    @router.post("/", response_model=MyResponse, status_code=status.HTTP_201_CREATED)
    async def create(self, data: MyCreate) -> MyResponse:
        try:
            return await self.controller.create(data)
        except ValueError as ve:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
```

### 8. Schemas Pydantic (`app/models/`)

- Três classes por domínio: `XCreate`, `XUpdate` (campos opcionais), `XResponse`
- `XUpdate` usa todos os campos como `Optional` com default `None`
- `XResponse` inclui `id`, timestamps e `from_attributes = True`
- Sempre incluir `json_schema_extra` com exemplo

```python
class MyCreate(BaseModel):
    name: str = Field(..., min_length=1, description="...")

class MyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, description="...")

class MyResponse(BaseModel):
    id: str
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
```

### 9. Repositórios (`app/infrastructure/repositories/`)

- Nome da classe: `Mongo<Domínio>Repository`
- Implementar `_entity_to_document()` e `_document_to_entity()`
- Usar `ObjectId` do `bson` para `_id`
- Soft delete: setar `is_deleted = True` (nunca `delete_one`)
- Filtrar `is_deleted: False` em todas as queries de leitura

```python
class MongoMyRepository(IMyRepository):
    def __init__(self):
        self.collection_name = "my_collection"

    def _get_collection(self):
        return Database.get_db()[self.collection_name]

    def _entity_to_document(self, entity: MyEntity) -> dict:
        doc = entity.model_dump(exclude={"id"})
        doc["_id"] = ObjectId(entity.id) if entity.id else ObjectId()
        return doc

    def _document_to_entity(self, doc: dict) -> MyEntity:
        if doc:
            doc["id"] = str(doc.pop("_id"))
            return MyEntity(**doc)
        return None
```

### 10. Injeção de Dependência (`app/infrastructure/dependencies/`)

- Classe estática `<Domínio>Dependencies` com métodos `get_repository()` e `get_controller()`
- `get_controller` usa `Depends(get_repository.__func__)` para encadear

```python
class MyDependencies:
    @staticmethod
    def get_repository() -> IMyRepository:
        return MongoMyRepository()

    @staticmethod
    def get_controller(
        repository: IMyRepository = Depends(get_repository.__func__),
    ) -> MyController:
        return MyController(repository)
```

### 11. Configurações (`app/infrastructure/settings.py`)

- `pydantic_settings.BaseSettings` + `@lru_cache()` em `get_settings()`
- Variáveis de ambiente em `.env` (caso-insensitivo)
- Nunca acessar `os.environ` diretamente — sempre usar `get_settings()`

### 12. Logger (`app/infrastructure/logger.py`)

- Sempre usar `logger = get_logger(__name__)` no topo do arquivo
- Não usar `print()` em nenhum módulo da aplicação
- Níveis: `info` (fluxo normal), `warning` (not-found, validação), `error` (exceção)

---

## Autenticação

O projeto usa **dupla autenticação**:

1. **API Key** — header `X-API-Key` obrigatório em todas as rotas
2. **JWT Bearer** — obrigatório em rotas privadas (`/users/` exceto `/register`, `/expenses/`)

Rotas públicas (somente API Key): `POST /users/register`, `POST /auth/login`, `POST /auth/refresh`

```python
# Rota privada (ambas as autenticações)
current_user: TokenData = Security(verify_oauth2_token)
api_key: str = Security(verify_api_key)

# Rota pública (somente API Key)
api_key: str = Security(verify_api_key)
```

---

## Testes Unitários

### Estrutura dos Testes

```
tests/
├── conftest.py                     # Fixtures globais (entities, schemas, mocks)
├── app/
│   ├── domain/
│   │   ├── entities/               # Testes das entidades
│   │   ├── dtos/                   # Testes dos DTOs
│   │   └── interfaces/             # Testes das interfaces
│   ├── use_cases/                  # Testes dos use cases (por domínio)
│   ├── controllers/                # Testes dos controllers
│   ├── routes/                     # Testes de integração HTTP
│   └── infrastructure/             # Testes dos repositórios e settings
```

### Convenções de Teste

- Cobertura mínima: **80%** (configurar com `pytest-cov`)
- Framework: `pytest` + `pytest-asyncio` + `pytest-mock`
- Padrão AAA: **Arrange / Act / Assert** com comentários
- Classes de teste: `Test<NomeDoArquivo>` → `Test<Cenário>` (ex: `TestCreateUserUseCase`)
- Nomenclatura: `test_<ação>_<cenário>` (ex: `test_create_user_email_already_exists`)
- Usar `AsyncMock(spec=IRepository)` para mockar repositórios
- **Nunca** conectar ao banco real nos testes unitários

```python
class TestCreateXUseCase:
    @pytest.mark.asyncio
    async def test_create_success(self, mock_repo, sample_entity):
        # Arrange
        mock_repo.find_by_name.return_value = None
        mock_repo.create.return_value = sample_entity
        use_case = CreateXUseCase(mock_repo)

        # Act
        result = await use_case.execute(sample_input)

        # Assert
        assert result.name == sample_entity.name
        mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_duplicate_raises_value_error(self, mock_repo, sample_entity):
        # Arrange
        mock_repo.find_by_name.return_value = sample_entity  # já existe
        use_case = CreateXUseCase(mock_repo)

        # Act & Assert
        with pytest.raises(ValueError, match="already exists"):
            await use_case.execute(sample_input)
        mock_repo.create.assert_not_called()
```

### Fixtures Obrigatórias em `conftest.py`

Para cada domínio novo, adicionar ao `conftest.py`:

```python
@pytest.fixture
def sample_x_data() -> dict: ...

@pytest.fixture
def sample_x_entity(sample_x_data) -> XEntity: ...

@pytest.fixture
def sample_x_create() -> XCreate: ...

@pytest.fixture
def sample_x_response(sample_x_data) -> XResponse: ...

@pytest.fixture
def mock_x_repository() -> AsyncMock:
    return AsyncMock(spec=IXRepository)
```

### Configuração do pytest (`pytest.ini`)

```ini
[pytest]
asyncio_mode = auto
pythonpath = .
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --verbose --strict-markers --tb=short
```

### Executar testes com cobertura

```bash
pytest --cov=app --cov-report=html --cov-fail-under=80
```

---

## Padrões de Nomenclatura

| Tipo                | Convenção                   | Exemplo                       |
| ------------------- | --------------------------- | ----------------------------- |
| Entidade            | `PascalCase` sem sufixo     | `User`, `Expense`             |
| Interface           | `I` + PascalCase            | `IUserRepository`, `IUseCase` |
| Implementação Mongo | `Mongo` + PascalCase        | `MongoUserRepository`         |
| Use Case            | PascalCase + `UseCase`      | `CreateUserUseCase`           |
| Controller          | PascalCase + `Controller`   | `UserController`              |
| Schema Create       | PascalCase + `Create`       | `UserCreate`                  |
| Schema Update       | PascalCase + `Update`       | `UserUpdate`                  |
| Schema Response     | PascalCase + `Response`     | `UserResponse`                |
| DTO Input           | PascalCase + `Input`        | `GetAllUsersInput`            |
| Dependencies        | PascalCase + `Dependencies` | `UserDependencies`            |
| Arquivo             | `snake_case.py`             | `create_user.py`              |
| Coleção MongoDB     | `snake_case` plural         | `users`, `expenses`           |

---

## Segurança

- Senhas **sempre** com `bcrypt` (rounds=12) — nunca armazenar plain text
- JWT com `HS256`, expiração configurável via settings
- API Key comparada via `secrets.compare_digest` ou comparação de string com settings
- Nunca logar senhas, tokens ou API keys completos (truncar se necessário)
- Validar inputs na borda (schemas Pydantic) antes de chegar nos use cases
- Soft delete: nunca remover dados fisicamente do banco

---

## Stack e Dependências

| Pacote                                      | Uso                               |
| ------------------------------------------- | --------------------------------- |
| `fastapi`                                   | Framework web                     |
| `uvicorn[standard]`                         | Servidor ASGI                     |
| `pydantic` v2                               | Validação e serialização          |
| `pydantic-settings`                         | Configurações via env             |
| `motor`                                     | MongoDB async                     |
| `pymongo` / `bson`                          | ObjectId e utilitários Mongo      |
| `fastapi-utils`                             | CBV (`@cbv`)                      |
| `bcrypt`                                    | Hash de senhas                    |
| `PyJWT`                                     | Geração/verificação de tokens JWT |
| `pytest` + `pytest-asyncio` + `pytest-mock` | Testes                            |
| `pytest-cov`                                | Cobertura de testes               |
| `httpx`                                     | Client HTTP nos testes de rota    |

---

## Checklist para Novo Domínio

Ao criar um novo recurso (ex: `Product`), seguir esta ordem:

1. [ ] `app/domain/enums/product_*_enum.py` (se necessário)
2. [ ] `app/domain/entities/product_entity.py` (herda `BaseEntity`)
3. [ ] `app/domain/interfaces/product_repository_interface.py` (herda `BaseRepository[Product]`)
4. [ ] `app/domain/dtos/product_dtos.py` (NamedTuples de input)
5. [ ] `app/models/product_schema.py` (`ProductCreate`, `ProductUpdate`, `ProductResponse`)
6. [ ] `app/use_cases/product/create_product.py` ... (um arquivo por use case)
7. [ ] `app/infrastructure/repositories/product_repository.py` (`MongoProductRepository`)
8. [ ] `app/controllers/product_controller.py`
9. [ ] `app/infrastructure/dependencies/product_dependencies.py`
10. [ ] `app/routes/product_routes.py` (CBV)
11. [ ] Registrar router em `app/api.py`
12. [ ] `tests/app/domain/entities/test_product_entity.py`
13. [ ] `tests/app/use_cases/product/test_*.py` (um por use case)
14. [ ] `tests/app/controllers/test_product_controller.py`
15. [ ] `tests/app/routes/test_product_routes.py`
16. [ ] Adicionar fixtures em `tests/conftest.py`
