import os
import textwrap

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager

CORES = {
    "entregue": "#1F5836",
    "parcial": "#F2B705",
    "nao_entregue": "#E86C28",
}

try:
    _fonts = {f.name for f in font_manager.fontManager.ttflist}
    if "Montserrat" in _fonts:
        plt.rcParams.update({"font.size": 12, "font.family": "Montserrat"})
    else:
        plt.rcParams.update({"font.size": 12, "font.family": "DejaVu Sans"})
except Exception:
    plt.rcParams.update({"font.size": 12, "font.family": "DejaVu Sans"})


def normalizar_colheita(df: pd.DataFrame) -> pd.DataFrame:
    if "Agrup Equipamento" not in df.columns or "Gestor" not in df.columns:
        raise ValueError("Colunas obrigatorias ausentes: Agrup Equipamento ou Gestor")

    df["Agrup Equipamento"] = df["Agrup Equipamento"].astype(str).str.strip().str.upper()
    df["Gestor"] = df["Gestor"].astype(str).str.strip().str.upper()

    for i in range(1, 6):
        mask = df["Agrup Equipamento"] == f"SAFRA F{i}"
        if mask.any():
            df.loc[mask, "Agrup Equipamento"] = "COLHEITA"
            df.loc[mask, "Gestor"] = "WANDER LUCIO"

    return df


def aplicar_estilo(ax):
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.set_facecolor("#FAFAFA")
    ax.title.set_fontsize(14)
    ax.title.set_fontweight("bold")
    ax.title.set_color(CORES["entregue"])
    if "top" in ax.spines:
        ax.spines["top"].set_visible(False)
    if "right" in ax.spines:
        ax.spines["right"].set_visible(False)


def ajustar_rotulos(labels, largura=12):
    return ["\n".join(textwrap.wrap(str(lbl), width=largura)) for lbl in labels]


def _annotate_stacked_bars(ax, bottoms, tops, labels_top, labels_bottom=None):
    for x, y, lab in zip(range(len(tops)), tops, labels_top):
        ax.text(
            x,
            y + 0.5,
            str(lab),
            ha="center",
            va="bottom",
            color="white",
            fontsize=11,
            fontweight="bold",
            bbox=dict(facecolor=CORES["entregue"], edgecolor="none", boxstyle="round,pad=0.2"),
        )

    if labels_bottom is not None:
        for x, bot, lab in zip(range(len(bottoms)), bottoms, labels_bottom):
            y_pos = (bot / 2) if bot > 0 else 0.5
            ax.text(
                x,
                y_pos,
                str(lab),
                ha="center",
                va="center",
                color="white",
                fontsize=11,
                fontweight="bold",
                bbox=dict(facecolor=CORES["nao_entregue"], edgecolor="none", boxstyle="round,pad=0.2"),
            )


def _annotate_points(ax, xs, ys, fmt="{:.0f}", color=CORES["entregue"]):
    for i, y in enumerate(ys):
        ax.text(
            i,
            y + 3,
            fmt.format(y),
            ha="center",
            va="bottom",
            color=color,
            fontsize=10,
            fontweight="bold",
            bbox=dict(facecolor="white", edgecolor=color, boxstyle="round,pad=0.2"),
        )


def grafico_situacao_geral(final_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 6))
    status = final_df["Status"].value_counts()
    valores = [status.get("Completo", 0), status.get("Incompleto", 0), status.get("Ausente", 0)]
    labels = ["Entregues", "Parciais", "Nao entregues"]
    cores = [CORES["entregue"], CORES["parcial"], CORES["nao_entregue"]]

    _, _, autotexts = ax.pie(valores, labels=labels, autopct="%1.1f%%", colors=cores, startangle=140)
    for t in autotexts:
        t.set_color("white")
        t.set_fontweight("bold")

    total = sum(valores)
    ax.set_title(f"Situacao Geral de Apontamentos - Total: {total}", fontsize=14)
    aplicar_estilo(ax)
    fig.tight_layout()
    return fig


def grafico_aderencia_qtd_turno(final_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 6))
    turnos = ["TURNO A", "TURNO B", "TURNO C"]
    entregues = [(final_df[t] == "OK").sum() for t in turnos]
    nao_entregues = [len(final_df) - e for e in entregues]
    pos = range(len(turnos))
    largura = 0.4
    ax.bar(pos, entregues, largura, label="Entregues", color=CORES["entregue"])
    ax.bar(pos, nao_entregues, largura, bottom=entregues, label="Nao entregues", color=CORES["nao_entregue"])
    for i in pos:
        ax.text(
            i,
            entregues[i] / 2,
            str(entregues[i]),
            ha="center",
            va="center",
            fontweight="bold",
            color="white",
            bbox=dict(facecolor=CORES["entregue"], edgecolor="none", boxstyle="round,pad=0.3"),
        )
        ax.text(
            i,
            entregues[i] + nao_entregues[i] / 2,
            str(nao_entregues[i]),
            ha="center",
            va="center",
            fontweight="bold",
            color="white",
            bbox=dict(facecolor=CORES["nao_entregue"], edgecolor="none", boxstyle="round,pad=0.3"),
        )
    ax.set_xticks(pos)
    ax.set_xticklabels(turnos, fontsize=11)
    ax.set_ylabel("Quantidade")
    ax.set_title("Aderencia Geral por Turno")
    ax.legend()
    aplicar_estilo(ax)
    fig.tight_layout()
    return fig


