# Nexa Adherence v1 (Legacy)

A `v1` e mantida como referencia/fallback. A versao recomendada para uso corrente e a `v2`.

## Requisitos

- Python 3.10+
- Windows recomendado para recursos de Outlook (opcional)

## Como executar

```powershell
cd v1
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

## Destinatarios locais

- Use `v1/destinatarios.example.json` como modelo.
- Mantenha `v1/destinatarios.json` fora do Git (gitignored).

## Observacao

Se estiver iniciando o projeto agora, prefira a `v2`.
