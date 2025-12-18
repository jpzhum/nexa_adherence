Nexa Adherence – V2 (Atual)

Esta é a versão atual e recomendada do sistema de Análise de Aderência.

Ela foi desenvolvida a partir do v1, porém agora com:

arquitetura modular e profissional

banco de dados interno (SQLite)

validações fortes e seguras

melhor UX e experiência operacional

exportações estruturadas

controle de estado do sistema

maior desempenho e confiabilidade

⚠️ Status: versão principal (em uso / evolução ativa)

🎯 O que o V2 faz

✔️ Importa múltiplos arquivos de apontamento
✔️ Valida estrutura (colunas obrigatórias)
✔️ Impede arquivos errados / incompletos
✔️ Deduplica dados automaticamente
✔️ Persiste tudo no banco SQLite
✔️ Aplica mesmas regras oficiais do v1
✔️ Consolida e calcula aderência
✔️ Dashboard profissional (gráficos + KPIs)
✔️ Exporta Excel formatado
✔️ Gera Base Power BI
✔️ Gera Indicadores (HTML)
✔️ Envio de e-mail via Outlook
✔️ Bloqueia ações inválidas com System State

🖥️ Requisitos

Python 3.10+

Windows recomendado (por integração com Outlook)

Dependências principais:

PyQt5

pandas / numpy

matplotlib

openpyxl

tqdm

sqlite3 (nativo do Python)

🚀 Como executar
1️⃣ Entre no diretório do v2
cd v2

2️⃣ (Opcional, mas recomendado) Criar ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip

3️⃣ Instalar dependências
pip install -r requirements.txt

4️⃣ Executar o sistema
python -m v2.app

🔌 Funcionalidades opcionais
Indicadores (HTML)

Instalar:

pip install PyQtWebEngine

Envio de e-mail via Outlook

Instalar:

pip install pywin32


Outlook precisa estar instalado e logado.

🧠 Arquitetura e Funcionamento

📌 Banco SQLite

salva dados importados

controla histórico

impede duplicidade

guarda configurações

mantém estado do sistema

📌 System State
Garante:

base carregada

dados válidos

dependências atendidas

Se faltar algo → UI bloqueia ação e explica o motivo.

📌 Pipeline

Importação → Validação → Banco de Dados → Consolidação → Dashboard / Relatórios / E-mail

📂 Estrutura do Projeto
v2/
 ├── app.py                 → inicialização
 ├── assets/                → tema, qss, recursos visuais
 ├── db/                    → conexão, schema e repositórios
 ├── parsers/               → leitura e validação de arquivos
 ├── services/              → regras de negócio
 ├── ui/                    → telas e páginas PyQt
 ├── utils/                 → logging, hash, helpers
 ├── data/                  → banco local, logs, sample data

📤 Exportações disponíveis

✔️ Excel formatado
✔️ Base oficial Power BI
✔️ Pacote de e-mail (HTML + imagens + PDF)

🧷 Quando usar o V2?

Ambiente corporativo

Operação real

Vários usuários

Necessidade de estabilidade

Segurança de dados

Evitar dependência de pastas externas

📚 Deploy corporativo

Guia completo:

docs/DEPLOYMENT.md

🧩 Empacotamento (Executável – PyInstaller)

Você pode gerar um .EXE standalone para distribuir sem precisar instalar Python nas máquinas.

📌 Pré-requisito
pip install pyinstaller

🚀 Comando recomendado (Windows)

Rodar a partir da raiz do projeto:

pyinstaller --noconfirm --onefile --windowed ^
  --name "NexaAderencia" ^
  --add-data "v2\\assets\\style.qss;v2\\assets" ^
  v2\\app.py


Resultado:

dist/NexaAderencia.exe

🔌 Recursos opcionais
✔️ Indicadores (HTML – WebEngine)
--hidden-import PyQt5.QtWebEngineWidgets

✔️ Envio de E-mail via Outlook
--hidden-import win32com.client

✔️ Layout de Dashboard via JSON
--add-data "v2\\resources\\dashboard_layout.json;v2\\resources"

💡 Comando completo (tudo habilitado)
pyinstaller --noconfirm --onefile --windowed ^
  --name "NexaAderencia" ^
  --add-data "v2\\assets\\style.qss;v2\\assets" ^
  --add-data "v2\\resources\\dashboard_layout.json;v2\\resources" ^
  --hidden-import PyQt5.QtWebEngineWidgets ^
  --hidden-import win32com.client ^
  v2\\app.py

✔️ Status

v2 → Produção / Atual

v1 → Legado / Backup técnico