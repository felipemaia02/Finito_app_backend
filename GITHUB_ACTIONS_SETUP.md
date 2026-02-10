# GitHub Actions Setup Guide

Este guia ajuda você a configurar as GitHub Actions para CI/CD automático do Finito App Backend.

## 📦 Workflows Criados

### 1. **Unit Tests** (`.github/workflows/tests.yml`)

Executa automaticamente os testes unitários em:

- 🔹 Todos os push nas branches `master` e `develop`
- 🔹 Todos os pull requests para `master` e `develop`

**O que faz:**

- ✅ Instala dependências Python
- ✅ Executa todos os testes com pytest
- ✅ Gera relatório de cobertura
- ✅ Upload para Codecov (opcional)
- ✅ Salva relatório HTML de cobertura

### 2. **Deploy to Railway** (`.github/workflows/deploy.yml`)

Faz deploy automático após aprovação dos testes:

- 🚀 Dispara após push na branch `master`
- 🚀 OU após sucesso do workflow de testes
- 🚀 Deploy automático no Railway

**O que faz:**

- 🔗 Conecta ao Railway
- 🔗 Faz deploy da aplicação
- 🔗 Notifica status do deploy

---

## 🔧 Configuração Passo a Passo

### Pré-requisitos

1. Repositório no GitHub
2. Conta no Railway
3. Token de acesso Railway

### Passo 1: Configurar Secrets do GitHub

Vá para seu repositório GitHub > Settings > Secrets and variables > Actions

Clique em **"New repository secret"** e adicione:

#### Para Deploy no Railway:

```
RAILWAY_TOKEN
```

- Valor: Seu token do Railway (obtém em https://railway.app/account/tokens)

```
RAILWAY_PROJECT_ID
```

- Valor: ID do seu projeto no Railway

```
RAILWAY_ENVIRONMENT_ID
```

- Valor: ID do seu ambiente no Railway

#### Como obter essas informações do Railway:

1. Faça login em https://railway.app
2. Vá para seu projeto
3. Clique em "Settings" → "General"
4. Copie o Project ID e Environment ID
5. Vá para "Account" → "Tokens" para gerar um novo token

### Passo 2: Fazer Push dos Arquivos

```bash
git add .github/
git commit -m "Add GitHub Actions workflows for CI/CD"
git push origin master
```

### Passo 3: Verificar Execução

1. Vá para sua página do repositório no GitHub
2. Clique na aba **"Actions"**
3. Você verá seus workflows sendo executados

---

## 📊 Entendendo os Workflows

### Workflow de Testes

O workflow executa a seguir:

```
1. Fazer checkout do código
   ↓
2. Configurar Python 3.14
   ↓
3. Instalar dependências (pip install -r requirements.txt)
   ↓
4. Rodar testes (pytest tests/app -v)
   ↓
5. Gerar relatório de cobertura (--cov=app)
   ↓
6. Upload para Codecov (opcional)
   ↓
7. Salvar artefatos (relatório HTML)
```

### Resultado dos Testes

Você verá:

- ✅ **Status verde** = Testes passaram
- ❌ **Status vermelho** = Testes falharam
- 📊 **Cobertura** = Percentual de código testado

---

## 🚀 Workflow de Deploy

O Deploy é **condicional**:

```
Se (Push em master) OU (Testes passaram):
   ↓
1. Conectar ao Railway
   ↓
2. Fazer deploy da aplicação
   ↓
3. Notificar conclusão
```

**Importante:** Certifique-se que os secrets `RAILWAY_TOKEN`, `RAILWAY_PROJECT_ID` e `RAILWAY_ENVIRONMENT_ID` estão configurados, caso contrário o deploy será pulado.

---

## 🔍 Verificar Status

### Via GitHub:

1. Vá para `Actions`
2. Clique no workflow mais recente
3. Vej detalhes de cada step

### Via Railway:

1. Acesse https://railway.app
2. Vá para seu projeto
3. Veja o deploy mais recente

---

## 📝 Personalizar Workflows

### Rodar testes em mais branches:

Edite `.github/workflows/tests.yml`:

```yaml
on:
  push:
    branches: [master, develop, staging] # Adicione mais branches
```

### Mudar versão Python:

```yaml
strategy:
  matrix:
    python-version: ['3.13', '3.14'] # Testar múltiplas versões
```

### Adicionar notificações:

```yaml
- name: Notify results
  uses: 8398a7/action-slack@v3
  if: always()
  with:
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
    status: ${{ job.status }}
```

---

## 🐛 Troubleshooting

### Workflow falhando?

1. ✅ Verifique se `requirements.txt` está atualizado
2. ✅ Veja logs em Actions → Seu workflow → Logs detalhados
3. ✅ Teste localmente: `pytest tests/app -v`

### Deploy não funciona?

1. ✅ Verifique se secrets estão configurados corretamente
2. ✅ Valide Railway token: `railway login`
3. ✅ Confirme que Dockerfile está correto
4. ✅ Veja logs no Railway dashboard

### Codecov não funciona?

- É opcional e não afeta os testes
- Se quiser habilitar: crie conta em https://codecov.io
- Adicione secret `CODECOV_TOKEN` (opcional)

---

## 📚 Recursos Úteis

- 📖 [GitHub Actions Documentation](https://docs.github.com/en/actions)
- 🚂 [Railway Documentation](https://docs.railway.app)
- 🧪 [Pytest Documentation](https://docs.pytest.org)
- 🔐 [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

## ✨ Próximos Passos

1. **Configurar secrets** no GitHub
2. **Fazer push** dos workflows
3. **Monitorar** primeira execução
4. **Validar** testes e deploy
5. **Celebrar** 🎉 automação funcionando!

---

**Última atualização:** 10 de Fevereiro de 2026
