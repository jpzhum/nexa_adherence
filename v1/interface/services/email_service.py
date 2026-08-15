
import os
import tempfile
from datetime import datetime

try:
    import win32com.client as win32
except Exception:
    win32 = None

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# Presume existir e retornar dict: { 'agrup_pct': '...png', 'graf2': '...png', ... }
from interface.services.dashboard_service import salvar_graficos


# -----------------------------
# (Opcional) Gerar PDF a partir dos gráficos
# -----------------------------
def gerar_pdf_relatorio(imagens_inline: dict, pasta_destino: str, periodo: str, data_emissao: str) -> str:
    """
    Gera um PDF simples agregando os gráficos salvos.
    Retorna o caminho do PDF.
    """
    pdf_path = os.path.join(pasta_destino, f"Relatorio_Aderencia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

    styles = getSampleStyleSheet()
    story = [
        Paragraph("<b>Relatório de Aderência</b>", styles["Title"]),
        Paragraph(f"Emitido em {data_emissao}", styles["Normal"]),
        Paragraph(f"<b>Período:</b> {periodo}", styles["Normal"]),
        Spacer(1, 0.3 * inch)
    ]

    # Adiciona as imagens como páginas do PDF
    for cid, path in imagens_inline.items():
        if os.path.isfile(path):
            story.append(Paragraph(f"Gráfico: {cid}", styles["Heading3"]))
            story.append(RLImage(path, width=6.5 * inch, height=4.0 * inch))
            story.append(Spacer(1, 0.2 * inch))
            story.append(PageBreak())

    doc = SimpleDocTemplate(pdf_path, pagesize=A4, title="Relatório de Aderência")
    doc.build(story)
    return pdf_path


# -----------------------------
# Salvar gráficos e preparar anexos
# -----------------------------
def preparar_arquivos(final_df, gerar_pdf: bool = False, periodo: str = ""):
    """
    Salva gráficos e (opcionalmente) gera PDF para anexar.
    Retorna: (imagens_inline: dict, caminho_pdf: str|None)
    """
    pasta_destino = os.path.join(tempfile.gettempdir(), "graficos_relatorio")
    os.makedirs(pasta_destino, exist_ok=True)

    imagens_inline = salvar_graficos(final_df, pasta_destino) or {}

    caminho_pdf = None
    if gerar_pdf:
        data_emissao = datetime.now().strftime("%d/%m/%Y %H:%M")
        caminho_pdf = gerar_pdf_relatorio(imagens_inline, pasta_destino, periodo, data_emissao)

    return imagens_inline, caminho_pdf


# -----------------------------
# HTML do e-mail — com imagem inline principal (CID)
# -----------------------------
def montar_html(periodo: str, data_emissao: str) -> str:
    return f"""
<div style="font-family:Arial,sans-serif;color:#333;max-width:1000px;text-align:left;">
  <h2 style="color:#1F5836;margin-bottom:5px;">Relatório de Aderência</h2>
  <p style="font-size:14px;margin-top:0;">Emitido em {data_emissao}</p>
  <p style="font-size:14px;">
    Boa tarde,<br>
    Segue relatório de <strong>Aderência dos Apontamentos dos Equipamentos</strong>.
  </p>

  <!-- Imagem inline principal (CID: agrup_pct) -->
  <div style="margin:20px 0;">
    <img src="cid:agrup_pct" style="max-width:100%;"/>
  </div>

  <h3 style="color:#1F5836;">Agrupamentos</h3>
  <table style="width:100%;border-collapse:collapse;font-size:13px;text-align:left;">
    <tr>
      <td style="padding:8px;border:1px solid #ddd;">Plantio</td>
      <td style="padding:8px;border:1px solid #ddd;">Colheita</td>
      <td style="padding:8px;border:1px solid #ddd;">Irrigação</td>
    </tr>
    <tr>
      <td style="padding:8px;border:1px solid #ddd;">Preparo de Solo</td>
      <td style="padding:8px;border:1px solid #ddd;">Reflorestamento</td>
      <td style="padding:8px;border:1px solid #ddd;">Apoio Agrícola</td>
    </tr>
  </table>

  <p style="margin-top:15px;font-size:13px;color:#555;">
    <strong>Período:</strong> {periodo} | <strong>Fonte:</strong> Bases operacionais e de equipamentos
  </p>

  <p style="font-size:14px;">
    Atenciosamente,<br>
    Este e-mail foi enviado automaticamente pelo sistema.<br>
    <strong>Para d??vidas ou ajustes na automa????o:</strong><br>
    Equipe Nexa<br>
    Email: email-removido@example.com | Tel.: +55 (00) 00000-0000
  </p>

  <hr style="border:none;border-top:1px solid #ddd;margin:20px 0;">
  <p style="font-size:12px;color:#777;text-align:center;">
    Este e-mail foi gerado automaticamente via automação Python.
  </p>
</div>
    """


# -----------------------------
# Enviar e-mail (Outlook) — com inline e anexos
# -----------------------------
def enviar_email(destinatarios, cc, assunto, imagens_inline=None, caminho_pdf=None, enviar=True):
    """
    Cria e envia e-mail com gráficos inline (imagem principal via CID) e anexos.
    - assunto esperado: "Relatório de Aderência - <período>"
    """
    if win32 is None:
        raise RuntimeError("pywin32 não carregado — envio via Outlook disponível apenas no Windows.")

    outlook = win32.Dispatch("outlook.application")
    mail = outlook.CreateItem(0)

    mail.To = ";".join(destinatarios) if isinstance(destinatarios, list) else destinatarios
    mail.CC = ";".join(cc) if isinstance(cc, list) else cc
    mail.Subject = assunto

    periodo = assunto.replace("Relatório de Aderência - ", "").strip()
    data_emissao = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Corpo (HTML) com o CID correto
    mail.HTMLBody = montar_html(periodo, data_emissao)

    # Inline principal (agrup_pct)
    if imagens_inline and "agrup_pct" in imagens_inline and os.path.isfile(imagens_inline["agrup_pct"]):
        att = mail.Attachments.Add(imagens_inline["agrup_pct"])
        # Define o CID (content-id) igual ao que usamos no HTML
        att.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", "agrup_pct")

    # Outros gráficos anexados (não inline)
    if imagens_inline:
        for cid, caminho in imagens_inline.items():
            if cid != "agrup_pct" and os.path.isfile(caminho):
                mail.Attachments.Add(caminho)

    # PDF (opcional)
    if caminho_pdf and os.path.isfile(caminho_pdf):
        mail.Attachments.Add(caminho_pdf)

    if enviar:
        mail.Send()

    return True
