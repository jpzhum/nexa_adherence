import json
import os

DEFAULT_LAYOUT = {
    "sections": [
        {"title": "Situacao Geral", "chart": "grafico_situacao_geral"},
        {"title": "Aderencia QTD por Turno", "chart": "grafico_aderencia_qtd_turno"},
        {"title": "Agrupamento [%]", "chart": "grafico_agrupamento_percent"},
        {"title": "Agrupamento [QTD]", "chart": "grafico_agrupamento_qtd"},
        {"title": "Evolucao Diaria", "chart": "grafico_evolucao_diaria"},
    ]
}

LAYOUT_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "resources", "dashboard_layout.json"
)


def get_layout():
    try:
        if os.path.exists(LAYOUT_FILE):
            with open(LAYOUT_FILE, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, dict) and "sections" in data:
                return data
    except Exception:
        pass
    return DEFAULT_LAYOUT
