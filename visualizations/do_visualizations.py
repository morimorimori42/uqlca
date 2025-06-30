import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def plot_gwp_boxplots_aggregated(data, database_name, exclude_stages=None):
    """
    Plots boxplots for GWP values across stages (A1-A5) and categories 
    (gwp_total, gwp_fossil, gwp_biogenic, gwp_luluc) for each design option.

    Parameters:
        data (dict): Dictionary of aggregated GWP data for each design option.
        database_name (str): Name of the database for labeling.
        exclude_stages (list): List of stages to exclude from the plot (default: None).
    """
    stages = ['A1', 'A2', 'A3', 'A4', 'A5']
    impact_categories = ['gwp_total', 'gwp_fossil', 'gwp_biogenic', 'gwp_luluc']

    # Exclude specified stages
    if exclude_stages:
        stages = [stage for stage in stages if stage not in exclude_stages]

    # Initialize a list to store data for boxplots
    all_data = []

    # Populate data with results from aggregated_data
    for design_option, data in data.items():
        for stage in stages:
            for category in impact_categories:
                if category in data[stage]:
                    # Extract the values for the specific stage and category
                    values = data[stage][category]
                    all_data.extend([{
                        'design_option': design_option,
                        'stage': stage,
                        'gwp_type': category,
                        'value': value
                    } for value in values])

    # Convert the collected data to a DataFrame for plotting
    df = pd.DataFrame(all_data)

    # Define custom colors
    custom_palette = {
        'base_design': 'black',
        'alternative_design1': 'lightcoral',  # Light red
        'alternative_design2': 'blue'
    }

    # Create subplots for each GWP type in a 2x2 layout
    fig, axes = plt.subplots(2, 2, figsize=(16, 10), sharey=False)
    fig.suptitle(f'GWP results for {database_name}', fontsize=15)
    axes = axes.flatten()  # Flatten to easily iterate over

    for i, gwp_type in enumerate(impact_categories):
        ax = axes[i]
        sns.boxplot(
            data=df[df['gwp_type'] == gwp_type],
            x='stage',
            y='value',
            hue='design_option',
            ax=ax,
            palette=custom_palette,  # Apply the custom palette
            fill=False
        )
        ax.set_title(f'{gwp_type.replace("gwp_", "GWP ")}')
        ax.set_xlabel('Life Cycle Stage')
        ax.set_ylabel('GWP (kgCO2eq/FU)')

        # Add vertical lines between each life cycle stage
        xticks = ax.get_xticks()
        for x in xticks[:-1]:  # Exclude the last tick to avoid drawing a line after the last stage
            ax.axvline(x + 0.5, color='gray', linestyle='--', linewidth=0.5)

    # Remove legend from individual plots and set a single legend
    handles, labels = axes[0].get_legend_handles_labels()
    for ax in axes:
        ax.legend_.remove()

    # Add a single legend to the figure
    fig.legend(
        handles, labels, loc='lower center', ncol=len(data), 
        title=f'Design Option', fontsize='small', frameon=False
    )
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout for space for the legend and title
    plt.subplots_adjust(bottom=0.15)  # Increase space at the bottom for the legend
    plt.show()




## boxplots for multiple databases 
def prepare_boxplot_data(aggregated_data, database_name):
    """
    Prepares data for boxplot creation.

    Parameters:
    - aggregated_data: Dictionary of raw GWP data for each design option.
    - database_name: Name of the database corresponding to the data.

    Returns:
    - df: Pandas DataFrame containing raw data suitable for boxplot creation.
    """
    records = []

    # Iterate over each design option
    for design_option, data in aggregated_data.items():
        # Iterate over each impact category
        for category, values in data.items():
            # Add each raw value as a record
            for value in values:
                records.append({
                    'Design Option': design_option,
                    'Database': database_name,
                    'Impact Category': category,
                    'Value': value,
                    'Unit': 'kgCO2eq/FU'
                })

    return pd.DataFrame(records)


