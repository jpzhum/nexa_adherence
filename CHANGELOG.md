# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Changed
- Reworked the public README with verified architecture, setup, privacy, limitations, and v1/v2 comparison details.
- Expanded repository safety guidance, example configuration, and contribution checks.
- Sanitizacao de dados sensiveis (emails, telefone e destinatarios corporativos).
- Padronizacao de configuracao publica com `.env.example` e arquivos `destinatarios.example.json`.
- Pipeline de qualidade com Ruff, Pytest e CI no GitHub Actions.
- Melhorias de robustez em parsers da v2 (leitura de arquivo e mensagens de erro).

## [2.0.0] - 2026-02-02

### Added
- Estrutura v2 como versao principal com persistencia em SQLite e servicos modulares.

## [1.0.0] - 2025-12-18

### Added
- Versao v1 legacy com fluxo completo de consolidacao, relatorios e envio de email.
