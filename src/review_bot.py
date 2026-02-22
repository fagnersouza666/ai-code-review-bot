#!/usr/bin/env python3
"""
AI Code Review Bot
Analisa PRs com LLM e comenta sugestões
"""

import os
import sys
import json
import requests
from github import Github
from typing import Dict, Tuple
from datetime import datetime

# Configuração
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
MODEL = os.getenv("MODEL", "openai/gpt-4.1-nano")

# Preços por 1M tokens (atualizar conforme provider)
PRICING = {
    "openai/gpt-4.1-nano": {"input": 0.10, "output": 0.40},
    "anthropic/claude-sonnet-4": {"input": 3.00, "output": 15.00},
}


def get_pr_diff(repo_name: str, pr_number: int) -> str:
    """Pega o diff completo do PR"""
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    
    # Concatena diff de todos os arquivos
    diff_text = ""
    files = pr.get_files()
    
    for file in files:
        diff_text += f"\n\n{'='*60}\n"
        diff_text += f"File: {file.filename}\n"
        diff_text += f"Status: {file.status}\n"
        diff_text += f"Changes: +{file.additions} -{file.deletions}\n"
        diff_text += f"{'='*60}\n"
        diff_text += file.patch or "(Binary or no changes)"
    
    return diff_text


def build_review_prompt(diff: str, pr_title: str, pr_body: str) -> str:
    """Cria prompt para o LLM"""
    prompt = f"""You are an expert code reviewer. Analyze this Pull Request and provide constructive feedback.

**PR Title:** {pr_title}

**Description:**
{pr_body or '(No description provided)'}

**Code Changes:**
{diff}

---

**Instructions:**
1. Identify bugs, security issues, performance problems
2. Suggest improvements with code examples
3. Keep feedback actionable and respectful
4. Use markdown format
5. Focus on high-impact issues first

**Output format:**
```markdown
## 🤖 AI Code Review

### ✅ Pontos positivos
- [list positive aspects]

### ⚠️ Sugestões

**1. [Issue title] (linha X)**
[Explanation]
```python
# ❌ Avoid
[bad code]

# ✅ Better
[good code]
```

**2. [Next issue]...
```

Provide the review in **Portuguese (PT-BR)**.
"""
    return prompt


def call_llm(prompt: str) -> Tuple[str, float, int, int]:
    """
    Chama LLM via OpenRouter
    Retorna: (resposta, custo, tokens_in, tokens_out)
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 1500,
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    usage = data["usage"]
    
    tokens_in = usage["prompt_tokens"]
    tokens_out = usage["completion_tokens"]
    
    # Calcula custo
    pricing = PRICING.get(MODEL, {"input": 0.10, "output": 0.40})
    cost = (tokens_in / 1_000_000 * pricing["input"]) + \
           (tokens_out / 1_000_000 * pricing["output"])
    
    return content, cost, tokens_in, tokens_out


def post_review_comment(repo_name: str, pr_number: int, review: str, cost: float):
    """Posta review como comentário no PR"""
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    
    # Adiciona footer com custo
    full_comment = f"{review}\n\n---\n**Custo desta review:** ${cost:.4f}\n*Powered by {MODEL} | [@Fagner_Souza](https://twitter.com/Fagner_Souza)*"
    
    pr.create_issue_comment(full_comment)
    print(f"✅ Review posted! Cost: ${cost:.4f}")


def main():
    """Executa review completa"""
    # GitHub Actions passa essas variáveis
    repo_name = os.getenv("GITHUB_REPOSITORY")  # ex: fagnersouza666/repo
    pr_number = int(os.getenv("PR_NUMBER", "0"))
    
    if not repo_name or not pr_number:
        print("❌ Missing GITHUB_REPOSITORY or PR_NUMBER")
        sys.exit(1)
    
    if not OPENROUTER_API_KEY or not GITHUB_TOKEN:
        print("❌ Missing OPENROUTER_API_KEY or GITHUB_TOKEN")
        sys.exit(1)
    
    print(f"🔍 Reviewing PR #{pr_number} in {repo_name}...")
    
    # 1. Pega diff
    diff = get_pr_diff(repo_name, pr_number)
    
    # 2. Pega metadados do PR
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    
    # 3. Gera review com LLM
    prompt = build_review_prompt(diff, pr.title, pr.body)
    review, cost, tokens_in, tokens_out = call_llm(prompt)
    
    print(f"📊 Tokens: {tokens_in} in, {tokens_out} out")
    print(f"💰 Cost: ${cost:.4f}")
    
    # 4. Posta comentário
    post_review_comment(repo_name, pr_number, review, cost)
    
    print("✅ Done!")


if __name__ == "__main__":
    main()
