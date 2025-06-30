import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

## not used distribution plot
def plot_overall_lca_distributions(full_results):
    """
    Plot the distributions of LCA results for each impact category from the overall aggregated results for each database.
    Each plot contains one graph for each database.
    
    Parameters:
    - full_results: List of dictionaries, each containing the aggregated results for one database. 
      Each dictionary has impact categories as keys and lists of results as values.
    """
    # Set up the plotting style
    sns.set_theme(style="whitegrid")
    impact_categories = ['gwp_total', 'gwp_fossil', 'gwp_biogenic', 'gwp_luluc']
    
    # Create the plot for each impact category (4 subplots in total, 2 rows x 2 columns)
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))  # Independent y-axis by default
    fig.suptitle('Overall GWP Distributions for Each Database', fontsize=16)

    # Flatten the axes array for easier iteration
    axes = axes.flatten()

    # Loop over each impact category and plot its distribution
    for i, category in enumerate(impact_categories):
        ax = axes[i]
        ax.set_title(f'{category.replace("_", " ").capitalize()}')

        # Loop over all full_results (one for each database)
        for db_idx, db_results in enumerate(full_results):
            # Extract the data for the current database and category
            for design_option, results in db_results.items():
                # Extract the data for the current design option and category
                data_to_plot = results.get(category, [])
                
                # Plot the KDE for the current design option and database
                sns.kdeplot(data_to_plot, label=f'{design_option} (DB{db_idx+1})', ax=ax, fill=True, alpha=0.5)

        ax.set_xlabel('GWP Value')
        ax.set_ylabel('Density')
        ax.legend(title="Database")

    # Remove unused subplot axes (if any)
    for j in range(len(impact_categories), len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout to fit the main title
    plt.show()

## this function is for material layers
def plot_lca_distributions(aggregated_data, num_bins=30):
    """
    Plot histograms with KDE lines for GWP values across categories (A1-A5) and types (gwp_total, gwp_fossil, gwp_biogenic, gwp_luluc).
    For each design option aggregated result plots.
    Parameters:
    - aggregated_data: Dictionary of aggregated GWP data for each design option.
    - num_bins: Number of bins for the histogram. Defaults to 30.
    """
    # Define the stages and GWP impact categories
    stages = ['A1', 'A2', 'A3', 'A4', 'A5']
    impact_categories = ['gwp_total', 'gwp_fossil', 'gwp_biogenic', 'gwp_luluc']

    # Set up the plotting style
    sns.set_theme(style="whitegrid")

    # Create plots for each design option
    for design_option, data in aggregated_data.items():
        fig, axs = plt.subplots(len(stages), len(impact_categories), figsize=(20, 18), constrained_layout=True)
        fig.suptitle(f'GWP Distributions for {design_option}', fontsize=20)

        # Plot each histogram with KDE
        for i, stage in enumerate(stages):
            for j, category in enumerate(impact_categories):
                ax = axs[i, j]
                sns.histplot(data[stage][category], kde=True, ax=ax, color="skyblue", edgecolor="black", bins=num_bins)
                ax.set_title(f'{stage} - {category.replace("_", " ").capitalize()}')
                ax.set_xlabel('GWP Value')
                ax.set_ylabel('Frequency' if j == 0 else '')

        plt.show()


def plot_gwp_histograms(probabilistic_results, name, num_bins=30):
    """
    Plots histograms with KDE lines for GWP values across categories (A1-A5) 
    and types (gwp_total, gwp_fossil, gwp_biogenic, gwp_luluc).
    
    Parameters:
        probabilistic_results (dict): Dictionary containing the design option and iteration results.
        num_bins (int): Number of bins for the histogram. Defaults to 30.
    """
    # Extract the list of iteration results
    results = probabilistic_results.get("results", [])
    
    categories = ['A1', 'A2', 'A3', 'A4', 'A5']
    gwp_types = ['gwp_total', 'gwp_fossil', 'gwp_biogenic', 'gwp_luluc']

    # Initialize empty dictionaries to store data for each gwp type by category
    data = {category: {gwp_type: [] for gwp_type in gwp_types} for category in categories}

    # Populate data with results
    for entry in results:
        if isinstance(entry, dict):
            for category in categories:
                category_key = f"{category}_result"
                category_result = entry.get(category_key)
                
                # Check if category_result is found and is an object (A1Result, A2Result, etc.)
                if category_result:
                    for gwp_type in gwp_types:
                        value = getattr(category_result, gwp_type, None)
                        if value is not None:
                            data[category][gwp_type].append(value)

    # Plot histograms with KDE lines for each GWP type and category
    fig, axs = plt.subplots(5, 4, figsize=(20, 18), constrained_layout=True)
    fig.suptitle(f'GWP for {name}', fontsize=20)

    for i, category in enumerate(categories):
        for j, gwp_type in enumerate(gwp_types):
            ax = axs[i, j]
            sns.histplot(data[category][gwp_type], kde=True, ax=ax, color="skyblue", edgecolor="black", bins=num_bins)
            ax.set_title(f'{category} - {gwp_type.replace("_", " ").capitalize()}')
            ax.set_xlabel('GWP Value')
            ax.set_ylabel('Frequency')

    plt.show()


def plot_gwp_boxplots(probabilistic_results):
    """
    Plots boxplots for GWP values across categories (A1-A5) and GWP types 
    (gwp_total, gwp_fossil, gwp_biogenic, gwp_luluc) for each design option.
    
    Parameters:
        probabilistic_results (list): List of dictionaries containing the design option 
                                      and iteration results.
    """
    categories = ['A1', 'A2', 'A3', 'A4', 'A5']
    gwp_types = ['gwp_total', 'gwp_fossil', 'gwp_biogenic', 'gwp_luluc']

    # Initialize a list to store data for boxplots
    all_data = []

    # Populate data with results
    for result in probabilistic_results:
        layer = result['layer']
        results = result.get("results", [])

        for entry in results:
            if isinstance(entry, dict):
                for category in categories:
                    category_key = f"{category}_result"
                    category_result = entry.get(category_key)

                    if category_result:
                        for gwp_type in gwp_types:
                            value = getattr(category_result, gwp_type, None)
                            if value is not None:
                                all_data.append({
                                    'layer': layer,
                                    'stage': category,
                                    'gwp_type': gwp_type,
                                    'value': value
                                })

    # Convert the collected data to a DataFrame for plotting
    df = pd.DataFrame(all_data)

    # Create subplots for each GWP type in a 2x2 layout
    fig, axes = plt.subplots(2, 2, figsize=(16, 10), sharey=False)
    fig.suptitle('GWP results with uncertainty range', fontsize=15)
    axes = axes.flatten()  # Flatten to easily iterate over

    for i, gwp_type in enumerate(gwp_types):
        ax = axes[i]
        sns.boxplot(
            data=df[df['gwp_type'] == gwp_type],
            x='stage',
            y='value',
            hue='layer',
            ax=ax
        )
        ax.set_title(f'{gwp_type.replace("_", " ").capitalize()}')
        ax.set_xlabel('Life Cycle Stage')
        ax.set_ylabel('GWP Value')

        # Add horizontal lines between each life cycle stage
        xticks = ax.get_xticks()
        for x in xticks[:-1]:  # Exclude the last tick to avoid drawing a line after the last stage
            ax.axvline(x + 0.5, color='gray', linestyle='--', linewidth=0.5)

    # Remove legend from individual plots and set a single legend
    handles, labels = axes[0].get_legend_handles_labels()
    for ax in axes:
        ax.legend_.remove()

    # Add a single legend to the figure
    fig.legend(
        handles, labels, loc='lower center', ncol=len(probabilistic_results), 
        title='Layer', fontsize='small', frameon=False
    )
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout for space for the legend and title
    plt.subplots_adjust(bottom=0.15)  # Increase space at the bottom for the legend
    plt.show()