def grafico_evolucao_diaria(final_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 6))
    diario = final_df.groupby("Data Cabecalho")[["Entregues", "Faltantes"]].sum()
    x_labels = pd.to_datetime(diario.index, errors="coerce").strftime("%d/%m").tolist()
    xs = range(len(x_labels))
    y_ent = diario["Entregues"].tolist()
    y_fal = diario["Faltantes"].tolist()

    ax.plot(xs, y_ent, marker="o", color=CORES["entregue"], label="Entregues")
    ax.plot(xs, y_fal, marker="o", color=CORES["nao_entregue"], label="Faltantes")

    ax.set_xticks(xs)
    ax.set_xticklabels(x_labels)
    ax.set_ylabel("Quantidade")
    ax.set_title("Evolucao Diaria")
    ax.legend()

    _annotate_points(ax, xs, y_ent, fmt="{:.0f}", color=CORES["entregue"])
    _annotate_points(ax, xs, y_fal, fmt="{:.0f}", color=CORES["nao_entregue"])

    aplicar_estilo(ax)
    fig.tight_layout()
    return fig


def grafico_agrupamento_percent(final_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(14, 6))
    df = normalizar_colheita(final_df.copy())

    agrup = df.groupby(["Gestor", "Agrup Equipamento"])["Aderencia"].mean().round(2)
    gestores = agrup.index.get_level_values(0).unique()

    posicoes, labels, percentuais = [], [], []
    separadores, gestor_labels = [], []
    pos = 0

    for gestor in gestores:
        sub = agrup.loc[gestor]
        for grupo in sub.index:
            percentuais.append(sub.loc[grupo])
            labels.append(grupo)
            posicoes.append(pos)
            pos += 1
        separadores.append(pos)
        gestor_labels.append(gestor)

    ax.bar(posicoes, percentuais, color=CORES["entregue"])

    for i, v in enumerate(percentuais):
        ax.text(
            i,
            v + 1,
            f"{v}%",
            ha="center",
            fontweight="bold",
            color="#333",
            bbox=dict(facecolor="white", edgecolor=CORES["entregue"], boxstyle="round,pad=0.2"),
        )

    ax.axhline(90, color="red", linestyle="--", linewidth=2, label="Meta 90%")

    ax.set_xticks(posicoes)
    ax.set_xticklabels(ajustar_rotulos(labels), rotation=0, fontsize=9)

    for sep in separadores[:-1]:
        ax.axvline(sep - 0.5, color="#004080", linestyle="--", linewidth=2)

    for i, gestor in enumerate(gestor_labels):
        inicio = separadores[i - 1] if i > 0 else 0
        fim = separadores[i] - 1
        pos_texto = (inicio + fim) / 2
        ax.text(
            pos_texto,
            -10,
            gestor,
            ha="center",
            va="top",
            fontsize=10,
            fontweight="bold",
            color="#1F5836",
        )

    ax.set_ylabel("%")
    ax.set_title("Aderencia por Agrupamento [%] com Gestores")
    ax.legend()
    aplicar_estilo(ax)
    fig.subplots_adjust(bottom=0.45)
    fig.tight_layout()
    return fig


