# interface/services/dashboard_layout_service.py

import os
import json

DEFAULT_LAYOUT = {
    "sections": [
        {"title": "Situação Geral", "chart": "grafico_situacao_geral"},
        {"title": "Aderência QTD por Turno", "chart": "grafico_aderencia_qtd_turno"},
        {"title": "Agrupamento [%]", "chart": "grafico_agrupamento_percent"},
        {"title": "Agrupamento [QTD]", "chart": "grafico_agrupamento_qtd"},
        {"title": "Evolução Diária", "chart": "grafico_evolucao_diaria"}
    ]
}

# resources/dashboard_layout.json (se existir) sobrepõe DEFAULT_LAYOUT
LAYOUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'resources', 'dashboard_layout.json')


def get_layout():
    try:
        if os.path.exists(LAYOUT_FILE):
            with open(LAYOUT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict) and 'sections' in data:
                return data
    except Exception:
        pass
    return DEFAULT_LAYOUT
