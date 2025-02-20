import networkx as nx
import matplotlib.pyplot as plt
import shutil
from pathlib import Path


def correlation_network(
    df,
    figsize=(12, 6),
    threshold=0.5,
    node_size=700,
    node_color="#A3D5FF",
    node_edgecolors="#03045E",
    node_linewidths=1.5,
    label_font_size=8,
    label_font_color="#03045E",
    label_verticalalignment="center",
    label_horizontalalignment="center",
    label_font_weight="bold",
    edge_cmap=plt.cm.coolwarm,
    cbar_size=0.5,
    title=None,
    title_fontsize=16,
    title_color="black",
    title_bold=True,
    title_italic=False,
    background_color="white",
    save_path=None,
    save_format="png",
    save_dpi=300,
):
    """
    Generates a highly customizable correlation network of samples.

    Parameters:
    - df: Pandas DataFrame containing the dataset
    - figsize: Tuple (width, height) of the figure
    - threshold: Minimal correlation network to visualize
    - node_size, node_color, node_edgecolors, node_linewidths: Node styling
    - label_font_size, label_font_color, label_verticalalignment, label_horizontalalignment, label_font_weight: Label styling
    - edge_cmap: Colormap
    - cbar_size: Colorbar size
    - title: Title of the plot
    - title_fontsize, title_color, title_weight, title_style: Title styling
    - background_color: Background color of the figure

    Returns:
    - Displays a correlation network with full customization.
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
        font_size=label_font_size,
        font_color=label_font_color,
        verticalalignment=label_verticalalignment,
        horizontalalignment=label_horizontalalignment,
        font_weight=label_font_weight,
    )

    # Add colorbar to represent correlation strengths
    cbar = plt.colorbar(edges, shrink=cbar_size)
    cbar.set_label("Correlation Strength")

    # Customize title
    title_weight = "bold" if title_bold else "normal"
    title_style = "italic" if title_italic else "normal"
    ax.set_title(
        title,
        fontsize=title_fontsize,
        color=title_color,
        weight=title_weight,
        style=title_style,
    )

    plt.axis("off")

    # Save figure if save_path is provided
    if save_path:
        plt.savefig(save_path, format=save_format, dpi=save_dpi, bbox_inches="tight")
        print(f"Correlation network saved as {save_path}")

    plt.show()

    # Get the path to the current directory (same location as the script)
    current_dir = Path(__file__).resolve().parent
    pycache_dir = current_dir / "__pycache__"

    # Check if __pycache__ exists and remove it
    if pycache_dir.exists() and pycache_dir.is_dir():
        shutil.rmtree(pycache_dir)
