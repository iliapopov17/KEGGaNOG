import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import Colormap
from typing import Optional, Tuple
import shutil
from pathlib import Path
from .base import KgnPlotBase


class KgnCorrnet(KgnPlotBase):
    pass


def correlation_network(
    df,
    figsize: Tuple[int, int] = (12, 6),
    threshold: float = 0.5,
    node_size: float = 700.0,
    node_color: str = "#A3D5FF",
    node_edgecolors: str = "#03045E",
    node_linewidths: float = 1.5,
    label_fontsize: float = 8.0,
    label_color: str = "#03045E",
    label_verticalalignment: str = "center",
    label_horizontalalignment: str = "center",
    label_weight: str = "normal",
    edge_cmap: Colormap = plt.cm.coolwarm,
    cbar_size: float = 0.5,
    title: Optional[str] = None,
    title_fontsize: float = 16.0,
    title_color: str = "black",
    title_weight: str = "normal",
    title_style: str = "normal",
    background_color="white",
    save_matrix: Optional[str] = None,
):
    """
    Generates a customizable correlation network of samples.

    Parameters:
    - df: Pandas DataFrame containing the dataset.
    - figsize: Tuple (width, height) of the figure.
    - threshold: Minimal correlation network to visualize.
    - node_size, node_color, node_edgecolors, node_linewidths: Node styling.
    - label_fontsize, label_color, label_verticalalignment, label_horizontalalignment, label_weight: Label styling.
    - edge_cmap: Colormap or string, optional (default: plt.cm.coolwarm).
      Specifies the colormap to use for edge coloring in the plot.
      This can either be a predefined `matplotlib` colormap (e.g., `plt.cm.coolwarm`)
      or a string representing the name of a colormap (e.g., 'coolwarm', 'viridis').
    - cbar_size: Colorbar size.
    - title: Title of the plot.
    - title_fontsize, title_color, title_weight, title_style: Title styling.
    - background_color: Background color of the figure.
    - save_matrix: Path to save the correlation matrix in "tsv" format;
      if None, matrix is not saved.

    Returns:
    - KgnCorrnet: An object containing the radar plot figure and axis for customization or saving.
    """

    # Select numerical columns for correlation analysis
    correlation_matrix = df.iloc[:, 1:].corr()

    # Threshold for strong correlations
    cor_threshold = threshold

    # Create a graph
    G = nx.Graph()

    # Add nodes
    for col in correlation_matrix.columns:
        G.add_node(col)

    # Add edges based on correlation cor.threshold
    edges = []
    for i, col1 in enumerate(correlation_matrix.columns):
        for j, col2 in enumerate(correlation_matrix.columns):
            if i < j and abs(correlation_matrix.iloc[i, j]) > cor_threshold:
                weight = abs(correlation_matrix.iloc[i, j])
                edges.append((col1, col2, weight))  # Save edges with weights

    # Add edges to the graph
    G.add_weighted_edges_from(edges)

    # Edge widths based on correlation strength
    weights = [d["weight"] for _, _, d in G.edges(data=True)]
    max_weight = max(weights)
    min_weight = min(weights)

    # Normalize weights to a width range (e.g., 1.0 to 2.0)
    edge_widths = [
        (
            (1.0 + (w - min_weight) / (max_weight - min_weight))
            if max_weight > min_weight
            else 2.0
        )
        for w in weights
    ]

    # Draw the network
    # Create figure
    fig, ax = plt.subplots(figsize=figsize, facecolor=background_color)
    pos = nx.spring_layout(G, seed=42)  # Layout for nodes

    # Draw nodes with borders
    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=node_size,
        node_color=node_color,
        edgecolors=node_edgecolors,  # Border color
        linewidths=node_linewidths,  # Border width
    )

    # Draw edges with dynamic widths
    edges = nx.draw_networkx_edges(
        G, pos, width=edge_widths, alpha=0.7, edge_color=weights, edge_cmap=edge_cmap
    )

    # Draw labels with centering adjustments
    nx.draw_networkx_labels(
        G,
        pos,
        font_size=label_fontsize,
        font_color=label_color,
        verticalalignment=label_verticalalignment,
        horizontalalignment=label_horizontalalignment,
        font_weight=label_weight,
    )

    # Add colorbar to represent correlation strengths
    cbar = plt.colorbar(edges, shrink=cbar_size)
    cbar.set_label("Correlation Strength")

    # Customize title
    ax.set_title(
        title,
        fontsize=title_fontsize,
        color=title_color,
        weight=title_weight,
        style=title_style,
    )

    plt.axis("off")

    if save_matrix:
        correlation_matrix.to_csv(save_matrix, sep="\t")
        print(f"Correlation matrix saved as {save_matrix}")

    # Get the path to the current directory (same location as the script)
    current_dir = Path(__file__).resolve().parent
    pycache_dir = current_dir / "__pycache__"

    # Check if __pycache__ exists and remove it
    if pycache_dir.exists() and pycache_dir.is_dir():
        shutil.rmtree(pycache_dir)

    plt.close(fig)

    return KgnCorrnet(fig, ax)