def grafico_agrupamento_qtd(final_df: pd.DataFrame, mostrar_separadores=True, mostrar_absolutos=True):
    fig, ax = plt.subplots(figsize=(14, 8))
    df = normalizar_colheita(final_df.copy())

    df = df.dropna(subset=["Agrup Equipamento"])
    df["Agrup Equipamento"] = df["Agrup Equipamento"].astype(str).str.strip().str.upper()
    df["Gestor"] = df["Gestor"].astype(str).str.strip().str.upper()

    agrup = df.groupby(["Gestor", "Agrup Equipamento"])[["Entregues", "Faltantes"]].sum()
    gestores = agrup.index.get_level_values(0).unique()

    posicoes, labels, entregues, faltantes = [], [], [], []
    separadores, gestor_labels = [], []
    pos = 0

    for gestor in gestores:
        sub = agrup.loc[gestor]
        for grupo in sub.index:
            e = int(sub.loc[grupo, "Entregues"])
            n = int(sub.loc[grupo, "Faltantes"])
            entregues.append(e)
            faltantes.append(n)
            labels.append(grupo)
            posicoes.append(pos)
            pos += 1
        separadores.append(pos)
        gestor_labels.append(gestor)

    totais = [e + n for e, n in zip(entregues, faltantes)]
    entregues_pct = [(e / t) * 100 if t > 0 else 0 for e, t in zip(entregues, totais)]
    faltantes_pct = [(n / t) * 100 if t > 0 else 0 for n, t in zip(faltantes, totais)]

    largura = 0.6
    ax.bar(posicoes, entregues_pct, largura, color=CORES["entregue"], label="Entregues")
    ax.bar(
        posicoes,
        faltantes_pct,
        largura,
        bottom=entregues_pct,
        color=CORES["nao_entregue"],
        label="Nao entregues",
    )

    if mostrar_absolutos:
        for i, (e, n) in enumerate(zip(entregues, faltantes)):
            if entregues_pct[i] > 0 and e > 0:
                ax.text(i, entregues_pct[i] / 2, str(e), ha="center", va="center", color="white", fontweight="bold")
            if faltantes_pct[i] > 0 and n > 0:
                ax.text(
                    i,
                    entregues_pct[i] + (faltantes_pct[i] / 2),
                    str(n),
                    ha="center",
                    va="center",
                    color="white",
                    fontweight="bold",
                )
    else:
        _annotate_stacked_bars(
            ax,
            bottoms=faltantes_pct,
            tops=entregues_pct,
            labels_top=[f"{v:.1f}%" for v in entregues_pct],
            labels_bottom=[f"{v:.1f}%" for v in faltantes_pct],
        )

    ax.set_xticks(posicoes)
    ax.set_xticklabels(ajustar_rotulos(labels), rotation=0, fontsize=9)

    if mostrar_separadores and len(separadores) > 1:
        for sep in separadores[:-1]:
            ax.axvline(sep - 0.5, color="#004080", linestyle="--", linewidth=2)

        y_min, y_max = ax.get_ylim()
        y_offset = y_min - (y_max * 0.08)
        for i, gestor in enumerate(gestor_labels):
            inicio = separadores[i - 1] if i > 0 else 0
            fim = separadores[i] - 1
            pos_texto = (inicio + fim) / 2
            ax.text(
                pos_texto,
                y_offset,
                gestor,
                ha="center",
                va="top",
                fontsize=10,
                fontweight="bold",
                color=CORES["entregue"],
            )
        fig.subplots_adjust(bottom=0.35)

    ax.set_ylabel("% (Escala 100%)")
    ax.set_title(
        "Aderencia por Agrupamento [100%] com Valores Absolutos"
        if mostrar_absolutos
        else "Aderencia por Agrupamento [100%] - % Entregues/Nao Entregues"
    )
    ax.legend()
    aplicar_estilo(ax)
    fig.tight_layout()
    return fig


def salvar_graficos(final_df: pd.DataFrame, pasta_destino: str):
    os.makedirs(pasta_destino, exist_ok=True)
    imagens = {}

    try:
        fig = grafico_agrupamento_percent(final_df)
        caminho = os.path.join(pasta_destino, "agrup_pct.png")
        fig.savefig(caminho, dpi=120, bbox_inches="tight")
        plt.close(fig)
        imagens["agrup_pct"] = caminho
    except Exception as exc:
        print(f"[warn] Falha ao gerar agrup_pct: {exc}")

    try:
        fig = grafico_situacao_geral(final_df)
        caminho = os.path.join(pasta_destino, "situacao_geral.png")
        fig.savefig(caminho, dpi=120, bbox_inches="tight")
        plt.close(fig)
        imagens["situacao_geral"] = caminho
    except Exception as exc:
        print(f"[warn] Falha ao gerar situacao_geral: {exc}")

    try:
        fig = grafico_aderencia_qtd_turno(final_df)
        caminho = os.path.join(pasta_destino, "aderencia_qtd_turno.png")
        fig.savefig(caminho, dpi=120, bbox_inches="tight")
        plt.close(fig)
        imagens["aderencia_qtd_turno"] = caminho
    except Exception as exc:
        print(f"[warn] Falha ao gerar aderencia_qtd_turno: {exc}")

    try:
        fig = grafico_evolucao_diaria(final_df)
        caminho = os.path.join(pasta_destino, "evolucao_diaria.png")
        fig.savefig(caminho, dpi=120, bbox_inches="tight")
        plt.close(fig)
        imagens["evolucao_diaria"] = caminho
    except Exception as exc:
        print(f"[warn] Falha ao gerar evolucao_diaria: {exc}")

    try:
        fig = grafico_agrupamento_qtd(final_df)
        caminho = os.path.join(pasta_destino, "agrup_qtd_100pct.png")
        fig.savefig(caminho, dpi=120, bbox_inches="tight")
        plt.close(fig)
        imagens["agrup_qtd_100pct"] = caminho
    except Exception as exc:
        print(f"[warn] Falha ao gerar agrup_qtd_100pct: {exc}")

    return imagens