def create_boxplots_from_raw_data(data):
    """
    Create boxplots using raw data for the specified impact categories.

    Parameters:
    - data: Pandas DataFrame containing the raw data.
    - impact_categories: List of impact categories to visualize.
    """
    sns.set_theme(style="whitegrid")
    impact_categories = ['gwp_total', 'gwp_fossil', 'gwp_biogenic', 'gwp_luluc']

    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.flatten()

    # Define a placeholder for labels
    handles, labels = None, None

    
    for ax, category in zip(axes, impact_categories):

        custom_palette = {
            'ecoinvent': 'grey',
            'ökobaudat': 'pink',
            'EPD': 'green'
        }

        # Create boxplot without legends for subplots
        boxplot = sns.boxplot(
            data=data[data['Impact Category'] == category],
            x='Design Option',
            y='Value',
            hue='Database',
            ax=ax,
            showfliers=True,  # Display outliers
            dodge=True,
            fill=False,
            palette=custom_palette
        )
        ax.set_title(f'{category.replace("gwp_", "GWP ")}')
        ax.set_ylabel('GWP (kgCO2eq/FU)')
        ax.set_xlabel('Design Option')

        # Add vertical lines between each life cycle stage
        xticks = ax.get_xticks()
        for x in xticks[:-1]:  # Exclude the last tick to avoid drawing a line after the last stage
            ax.axvline(x + 0.5, color='gray', linestyle='--', linewidth=0.5)

        # Capture handles and labels for the legend
        if handles is None or labels is None:
            handles, labels = ax.get_legend_handles_labels()

        ax.get_legend().remove()  # Remove legend from subplot

    # Add a single legend for the figure
    fig.legend(handles, labels, title="Database", loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)

    plt.tight_layout()
    plt.show()



def plot_lca_distributions_by_design_option(full_results):
    """
    Plot the distributions of LCA results for each impact category for each design option separately.
    Each figure contains subplots for one design option, with one subplot per impact category.
    
    Parameters:
    - full_results: List of dictionaries, each containing the aggregated results for one database. 
      Each dictionary has impact categories as keys and lists of results as values, grouped by design option.
    """
    sns.set_theme(style="whitegrid")
    impact_categories = ['gwp_total', 'gwp_fossil', 'gwp_biogenic', 'gwp_luluc']
    custom_palette = {
        'ecoinvent': 'grey',
        'ökobaudat': 'pink',
        'EPD': 'green'
    }
    
    # Extract all design options from the first database's results
    design_options = list(full_results[0].keys())

    # Create a separate figure for each design option
    for design_option in design_options:
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'{design_option}', fontsize=16)

        # Flatten the axes array for easier iteration
        axes = axes.flatten()

        # Loop over each impact category and create a subplot
        for i, category in enumerate(impact_categories):
            ax = axes[i]
            ax.set_title(f'{category.replace("gwp_", "GWP ")}')

            # Plot data from all databases for the current design option and category
            for db_idx, db_results in enumerate(full_results):
                # Map database index to a name
                db_name = ['ecoinvent', 'ökobaudat', 'EPD'][db_idx]

                # Extract the data for the current design option and category
                data_to_plot = db_results[design_option].get(category, [])
                
                # Plot the KDE for the current database using the custom palette
                sns.kdeplot(
                    data_to_plot, label=db_name, ax=ax, 
                    fill=False, alpha=1, color=custom_palette[db_name]
                )

            ax.set_xlabel('GWP (kgCO2eq/FU)')
            ax.set_ylabel('Density')
            ax.legend(title="Database", loc='upper right', fontsize='small')

        # Remove unused subplot axes (if any)
        for j in range(len(impact_categories), len(axes)):
            fig.delaxes(axes[j])

        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout to fit the main title
        plt.show()

# Constants
impact_categories = ['gwp_total', 'gwp_fossil', 'gwp_biogenic', 'gwp_luluc']
stages = ['A1', 'A2', 'A3', 'A4', 'A5']

