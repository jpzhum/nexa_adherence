def render_html(resumos: dict) -> str:
    ind = resumos.get("Indicadores Gerais")
    val = ind.iloc[0].to_dict() if hasattr(ind, "iloc") else {}
    resumo_status = resumos.get("Resumo Status")

    aderencia = val.get("Aderencia Media Global", 0)
    total_esperado = val.get("Total Esperado", 0)
    total_entregue = val.get("Total Entregue", 0)
    total_nao_entregue = max(total_esperado - total_entregue, 0)

    ausentes = resumo_status.sum().get("Ausente", 0) if resumo_status is not None else 0
    incompletos = resumo_status.sum().get("Incompleto", 0) if resumo_status is not None else 0

    def pct(valor, total):
        return (valor / total * 100) if total > 0 else 0

    badge_class = "badge-ok" if aderencia >= 90 else "badge-warn"

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Indicadores Estrategicos</title>
<style>
    :root {{
      --bg: #0F172A;
      --card: #111827;
      --text: #F8FAFC;
      --muted: #9CA3AF;
      --ok: #1F5836;
      --warn: #F2B705;
      --err: #E0652F;
    }}

    * {{ box-sizing: border-box; }}
    html, body {{ height: 100%; }}
    body {{
        background: var(--bg);
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 24px;
        color: var(--text);
    }}
    .header {{
        text-align: left;
        font-size: 22px;
        font-weight: 700;
        color: var(--text);
        margin-bottom: 18px;
    }}
    .dashboard {{
        display: grid;
        grid-template-columns: repeat(3, minmax(240px, 1fr));
        gap: 16px;
        margin-bottom: 18px;
    }}
    .card {{
        background: var(--card);
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.25);
        text-align: center;
        transition: transform 0.20s ease, box-shadow 0.20s ease;
    }}
    .card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 6px 10px rgba(0,0,0,0.28);
    }}
    .card h3 {{
        font-size: 14px;
        margin-bottom: 8px;
        color: #E5E7EB;
        font-weight: 600;
    }}
    .value {{
        font-size: 30px;
        font-weight: 800;
        margin-bottom: 6px;
        color: var(--text);
        text-shadow: 0 1px 3px rgba(0,0,0,0.25);
    }}
    .legend {{
        font-size: 12px;
        color: var(--muted);
    }}
    .center-card {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 100%;
    }}

    .bars {{
        display: grid;
        grid-template-columns: repeat(2, minmax(280px, 1fr));
        gap: 16px;
    }}
    .bar-container {{
        background: var(--card);
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.25);
        transition: transform 0.20s ease, box-shadow 0.20s ease;
        text-align: center;
    }}
    .bar-container:hover {{
        transform: translateY(-4px);
        box-shadow: 0 6px 10px rgba(0,0,0,0.28);
    }}
    .bar-title {{
        font-size: 13px;
        margin-bottom: 8px;
        color: #E5E7EB;
        font-weight: 600;
        text-align: center;
    }}
    .bar {{
        height: 22px;
        background: #334155;
        border-radius: 7px;
        overflow: hidden;
        position: relative;
    }}
    .bar-fill {{
        height: 100%;
        width: 0;
        transition: width 0.8s ease-in-out;
        background: #0B6623;
    }}
    .bar-value {{
        font-size: 36px;
        font-weight: 800;
        color: var(--ok);
        margin: 10px 0;
        text-align: center;
        text-shadow: 0 1px 3px rgba(0,0,0,0.25);
    }}

    .badge {{
        display:inline-block; padding: 2px 8px; border-radius: 10px;
        font-size: 12px; font-weight: 600; margin-left: 8px;
    }}
    .badge-ok {{ background: var(--ok); color: #fff; }}
    .badge-warn {{ background: var(--warn); color: #111; }}

    canvas {{ background: transparent; }}

    @media (max-width: 768px) {{
        .dashboard, .bars {{ grid-template-columns: 1fr; }}
    }}
</style>
</head>
<body>

<div class="header">Indicadores Estrategicos</div>

<div class="dashboard">
    <div class="card">
        <h3>Aderencia Global <span class="badge {badge_class}">Meta 90%</span></h3>
        <canvas id="gaugeAderencia" width="150" height="100"></canvas>
        <div class="value" id="aderenciaValue">{aderencia:.1f}%</div>
        <div class="legend">Percentual medio de aderencia</div>
    </div>

    <div class="card center-card">
        <h3>Total Nao Entregue</h3>
        <div class="value" style="color:var(--err);">{total_nao_entregue}</div>
        <div class="legend">Itens faltantes no periodo</div>
    </div>

    <div class="card">
        <h3>Total Entregue</h3>
        <canvas id="gaugeEntregue" width="150" height="100"></canvas>
        <div class="value" style="color:var(--warn);">{total_entregue}</div>
        <div class="legend">Quantidade entregue no periodo</div>
    </div>
</div>

<div class="bars">
    <div class="bar-container">
        <div class="bar-title">Total Esperado</div>
        <div class="bar">
            <div class="bar-fill" style="background:#0B6623;" data-width="100%"></div>
        </div>
        <div class="bar-value">{total_esperado}</div>
        <div class="legend">Total esperado do periodo</div>
    </div>

    <div class="bar-container">
        <div class="bar-title">Incompletos</div>
        <div class="bar">
            <div class="bar-fill" style="background:#00ACBC;" data-width="{pct(incompletos,total_esperado):.1f}%"></div>
        </div>
        <div class="bar-value">{pct(incompletos,total_esperado):.1f}%</div>
        <div class="legend">Itens entregues parcialmente</div>
    </div>
</div>

<script>
function animateGauge(canvasId, percent, color) {{
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');
    const startAngle = Math.PI;
    const endAngle = Math.PI * (1 + percent / 100);
    let currentAngle = Math.PI;
    ctx.lineWidth = 15;

    function drawFrame() {{
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.strokeStyle = '#334155';
        ctx.beginPath();
        ctx.arc(canvas.width/2, canvas.height, 40, Math.PI, 0, false);
        ctx.stroke();

        ctx.strokeStyle = color;
        ctx.beginPath();
        ctx.arc(canvas.width/2, canvas.height, 40, startAngle, currentAngle, false);
        ctx.stroke();

        if (currentAngle < endAngle) {{
            currentAngle += 0.05;
            requestAnimationFrame(drawFrame);
        }}
    }}
    drawFrame();
}}

animateGauge('gaugeAderencia', {aderencia:.1f}, getComputedStyle(document.documentElement).getPropertyValue('--ok').trim());
animateGauge('gaugeEntregue', ({total_entregue}/{total_esperado})*100, getComputedStyle(document.documentElement).getPropertyValue('--warn').trim());

Array.from(document.querySelectorAll('.bar-fill')).forEach(bar => {{
    const width = bar.getAttribute('data-width');
    setTimeout(() => {{ bar.style.width = width; }}, 800);
}});
</script>
</body>
</html>"""
    return html
