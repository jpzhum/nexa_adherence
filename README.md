# Nexa Adherence

Projeto Python para analise de aderencia operacional, com duas versoes:

- `v2/` - versao principal (recomendada)
- `v1/` - versao legacy (referencia/fallback)

## Requisitos

- Python 3.10+
- Windows recomendado para recursos de Outlook (opcional)

## Setup rapido (v2)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .[dev]
# opcional para UI:
pip install -e .[gui]
# opcional para Outlook no Windows:
pip install -e .[outlook]
```

## Configuracao

1. Copie `.env.example` para `.env` e ajuste se necessario.
2. Para destinatarios locais, use os exemplos:
   - `v1/destinatarios.example.json`
   - `v2/destinatarios.example.json`
3. Arquivos locais com dados reais nao devem ir para o Git.

## Executar

- v2 (principal):

```powershell
python v2/app.py
```

- v1 (legacy):

```powershell
python v1/app.py
```

## Qualidade

```powershell
ruff check .
ruff format .
pytest -q
```

## Estrutura

- `v2/`: app principal, parser/importacao, servicos, UI e SQLite
- `v1/`: versao legacy para referencia
- `tests/`: testes unitarios sem UI
- `.github/workflows/ci.yml`: lint + testes em `push` e `pull_request`

## Documentacao adicional

- `v2/README.md`
- `v1/README.md`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
