# Nexa Adherence v2 (Principal)

A `v2` e a versao recomendada do projeto.

## Requisitos

- Python 3.10+
- Dependencias de runtime instaladas no ambiente

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .[dev]
pip install -e .[gui]        # opcional (UI completa)
pip install -e .[outlook]    # opcional no Windows (envio via Outlook)
```

## Configuracao

1. Copie `.env.example` para `.env` na raiz do projeto.
2. Se for usar lista de destinatarios local, copie `v2/destinatarios.example.json` para `v2/data/destinatarios.json`.
3. Ajuste os valores de exemplo antes de usar em ambiente real.

## Executar

Na raiz do repositorio:

```powershell
python v2/app.py
```

## Validacoes e qualidade

```powershell
ruff check .
ruff format .
pytest -q
```

## Troubleshooting

- **Erro de importacao de planilha**: confirme extensao (`.xlsx`, `.xls`, `.xlsm`, `.csv`) e colunas obrigatorias.
- **Erro de encoding em CSV**: salve o arquivo em UTF-8 ou Latin-1.
- **Outlook indisponivel**: instale `pywin32`, abra o Outlook e tente novamente.
- **UI nao abre no Linux/CI**: rode apenas testes unitarios (sem interface grafica).