# Heatmap for Mean Values
def plot_heatmaps(combined_df):
    fig, axes = plt.subplots(2, 2, figsize=(15, 10), sharey=True)
    axes = axes.flatten()  # Flatten the axes array to iterate over it easily
    for i, impact in enumerate(impact_categories):
        # Pivot the data for heatmap
        heatmap_data = combined_df[combined_df['Impact Category'] == impact] \
            .pivot_table(index='Design Option', columns='Database', values='Mean')
        
        # Draw the heatmap on the appropriate subplot
        sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap="coolwarm", ax=axes[i])
        axes[i].set_title(f'{impact.replace("gwp_", "GWP ")}')
        axes[i].set_xlabel('Database')
        axes[i].set_ylabel('Design Option')
    
    # Adjust layout to prevent overlap
    plt.tight_layout()
    plt.show()


# Violin Plots for Boxplot Data
def plot_violin(boxplot_combined_data):
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.flatten()

    for i, impact in enumerate(impact_categories):
        # Filter data for the specific impact category
        data = boxplot_combined_data[boxplot_combined_data['Impact Category'] == impact]

        custom_palette = {
            'ecoinvent': 'grey',
            'ökobaudat': 'pink',
            'EPD': 'green'
        }

        # Plot violin plot
        sns.violinplot(
            data=data,
            x='Design Option', y='Value', hue='Database', split=True, ax=axes[i], fill=False, palette=custom_palette
        )

        # Add vertical lines between design options
        design_options = data['Design Option'].unique()
        for x in range(len(design_options) - 1):
            axes[i].axvline(x + 0.5, color='gray', linestyle='--', linewidth=0.8)

        # Set titles and labels
        axes[i].set_title(f'{impact.replace("gwp_", "GWP ")}')
        axes[i].set_xlabel('Design Option')
        axes[i].set_ylabel('GWP (kgCO2eq/FU)')
        axes[i].legend(title='Database', loc='upper right')

    plt.tight_layout()
    plt.show()


## plot distributions for stage specific LCA results
def plot_kde_distributions_by_stage(aggregated_data, database_name, selected_stages=None):
    """
    Plot KDE distributions for GWP values across impact categories (gwp_total, gwp_fossil, etc.)
    for selected life cycle stages and design options, organized in a 2x2 subplot layout.

    Parameters:
        aggregated_data (dict): Aggregated GWP data for each design option.
        database_name (str): Name of the database (for labeling).
        selected_stages (list): List of specific life cycle stages to include (default: None = all stages).
    """
    # Define all life cycle stages and impact categories
    all_stages = ['A1', 'A2', 'A3', 'A4', 'A5']
    impact_categories = ['gwp_total', 'gwp_fossil', 'gwp_biogenic', 'gwp_luluc']
    
    stages = selected_stages if selected_stages else all_stages

    # Initialize a list to collect data for KDE plots
    all_data = []

    # Populate data with results from aggregated_data
    for design_option, data in aggregated_data.items():
        for stage in stages:
            for category in impact_categories:
                if stage in data and category in data[stage]:
                    # Extract the values for the specific stage and category
                    values = data[stage][category]
                    all_data.extend([{
                        'design_option': design_option,
                        'stage': stage,
                        'gwp_type': category,
                        'value': value
                    } for value in values])

    # Convert the collected data to a DataFrame for plotting
    df = pd.DataFrame(all_data)

    # Define custom colors for design options
    custom_palette = {
        'base_design': 'black',
        'alternative_design1': 'lightcoral',
        'alternative_design2': 'blue'
    }

    # Create 2x2 subplots for each impact category
    fig, axes = plt.subplots(2, 2, figsize=(16, 10), sharex=False, sharey=False)
    fig.suptitle(f'GWP Distributions for Stage {stage} - {database_name}', fontsize=16)
    axes = axes.flatten()

    for i, category in enumerate(impact_categories):
        ax = axes[i]
        sns.kdeplot(
            data=df[df['gwp_type'] == category],
            x='value',
            hue='design_option',
            ax=ax,
            fill=False,
            common_norm=False,
            palette=custom_palette,
            alpha=1
        )
        ax.set_title(f'{category.replace("gwp_", "GWP ")}', fontsize=14)
        ax.set_xlabel('GWP (kgCO2eq/FU)', fontsize=12)
        ax.set_ylabel('Density', fontsize=12)
        ax.grid(True)
        ax.get_legend()

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])  # Adjust layout for space for title and legend
    plt.subplots_adjust(bottom=0.15)  # Add space at the bottom for the legend
    plt.show()



