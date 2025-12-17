
import sys, os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor
from interface.views.main_window import MainWindow

def resource_path(*parts):
    """
    Resolve caminho de recursos tanto no dev quanto no executável PyInstaller.
    Em 'onefile', usa sys._MEIPASS; em dev, usa a pasta do arquivo atual.
    """
    base = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base, *parts)

def load_qss():
    """
    Carrega style.qss e, se existir, style.qss.append2.
    Retorna o texto concatenado.
    """
    qss = ""
    qss_path = resource_path('styles', 'style.qss')
    if os.path.isfile(qss_path):
        with open(qss_path, 'r', encoding='utf-8') as f:
            qss = f.read()
    else:
        print(f"[WARN] QSS não encontrado: {qss_path}")

    append_path = resource_path('styles', 'style.qss.append2')
    if os.path.isfile(append_path):
        with open(append_path, 'r', encoding='utf-8') as f:
            qss += "\n" + f.read()

    return qss

def apply_dark_palette(app: QApplication):
    """
    Aplica paleta escura consistente com seu tema.
    Dica: use paleta para elementos que não conflitam com QSS (textos, base, etc.).
    Para cores de botões específicos, prefira o QSS com seletores por ID.
    """
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor('#0B0F19'))
    pal.setColor(QPalette.WindowText, QColor('#E7E9EE'))
    pal.setColor(QPalette.Base, QColor('#1A2238'))
    pal.setColor(QPalette.AlternateBase, QColor('#121829'))
    pal.setColor(QPalette.ToolTipBase, QColor('#121829'))
    pal.setColor(QPalette.ToolTipText, QColor('#E7E9EE'))
    pal.setColor(QPalette.Text, QColor('#E7E9EE'))
    pal.setColor(QPalette.Button, QColor('#1A2238'))
    pal.setColor(QPalette.ButtonText, QColor('#E7E9EE'))
    pal.setColor(QPalette.BrightText, QColor('#EF4444'))
    pal.setColor(QPalette.Highlight, QColor('#22C55E'))
    pal.setColor(QPalette.HighlightedText, QColor('#0B0F19'))
    app.setPalette(pal)

def main():
    # Se usa multiprocessing em Windows, ajude o PyInstaller a inicializar corretamente:
    # import multiprocessing
    # multiprocessing.freeze_support()

    app = QApplication(sys.argv)

    # 1) Paleta primeiro (base do tema)
    apply_dark_palette(app)

    # 2) QSS por último (sobrepõe onde necessário)
    qss = load_qss()
    if qss:
        app.setStyleSheet(qss)
    else:
        print("[WARN] Stylesheet vazio. Verifique inclusão de 'styles' no build.")

    # 3) Crie e mostre a janela (QSS já carregado antes)
    win = MainWindow()
    win.showMaximized()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

