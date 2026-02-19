# ✨ Middleware de Autenticação por API Key

## Visão Geral

Um **middleware customizado** foi adicionado para centralizar a validação de API Key em todos os endpoints. O middleware funciona automaticamente em toda a aplicação, protegendo rotas por padrão e deixando rotas públicas acessíveis sem autenticação.

## Como Funciona

### Fluxo de Requisição

```
Requisição → 🔄 Middleware AuthMiddleware
              ├─ É uma rota pública? → ✅ Deixa passar
              └─ É uma rota protegida?
                 ├─ Header X-API-Key presente? ✅ Valida chave
                 │  ├─ Válida? → ✅ Deixa passar
                 │  └─ Inválida? → ❌ Retorna 401
                 └─ Header ausente? → ❌ Retorna 422
```

## Rotas Públicas Padrão

```python
PUBLIC_ROUTES = {
    "/": "GET",                      # Root endpoint
    "/docs": "GET",                  # Swagger docs
    "/openapi.json": "GET",          # OpenAPI schema
    "/health": "GET",                # Health check
    "/users/register": "POST",       # User registration
}
```

## Rotas Protegidas

Todas as outras rotas requerem autenticação:

- ✅ **Usuários**
  - `GET /users` - Listar usuários (autenticado)
  - `GET /users/{id}` - Buscar usuário (autenticado)
  - `GET /users/email/{email}` - Buscar por email (autenticado)
  - `PUT /users/{id}` - Atualizar usuário (autenticado)
  - `DELETE /users/{id}` - Deletar usuário (autenticado)

- ✅ **Despesas**
  - `POST /expenses` - Criar despesa (autenticado)
  - `GET /expenses/{group_id}` - Listar despesas (autenticado)
  - `GET /expenses/{id}/details` - Detalhes da despesa (autenticado)
  - `PATCH /expenses/{id}` - Atualizar despesa (autenticado)
  - `DELETE /expenses/{id}` - Deletar despesa (autenticado)
  - `GET /expenses/{group_id}/analytics` - Analytics (autenticado)

## Usando o Middleware

### Na Aplicação (Automático)

O middleware está automaticamente ativo em `app/api.py`:

```python
from app.infrastructure.auth_middleware import AuthMiddleware

app.add_middleware(AuthMiddleware)  # Ativado!
```

**Não é necessário fazer nada** - o middleware funciona automaticamente para todas as requisições.

### Adicionando Rotas Públicas

Se quiser adicionar uma nova rota pública, edite `app/infrastructure/auth_middleware.py`:

```python
PUBLIC_ROUTES = {
    "/": "GET",
    "/docs": "GET",
    "/openapi.json": "GET",
    "/health": "GET",
    "/users/register": "POST",
    "/meu-novo-endpoint-publico": "GET",  # Adicione aqui
}
```

## Nos Testes

### Cliente Simples (Sem Autenticação)

```python
from fastapi.testclient import TestClient
from app.api import app

def test_public_route(mock_app_dependencies):
    client = TestClient(mock_app_dependencies)

    # Rotas públicas funcionam sem autenticação
    response = client.post("/users/register", json={...})
    assert response.status_code == 201
```

### Cliente Autenticado (Com API Key)

Use a fixture `authenticated_client`:

```python
def test_protected_route(authenticated_client):
    # O cliente já tem o header X-API-Key configurado
    response = authenticated_client.get("/users")
    assert response.status_code == 200
```

### Teste de Autenticação

```python
def test_missing_api_key(client):
    """Rota protegida sem header retorna 422"""
    response = client.get("/users")
    assert response.status_code == 422
    assert "API key required" in response.json()["detail"]

def test_invalid_api_key(client):
    """API key inválida retorna 401"""
    response = client.get(
        "/users",
        headers={"X-API-Key": "invalid"}
    )
    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"]

def test_valid_api_key(authenticated_client):
    """API key válida permite acesso"""
    response = authenticated_client.get("/users")
    assert response.status_code == 200
```

## Estrutura do Código

### Arquivo: `app/infrastructure/auth_middleware.py`

```python
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Verifica se é rota pública
        # 2. Se protegida, valida X-API-Key header
        # 3. Chama auth_service.validate_api_key()
        # 4. Retorna 401/422 ou deixa passar
```

**Responsabilidades:**

- ✅ Identificar rotas públicas vs protegidas
- ✅ Extrair header `X-API-Key`
- ✅ Validar a chave
- ✅ Retornar status correto

## Fluxo de Validação da API Key

```
Middleware detecta rota protegida
    ↓
Extrai header X-API-Key
    ↓
Chama AuthDependencies.get_auth_service()
    ↓
Chama auth_service.validate_api_key(api_key)
    ↓
API Key é comparada com get_settings().api_key
    ↓
Retorna True/False
    ↓
Se True: Deixa requisição passar ✅
Se False: Retorna 401 Unauthorized ❌
```

## Segurança

### Headers Esperados

```bash
X-API-Key: seu-secret-api-key-aqui
```

### Status HTTP Retornados

| Status  | Caso                      |
| ------- | ------------------------- |
| 200-299 | Autenticado com sucesso   |
| **401** | API Key inválida/expirada |
| **422** | Header X-API-Key ausente  |
| 500+    | Erro servidor             |

### Logs

O middleware registra:

```
[DEBUG] Public route accessed: /health
[DEBUG] API key validated for route: /users
[WARNING] Missing API key for protected route: /expenses
[WARNING] Invalid API key from 192.168.1.1
[ERROR] Authentication service error: Connection failed
```

## Próximos Passos

Sugestões para melhorias futuras:

1. **Rate Limiting** - Limitar requisições por API Key
2. **API Key Expiração** - Chaves que expiram automaticamente
3. **Múltiplas Chaves** - Diferentes chaves para diferentes usuários
4. **Scopes/Permissões** - Controle granular de acesso
5. **Audit Log** - Registrar todas as tentativas de acesso
6. **Token JWT** - Migrar para JWT com refresh tokens

## Referências

- [FastAPI Middleware](https://fastapi.tiangolo.com/advanced/middleware/)
- [Starlette BaseHTTPMiddleware](https://www.starlette.io/middleware/)
- [HTTP Status Codes](https://httpwg.org/specs/rfc9110.html#status.codes)
