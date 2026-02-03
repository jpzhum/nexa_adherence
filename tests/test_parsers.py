import pandas as pd
import pytest

from v2.parsers.apontamentos import load_apontamentos
from v2.parsers.equipamentos import load_equipamentos
from v2.parsers.supervisores import load_supervisores


def test_load_apontamentos_renames_synonym_columns(tmp_path) -> None:
    path = tmp_path / "apontamentos.csv"
    pd.DataFrame(
        {
            "Data": ["01/01/2026"],
            "Frota": ["EQ-01"],
            "Turno": ["TURNO A"],
        }
    ).to_csv(path, index=False)

    df = load_apontamentos(str(path))

    assert {"Data Cabecalho", "Equipamento", "Desc.Turno"}.issubset(df.columns)


def test_load_equipamentos_requires_expected_columns(tmp_path) -> None:
    path = tmp_path / "equipamentos.csv"
    pd.DataFrame({"Qualquer": [1]}).to_csv(path, index=False)

    with pytest.raises(ValueError, match="Equipamentos: colunas obrigatorias ausentes"):
        load_equipamentos(str(path))


def test_load_supervisores_supports_e_mail_header(tmp_path) -> None:
    path = tmp_path / "supervisores.csv"
    pd.DataFrame(
        {
            "Supervisor": ["Gestor 1"],
            "Agrupamento": ["COLHEITA"],
            "E-Mail": ["email-removido@example.com"],
        }
    ).to_csv(path, index=False)

    df = load_supervisores(str(path))

    assert "Gestor" in df.columns
    assert "Agrup Equipamento" in df.columns
    assert "Email" in df.columns


def test_load_apontamentos_rejects_unsupported_extension(tmp_path) -> None:
    path = tmp_path / "apontamentos.txt"
    path.write_text("invalido", encoding="utf-8")

    with pytest.raises(ValueError, match="Formato de arquivo nao suportado"):
        load_apontamentos(str(path))
