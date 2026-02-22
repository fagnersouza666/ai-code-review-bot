# AI Code Review Bot 🤖

Bot automático que faz code review em Pull Requests usando LLM.

**Custo:** ~$0.003 por PR  
**Tempo:** Review completa em <30s
fsdfdsfs
## Como funciona

1. Abre um PR no repo
2. GitHub Action dispara automaticamente
3. Bot analisa diff com gpt-5-nano
4. Comenta no PR com sugestões

## Features

✅ Review completa (bugs, performance, segurança)  
✅ Mostra custo real da review ($0.00X)  
✅ Sugere melhorias com exemplos de código  
✅ Identifica code smells e anti-patterns  
✅ Zero config (só adicionar secrets)

## Setup

### 1. Fork este repo

### 2. Adicionar secrets no GitHub

`Settings → Secrets and variables → Actions`:

```
OPENAI_API_KEY=sk-...
GITHUB_TOKEN=ghp_... (auto-gerado pelo GitHub Actions)
```

### 3. Ativar GitHub Actions

`Actions → Enable workflows`

### 4. Abrir um PR de teste

O bot vai comentar automaticamente!

## Configuração

Edite `.github/workflows/review.yml` para customizar:

- Modelo LLM (default: `gpt-5-nano`)
- Temperatura (default: 0.3)
- Max tokens (default: 1500)

## Custos

**gpt-5-nano:**
- Input: $0.10/1M tokens
- Output: $0.40/1M tokens

**Exemplo real (PR com 200 linhas):**
- Input: ~2k tokens ($0.0002)
- Output: ~800 tokens ($0.0003)
- **Total: $0.0005**

PRs maiores: ~$0.001-0.003

## Stack

- Python 3.10+
- OpenAI API (SDK oficial)
- PyGithub (GitHub API)
- GitHub Actions (CI/CD)

## Exemplo de Review

```markdown
## 🤖 AI Code Review

**Custo desta review:** $0.0008

### ✅ Pontos positivos
- Código bem estruturado
- Testes unitários presentes

### ⚠️ Sugestões

**1. Possível SQL Injection (linha 42)**
```python
# ❌ Evite
query = f"SELECT * FROM users WHERE id = {user_id}"

# ✅ Use
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

**2. Performance (linha 87)**
Considere usar `set()` em vez de `list` para lookups (O(1) vs O(n))

---
*Powered by gpt-5-nano | @Fagner_Souza*
```

## Licença

MIT
