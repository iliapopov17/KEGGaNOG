import matplotlib.pyplot as plt
import seaborn as sns

def boxplot(
    df, 
    figsize=(12, 6), 
    color="blue", 
    showfliers=True,
    title="Distribution of Pathway Completeness Across Samples",
    title_fontsize=16, title_color="black", title_weight="bold", title_style="normal",
    xlabel="Samples", xlabel_fontsize=14, xlabel_color="black", xlabel_weight="bold", xlabel_style="normal",
    ylabel="Completeness Value", ylabel_fontsize=14, ylabel_color="black", ylabel_weight="bold", ylabel_style="normal",
    xticks_rotation=45, xticks_fontsize=12, xticks_color="black", xtick_weight="normal", xtick_style="normal",
    yticks_fontsize=12, yticks_color="black", ytick_weight="normal", ytick_style="normal",
    grid=True, grid_color="gray", grid_linestyle="--", grid_linewidth=0.5,
    background_color="white"
):
    """
    Generates a highly customizable boxplot for pathway completeness.

    Parameters:
    - df: Pandas DataFrame containing the dataset
    - figsize: Tuple (width, height) of the figure
    - color: Box color
    - showfliers: Boolean, whether to show outliers
    - title: Title of the plot
    - title_fontsize, title_color, title_weight, title_style: Title styling
    - xlabel, ylabel: Labels for axes
    - xlabel_fontsize, xlabel_color, xlabel_weight, xlabel_style: X-axis label styling
    - ylabel_fontsize, ylabel_color, ylabel_weight, ylabel_style: Y-axis label styling
    - xticks_rotation, xticks_fontsize, xticks_color, xtick_weight, xtick_style: X-ticks styling
    - yticks_fontsize, yticks_color, ytick_weight, ytick_style: Y-ticks styling
    - grid: Whether to show grid
    - grid_color, grid_linestyle, grid_linewidth: Grid styling
    - background_color: Background color of the figure

    Returns:
    - Displays a boxplot with full customization.
    """

    # Create figure
    fig, ax = plt.subplots(figsize=figsize, facecolor=background_color)

    # Create boxplot
    sns.boxplot(data=df.iloc[:, 1:], color=color, showfliers=showfliers, ax=ax)

    # Customize title
    ax.set_title(title, fontsize=title_fontsize, color=title_color, weight=title_weight, style=title_style)

    # Customize x-axis label
    ax.set_xlabel(xlabel, fontsize=xlabel_fontsize, color=xlabel_color, weight=xlabel_weight, style=xlabel_style)

    # Customize y-axis label
    ax.set_ylabel(ylabel, fontsize=ylabel_fontsize, color=ylabel_color, weight=ylabel_weight, style=ylabel_style)

    # Customize x-ticks
    plt.xticks(rotation=xticks_rotation, fontsize=xticks_fontsize, color=xticks_color, weight=xtick_weight, style=xtick_style)

    # Customize y-ticks
    plt.yticks(fontsize=yticks_fontsize, color=yticks_color, weight=ytick_weight, style=ytick_style)

    # Grid settings
    if grid:
        plt.grid(color=grid_color, linestyle=grid_linestyle, linewidth=grid_linewidth)

    # Show plot
    plt.show()