from datetime import date, datetime

import pytest

from v2.db.connection import get_connection
from v2.db.schema import ensure_schema
from v2.services.analysis_service import create_base
from v2.services.consolidation_service import consolidate_period


def _setup_db(monkeypatch, tmp_path) -> None:
    db_path = tmp_path / "pipeline_test.db"
    monkeypatch.setenv("NEXA_V2_DB_PATH", str(db_path))
    ensure_schema()


def _insert_equipamento(codigo: str, agrupamento: str = "COLHEITA") -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO equipamentos (codigo, descricao, classe, agrupamento, ativo, atualizado_em)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (codigo, "Equip", "Classe", agrupamento, 1, datetime.utcnow().isoformat()),
        )
        conn.commit()


def _insert_supervisor(chave: str, nome: str, agrupamento: str = "COLHEITA") -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO supervisores (chave, nome, email, matricula, agrupamento, atualizado_em)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (chave, nome, None, None, agrupamento, datetime.utcnow().isoformat()),
        )
        conn.commit()


def _insert_apontamento(
    data_iso: str,
    equipamento: str,
    turno: str,
    escala: str = "PADRAO",
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO apontamentos
            (import_id, data, equipamento, turno, escala, status, aderencia, entregues, faltantes, raw_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                None,
                data_iso,
                equipamento,
                turno,
                escala,
                None,
                None,
                None,
                None,
                "hash",
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()


def test_consolidate_fails_when_supervisor_base_is_missing(monkeypatch, tmp_path) -> None:
    _setup_db(monkeypatch, tmp_path)
    _insert_equipamento("EQ-01")

    with pytest.raises(ValueError, match="Base de supervisores vazia"):
        consolidate_period(date(2026, 1, 1), date(2026, 1, 1))


def test_consolidate_dedups_supervisor_group_without_row_multiplication(
    monkeypatch, tmp_path
) -> None:
    _setup_db(monkeypatch, tmp_path)
    _insert_equipamento("EQ-01", "COLHEITA")
    _insert_equipamento("EQ-02", "COLHEITA")
    _insert_supervisor("sup:1", "Gestor A", "COLHEITA")
    _insert_supervisor("sup:2", "Gestor B", "COLHEITA")

    _insert_apontamento("2026-01-01", "EQ-01", "TURNO A")
    _insert_apontamento("2026-01-01", "EQ-02", "TURNO A")

    final_df, _ = consolidate_period(date(2026, 1, 1), date(2026, 1, 1))

    assert len(final_df) == 2
    assert set(final_df["Equipamento"]) == {"EQ-01", "EQ-02"}
    assert all(final_df["Gestor"] != "Nao Informado")


def test_consolidate_handles_unknown_turno_as_outros(monkeypatch, tmp_path) -> None:
    _setup_db(monkeypatch, tmp_path)
    _insert_equipamento("EQ-01", "COLHEITA")
    _insert_supervisor("sup:1", "Gestor A", "COLHEITA")
    _insert_apontamento("2026-01-01", "EQ-01", "TURNO Z")

    final_df, _ = consolidate_period(date(2026, 1, 1), date(2026, 1, 1))

    assert "OUTROS" in final_df.columns
    assert final_df.loc[0, "OUTROS"] == "OK"
    assert final_df.loc[0, "Entregues"] == 0
    assert final_df.loc[0, "Faltantes"] == 3
    assert final_df.loc[0, "Status"] == "Ausente"


def test_consolidate_with_no_apontamentos_returns_expected_base(monkeypatch, tmp_path) -> None:
    _setup_db(monkeypatch, tmp_path)
    _insert_equipamento("EQ-01", "COLHEITA")
    _insert_supervisor("sup:1", "Gestor A", "COLHEITA")

    final_df, resumos = consolidate_period(date(2026, 1, 1), date(2026, 1, 2))

    assert len(final_df) == 2
    assert set(final_df["TURNO A"]) == {"-"}
    assert set(final_df["TURNO B"]) == {"-"}
    assert set(final_df["TURNO C"]) == {"-"}
    assert int(final_df["Entregues"].sum()) == 0
    assert int(final_df["Faltantes"].sum()) == 6

    indicadores = resumos["Indicadores Gerais"].iloc[0].to_dict()
    assert indicadores["Total Esperado"] == 6
    assert indicadores["Total Entregue"] == 0


def test_consolidate_rejects_invalid_period(monkeypatch, tmp_path) -> None:
    _setup_db(monkeypatch, tmp_path)
    _insert_equipamento("EQ-01")
    _insert_supervisor("sup:1", "Gestor A")

    with pytest.raises(ValueError, match="Data inicial maior que data final"):
        consolidate_period(date(2026, 1, 2), date(2026, 1, 1))


def test_create_base_rejects_invalid_equipment_codes() -> None:
    import pandas as pd

    df = pd.DataFrame({"Equipamento": ["", "  ", None, "nan"]})
    with pytest.raises(ValueError, match="sem codigos validos"):
        create_base(df, "2026-01-01", "2026-01-01")
