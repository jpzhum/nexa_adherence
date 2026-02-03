from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QVBoxLayout, QWidget


class ChartView(QWidget):
    def __init__(self):
        super().__init__()
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def render(self, dataset, group_by: str, metric: str, chart_type: str):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if dataset is None or dataset.empty:
            ax.text(0.5, 0.5, "Sem dados", ha="center", va="center")
            ax.set_axis_off()
            self.canvas.draw()
            return

        labels = dataset[group_by].astype(str).tolist()
        values = dataset["Valor"].tolist()
        xs = list(range(len(labels)))
        if chart_type == "linha":
            ax.plot(xs, values, marker="o", color="#0EA5A5")
        else:
            ax.bar(xs, values, color="#0EA5A5")
        ax.set_xticks(xs)
        ax.set_xticklabels(labels, rotation=30, ha="right")
        ax.set_title(f"{metric} por {group_by}")
        ax.set_ylabel("Valor")
        self.figure.tight_layout()
        self.canvas.draw()
