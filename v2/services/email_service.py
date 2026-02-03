import os
import shutil
import tempfile
from datetime import datetime
from typing import Dict, Optional, Tuple

try:
    import win32com.client as win32
except Exception:
    win32 = None

from v2.services.dashboard_service import salvar_graficos


def has_outlook() -> bool:
    if win32 is None:
        return False
    try:
        win32.Dispatch("outlook.application")
    except Exception:
        return False
    return True


def gerar_pdf_relatorio(
    imagens_inline: Dict[str, str], pasta_destino: str, periodo: str, data_emissao: str
) -> str:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import Image as RLImage
        from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer
    except Exception as exc:
        raise RuntimeError("ReportLab nao disponivel para gerar PDF.") from exc

    pdf_path = os.path.join(
        pasta_destino, f"Relatorio_Aderencia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    styles = getSampleStyleSheet()
    story = [
        Paragraph("<b>Relatorio de Aderencia</b>", styles["Title"]),
        Paragraph(f"Emitido em {data_emissao}", styles["Normal"]),
        Paragraph(f"<b>Periodo:</b> {periodo}", styles["Normal"]),
        Spacer(1, 0.3 * inch),
    ]

    for cid, path in imagens_inline.items():
        if os.path.isfile(path):
            story.append(Paragraph(f"Grafico: {cid}", styles["Heading3"]))
            story.append(RLImage(path, width=6.5 * inch, height=4.0 * inch))
            story.append(Spacer(1, 0.2 * inch))
            story.append(PageBreak())

    doc = SimpleDocTemplate(pdf_path, pagesize=A4, title="Relatorio de Aderencia")
    doc.build(story)
    return pdf_path


def preparar_arquivos(
    final_df, gerar_pdf: bool = False, periodo: str = ""
) -> Tuple[Dict[str, str], Optional[str]]:
    pasta_destino = os.path.join(tempfile.gettempdir(), "graficos_relatorio")
    os.makedirs(pasta_destino, exist_ok=True)

    imagens_inline = salvar_graficos(final_df, pasta_destino) or {}

    caminho_pdf = None
    if gerar_pdf:
        data_emissao = datetime.now().strftime("%d/%m/%Y %H:%M")
        caminho_pdf = gerar_pdf_relatorio(imagens_inline, pasta_destino, periodo, data_emissao)

    return imagens_inline, caminho_pdf


def montar_html(periodo: str, data_emissao: str, inline: bool = True) -> str:
    img_ref = "cid:agrup_pct" if inline else "agrup_pct.png"
    return f"""
<div style="font-family:Arial,sans-serif;color:#333;max-width:1000px;text-align:left;">
  <h2 style="color:#1F5836;margin-bottom:5px;">Relatorio de Aderencia</h2>
  <p style="font-size:14px;margin-top:0;">Emitido em {data_emissao}</p>
  <p style="font-size:14px;">
    Boa tarde,<br>
    Segue relatorio de <strong>Aderencia dos Apontamentos dos Equipamentos</strong>.
  </p>

  <div style="margin:20px 0;">
    <img src="{img_ref}" style="max-width:100%;"/>
  </div>

  <h3 style="color:#1F5836;">Agrupamentos</h3>
  <table style="width:100%;border-collapse:collapse;font-size:13px;text-align:left;">
    <tr>
      <td style="padding:8px;border:1px solid #ddd;">Plantio</td>
      <td style="padding:8px;border:1px solid #ddd;">Colheita</td>
      <td style="padding:8px;border:1px solid #ddd;">Irrigacao</td>
    </tr>
    <tr>
      <td style="padding:8px;border:1px solid #ddd;">Preparo de Solo</td>
      <td style="padding:8px;border:1px solid #ddd;">Reflorestamento</td>
      <td style="padding:8px;border:1px solid #ddd;">Apoio Agricola</td>
    </tr>
  </table>

  <p style="margin-top:15px;font-size:13px;color:#555;">
    <strong>Periodo:</strong> {periodo} | <strong>Fonte:</strong> GATec_OPE / GATec_EQP
  </p>

  <p style="font-size:14px;">
    Atenciosamente,<br>
<<<<<<< HEAD
    Este e-mail foi enviado automaticamente pelo sistema.<br>
    <strong>Para duvidas ou ajustes na automacao:</strong><br>
    Equipe Nexa<br>
    Email: email-removido@example.com | Tel.: +55 (00) 00000-0000
=======
    Este e-mail foi enviado automaticamente pelo sistema corporativo.<br>
    <strong>Para duvidas ou ajustes na automacao, entre em contato com o desenvolvedor:</strong><br>
    Joao Pedro Nogueira Silva<br>
    Email: email-removido@example.com |
>>>>>>> 89abb613f94287cc5231e5d45d9afaecda004ebf
  </p>

  <hr style="border:none;border-top:1px solid #ddd;margin:20px 0;">
  <p style="font-size:12px;color:#777;text-align:center;">
    Este e-mail foi gerado automaticamente via automacao Python.
  </p>
</div>
    """


def enviar_email(
    destinatarios,
    cc,
    assunto: str,
    imagens_inline: Optional[Dict[str, str]] = None,
    caminho_pdf: Optional[str] = None,
    enviar: bool = True,
) -> bool:
    if isinstance(destinatarios, list):
        destinatarios = [item for item in destinatarios if (item or "").strip()]
    if not destinatarios:
        raise ValueError("Lista de destinatarios vazia.")

    if win32 is None:
        raise RuntimeError("Outlook nao encontrado.")
    try:
        outlook = win32.Dispatch("outlook.application")
    except Exception as exc:
        raise RuntimeError("Outlook nao encontrado.") from exc
    mail = outlook.CreateItem(0)

    mail.To = ";".join(destinatarios) if isinstance(destinatarios, list) else destinatarios
    mail.CC = ";".join(cc) if isinstance(cc, list) else cc
    mail.Subject = assunto

    periodo = assunto.replace("Relatorio de Aderencia - ", "").strip()
    data_emissao = datetime.now().strftime("%d/%m/%Y %H:%M")

    mail.HTMLBody = montar_html(periodo, data_emissao, inline=True)

    if (
        imagens_inline
        and "agrup_pct" in imagens_inline
        and os.path.isfile(imagens_inline["agrup_pct"])
    ):
        att = mail.Attachments.Add(imagens_inline["agrup_pct"])
        att.PropertyAccessor.SetProperty(
            "http://schemas.microsoft.com/mapi/proptag/0x3712001F", "agrup_pct"
        )

    if imagens_inline:
        for cid, caminho in imagens_inline.items():
            if cid != "agrup_pct" and os.path.isfile(caminho):
                mail.Attachments.Add(caminho)

    if caminho_pdf and os.path.isfile(caminho_pdf):
        mail.Attachments.Add(caminho_pdf)

    if enviar:
        mail.Send()

    return True


def export_package(
    final_df,
    output_dir: str,
    gerar_pdf: bool = False,
    periodo: str = "",
) -> Dict[str, str]:
    os.makedirs(output_dir, exist_ok=True)
    imagens_inline, caminho_pdf = preparar_arquivos(final_df, gerar_pdf=gerar_pdf, periodo=periodo)

    imagens_out = {}
    for cid, src in imagens_inline.items():
        if os.path.isfile(src):
            name = os.path.basename(src)
            dest = os.path.join(output_dir, name)
            shutil.copy2(src, dest)
            imagens_out[cid] = dest

    data_emissao = datetime.now().strftime("%d/%m/%Y %H:%M")
    html_path = os.path.join(output_dir, "email_relatorio.html")
    with open(html_path, "w", encoding="utf-8") as handle:
        handle.write(montar_html(periodo, data_emissao, inline=False))

    pdf_out = None
    if caminho_pdf and os.path.isfile(caminho_pdf):
        pdf_out = os.path.join(output_dir, os.path.basename(caminho_pdf))
        shutil.copy2(caminho_pdf, pdf_out)

    return {"html": html_path, "pdf": pdf_out or "", "imagens": ",".join(imagens_out.values())}
