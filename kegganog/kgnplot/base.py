import matplotlib.pyplot as plt
from typing import Optional


class KgnPlotBase:
    def __init__(self, fig: plt.Figure, ax: plt.Axes):
        self.fig = fig
        self.ax = ax

    def plotfig(self) -> plt.Figure:
        self.fig.tight_layout()
        plt.show()
        return self.fig

    def savefig(self, path: str, dpi: int = 300, bbox_inches: Optional[str] = "tight"):
        """
        Save the figure to a file.

        Parameters:
        - path: Path to save the figure (e.g. "plot.png", "plot.svg").
        - dpi: Dots per inch (resolution) of the output image. Default is 300.
        - bbox_inches: Bounding box option passed to matplotlib. Default is "tight".
        """
        self.fig.savefig(path, dpi=dpi, bbox_inches=bbox_inches)
