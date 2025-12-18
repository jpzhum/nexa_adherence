Nexa Adherence – V1 (Legacy)

Esta é a primeira versão estável do sistema de análise de aderência.
Ela foi utilizada em produção e validou totalmente as regras de negócio, consolidação e geração de relatórios.

⚠️ Status: versão legada
A versão recomendada atualmente é a v2, porém o v1 continua disponível como fallback e referência funcional.

🎯 O que o V1 faz

✔️ Consolida arquivos de apontamento
✔️ Aplica regras de aderência
✔️ Permite excluir agrupamentos / frotas
✔️ Gera relatórios Excel formatados
✔️ Exporta base para Power BI
✔️ Envia e-mail com resultados
✔️ Possui página de indicadores e dashboard

🖥️ Requisitos

Python 3.10+

Windows recomendado (por compatibilidade com Outlook e alguns serviços)

Dependências principais:

PyQt5

pandas

numpy

matplotlib

openpyxl

dateutil

(opcional) pywin32 – envio de e-mail via Outlook

🚀 Como executar o V1

1️⃣ Entre na pasta do v1:

cd v1


2️⃣ (Recomendado) Crie um ambiente virtual:

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip


3️⃣ Instale as dependências:

pip install -r requirements.txt


4️⃣ Execute o sistema:

python app.py

✉️ Funcionalidades opcionais
Página de Indicadores (HTML)

Instalar:

pip install PyQtWebEngine

Envio de e-mail via Outlook

Instalar:

pip install pywin32


Outlook precisa estar instalado e configurado.

📂 Estrutura geral do V1

interface/

telas do sistema

services/

lógica de negócio (consolidação, relatórios, e-mail, dashboard)

data/

arquivos de exemplo / bases utilizadas

destinatarios.json

gerencia os e-mails de envio

config.json

diretório de dados + exclusões

🧷 Quando usar o V1?

Use esta versão quando:

precisar de rollback

quiser comparar comportamento com o V2

for validar regras legadas

estiver em auditoria

quiser garantir estabilidade histórica

✅ Motivo de manter o V1 vivo

Mesmo com a existência do V2, o V1 segue importante porque:

prova as regras de negócio

garante fallback seguro

serve como referência técnica

facilita validações