## stage specific boxplots for design options
def plot_stage_specific_boxplots(aggregated_results):
    """
    Plots stage-specific boxplots for each design option, with 4 subplots (2x2) for impact categories.
    Each plot compares results across different databases.

    Parameters:
        aggregated_results (list): List of aggregated results for each database.
                                   Each entry is a dictionary of design options and their results.
    """
    impact_categories = ['gwp_total', 'gwp_fossil', 'gwp_biogenic', 'gwp_luluc']
    design_options = ['base_design', 'alternative_design1', 'alternative_design2']
    stages = ['A1', 'A2', 'A3', 'A4', 'A5']  # Life cycle stages
    database_names = ['ecoinvent', 'ökobaudat', 'EPD']  # Database names for labeling

    # Custom color palette for databases
    custom_palette = {
        'ecoinvent': 'grey',
        'ökobaudat': 'pink',
        'EPD': 'green'
    }

    # Collect all data into a single DataFrame for plotting
    all_data = []
    for db_idx, db_results in enumerate(aggregated_results):
        database_name = database_names[db_idx]
        for design_option, stage_data in db_results.items():
            for stage in stages:
                if stage in stage_data:
                    for category in impact_categories:
                        if category in stage_data[stage]:
                            values = stage_data[stage][category]
                            all_data.extend([{
                                'Database': database_name,
                                'Design Option': design_option,
                                'Stage': stage,
                                'Impact Category': category,
                                'Value': value
                            } for value in values])

    # Convert data to a DataFrame
    df = pd.DataFrame(all_data)

    # Plot for each design option
    for design_option in design_options:
        fig, axes = plt.subplots(2, 2, figsize=(16, 10), sharey=False)
        axes = axes.flatten()  # Flatten to easily iterate over subplots
        fig.suptitle(f"Stage-Specific Boxplots for {design_option}", fontsize=16)

        for i, category in enumerate(impact_categories):
            ax = axes[i]
            sns.boxplot(
                data=df[(df['Design Option'] == design_option) & (df['Impact Category'] == category)],
                x='Stage',
                y='Value',
                hue='Database',
                ax=ax,
                dodge=True,
                showfliers=True,  # Display outliers
                palette=custom_palette,  # Apply the custom palette
                fill=False
            )

            ax.set_title(f"{category.replace('gwp_', 'GWP ')}")
            ax.set_xlabel('Life Cycle Stage')
            ax.set_ylabel('GWP (kgCO2eq/FU)')

            # Add vertical lines between each life cycle stage
            xticks = ax.get_xticks()
            for x in xticks[:-1]:  # Exclude the last tick to avoid drawing a line after the last stage
                ax.axvline(x + 0.5, color='gray', linestyle='--', linewidth=0.5)

            # Remove legend from individual plots
            ax.get_legend().remove()

        # Add a single legend to the figure
        handles, labels = axes[0].get_legend_handles_labels()
        fig.legend(
            handles, labels, loc='lower center', ncol=3,
            title="Database", fontsize='small', frameon=False
        )

        # Adjust layout for better spacing
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.subplots_adjust(bottom=0.15)  # Increase space at the bottom for the legend
        plt.show()