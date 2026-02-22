#!/bin/bash
# Teste local do bot (sem GitHub Actions)

set -e

echo "🧪 Testando AI Code Review Bot localmente..."

# Verifica .env
if [ ! -f .env ]; then
    echo "❌ Crie .env baseado em .env.example"
    exit 1
fi

# Carrega variáveis
export $(cat .env | grep -v '^#' | xargs)

# Pede repo e PR
read -p "Repo (ex: fagnersouza666/ai-stories-generator): " REPO
read -p "PR number: " PR_NUM

export GITHUB_REPOSITORY=$REPO
export PR_NUMBER=$PR_NUM

# Roda bot
python3 src/review_bot.py

echo "✅ Teste concluído!"
