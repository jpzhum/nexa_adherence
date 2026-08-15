from v2.services import recipients_service


def test_email_valid() -> None:
    assert recipients_service.email_valid("email-removido@example.com")
    assert not recipients_service.email_valid("invalido")


def test_sanitize_list_removes_empty_and_duplicates() -> None:
    values = [
        "  user@example.com ",
        "",
        "copy@example.com",
        "user@example.com",
        "  ",
    ]
    assert recipients_service._sanitize_list(values) == ["user@example.com", "copy@example.com"]


def test_load_recipients_uses_env_defaults_when_file_is_missing(monkeypatch, tmp_path) -> None:
    db_path = tmp_path / "nexa.db"
    monkeypatch.setenv("NEXA_V2_DB_PATH", str(db_path))
    monkeypatch.setenv("NEXA_DEFAULT_TO", "email-removido@example.com")
    monkeypatch.setenv("NEXA_DEFAULT_CC", "email-removido@example.com")

    to, cc = recipients_service.load_recipients()

    assert to == ["email-removido@example.com"]
    assert cc == ["email-removido@example.com"]
