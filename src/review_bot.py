#!/usr/bin/env python3
"""
AI Code Review Bot
Analisa PRs com LLM e comenta sugestões
"""

import os
import sys
from openai import OpenAI
from github import Github
from typing import Tuple

# Configuração
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
MODEL = os.getenv("MODEL", "gpt-5-nano")

# Preços por 1M tokens (atualizar conforme provider)
PRICING = {
    "gpt-5-nano": {"input": 0.10, "output": 0.40},
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
    Chama LLM via OpenAI Responses API
    Retorna: (resposta, custo, tokens_in, tokens_out)
    """
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.responses.create(
        model=MODEL,
        input=prompt,
        max_output_tokens=16000,
    )

    # Extrai texto da resposta
    content = response.output_text

    if not content:
        # Fallback para modelos de raciocínio: extrai summary do reasoning
        parts = []
        for item in response.output:
            if item.type == "message" and item.content:
                for block in item.content:
                    if hasattr(block, 'text'):
                        parts.append(block.text)
            elif item.type == "reasoning" and hasattr(item, 'summary') and item.summary:
                for s in item.summary:
                    if hasattr(s, 'text'):
                        parts.append(s.text)
        content = "\n".join(parts)

    usage = response.usage

    tokens_in = usage.input_tokens
    tokens_out = usage.output_tokens

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
    
    if not OPENAI_API_KEY or not GITHUB_TOKEN:
        print("❌ Missing OPENAI_API_KEY or GITHUB_TOKEN")
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
