
import json, os, re, sys
CAMINHO_JSON = os.path.join(os.path.dirname(sys.argv[0]), 'destinatarios.json')
DEST_PADRAO = ['email-removido@example.com']
CC_PADRAO = ['email-removido@example.com']

def carregar_destinatarios():
    if os.path.exists(CAMINHO_JSON):
        try:
            with open(CAMINHO_JSON, 'r', encoding='utf-8') as f:
                d = json.load(f)
                return d.get('destinatarios', DEST_PADRAO), d.get('cc', CC_PADRAO)
        except Exception:
            return DEST_PADRAO, CC_PADRAO
    salvar_destinatarios(DEST_PADRAO, CC_PADRAO)
    return DEST_PADRAO, CC_PADRAO

def salvar_destinatarios(dest, cc):
    with open(CAMINHO_JSON, 'w', encoding='utf-8') as f:
        json.dump({'destinatarios':dest, 'cc':cc}, f, indent=2)

def email_valido(email):
    padrao = r'^[\w\.-]+@[\w\.-]+\.[A-Za-z]{2,}$'
    return re.match(padrao, email) is not None
