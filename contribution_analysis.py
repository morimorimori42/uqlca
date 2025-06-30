import matplotlib.pyplot as plt
from matplotlib.cm import tab20

## contribution analysis for A1 and GWP total
def calculate_normalized_a1_contributions_multiple_emission_factors(design_options, layers, emission_factors_sets, stat_results_tables):
    """
    Calculate the normalized material contributions for A1 across multiple emission factor sets.

    Args:
        design_options (list): List of DesignOption objects.
        layers (list): List of Layer objects.
        emission_factors_sets (dict): Dictionary of emission factor sets keyed by database name.
        stat_results_tables (dict): Dictionary of statistical results tables keyed by database name.

    Returns:
        dict: Normalized contributions structured by database, design option, and materials.
    """
    contributions = {}

    for db_name, emission_factors in emission_factors_sets.items():
        contributions[db_name] = {}

        stat_results_table = stat_results_tables[db_name]

        for design_option in design_options:
            design_name = design_option.name
            contributions[db_name][design_name] = {}

            # Extract A1 gwp_total mean value from stat_results_table
            a1_mean = stat_results_table[
                (stat_results_table['Design Option'] == design_name) &
                (stat_results_table['Life Cycle Stage'] == 'A1') &
                (stat_results_table['Impact Category'] == 'gwp_total')
            ]['Mean'].values[0]
            total_impact = abs(a1_mean)  # Use absolute value for total impact

            for layer_type in design_option.layer:
                # Find matching layer in layers
                layer = next((l for l in layers if l.name == layer_type.name), None)
                if not layer:
                    continue

                # Calculate layer contribution to total impact
                surface_area = 113970  # Assume fixed value as in the StageA1 calculation
                density = layer_type.density
                thickness = layer_type.thickness
                volume = surface_area * density * thickness

                for material in layer.materials:
                    material_impact = (
                        abs(material.composition) *
                        abs(next((ef.mean_total for ef in emission_factors if ef.material == material.name), 0)) *
                        volume
                    )

                    if material.name in contributions[db_name][design_name]:
                        contributions[db_name][design_name][material.name] += material_impact
                    else:
                        contributions[db_name][design_name][material.name] = material_impact

            # Normalize contributions to percentage
            total_contribution = sum(contributions[db_name][design_name].values())
            for material_name in contributions[db_name][design_name]:
                contributions[db_name][design_name][material_name] = (
                    contributions[db_name][design_name][material_name] / total_contribution * 100
                )

    return contributions


def plot_comparison_a1_contributions(contributions):
    """
    Plot a 3x3 subplot grid comparing normalized A1 contributions across emission factor sets and design options,
    with a global legend for consistent material representation.

    Args:
        contributions (dict): Normalized contributions structured by database, design option, and materials.
    """
    databases = list(contributions.keys())
    design_options = list(contributions[databases[0]].keys())

    # Collect all unique materials for consistent coloring
    all_materials = set()
    for db_data in contributions.values():
        for design_data in db_data.values():
            all_materials.update(design_data.keys())
    all_materials = sorted(all_materials)

    # Assign consistent colors to materials
    color_map = {material: color for material, color in zip(all_materials, tab20.colors)}

    fig, axes = plt.subplots(len(design_options), len(databases), figsize=(15, 12), sharex=True, sharey=True)

    for i, design_name in enumerate(design_options):
        for j, db_name in enumerate(databases):
            data = contributions[db_name][design_name]
            labels = list(data.keys())
            sizes = list(data.values())
            colors = [color_map[label] for label in labels]  # Use consistent colors

            ax = axes[i, j]
            wedges, texts, autotexts = ax.pie(
                sizes, labels=None, autopct='%1.1f%%',
                startangle=140, textprops={'fontsize': 8}, colors=colors
            )
            ax.set_aspect('equal')  # Ensure the pie is circular
            if i == 0:
                ax.set_title(db_name, fontsize=10)
            if j == 0:
                ax.annotate(design_name, xy=(0, 0.5), xytext=(-ax.yaxis.labelpad - 5, 0),
                            xycoords=ax.yaxis.label, textcoords='offset points',
                            size='medium', ha='right', va='center', rotation=90)

    # Create a global legend
    handles = [plt.Line2D([0], [0], marker='o', color=color_map[material], markersize=10, linestyle='') for material in all_materials]
    labels = all_materials
    fig.legend(handles, labels, loc='center right', title="Materials", fontsize=8)

    plt.suptitle("Contribution Analysis Life Cycle Stage A1 - GWP total", fontsize=16)
    plt.tight_layout(rect=[0, 0, 0.85, 0.95])  # Adjust layout to make room for the global legend
    plt.show()


## contribution analysis for A1 and based on COV
def calculate_uncertainty_contributions(design_options, layers, emission_factors, stat_results_table):
    """
    Calculate the uncertainty contributions of materials for A1 using COV and mean.

    Args:
        design_options (list): List of DesignOption objects.
        layers (list): List of Layer objects.
        emission_factors (list): List of EmissionFactor objects.
        stat_results_table (pd.DataFrame): Statistical results table for the database.

    Returns:
        dict: Uncertainty contributions structured by design option and materials.
    """
    contributions = {}

    for design_option in design_options:
        design_name = design_option.name
        contributions[design_name] = {}

        # Extract A1 mean values from stat_results_table
        a1_means = stat_results_table[
            (stat_results_table['Design Option'] == design_name) &
            (stat_results_table['Life Cycle Stage'] == 'A1')
        ].set_index('Impact Category')['Mean']

        total_variance = 0
        variance_contributions = {}

        for layer_type in design_option.layer:
            # Find matching layer in layers
            layer = next((l for l in layers if l.name == layer_type.name), None)
            if not layer:
                continue

            # Calculate layer contribution to variance
            surface_area = 113970  # Assume fixed value as in the StageA1 calculation
            density = layer_type.density
            thickness = layer_type.thickness
            volume = surface_area * density * thickness

            for material in layer.materials:
                material_name = material.name
                emission_factor = next((ef for ef in emission_factors if ef.material == material_name), None)
                if not emission_factor:
                    continue

                # Calculate variance contribution using COV and mean
                cov = emission_factor.cov
                mean = emission_factor.mean_total
                variance = (cov * mean) ** 2 * material.composition * volume

                if material_name in variance_contributions:
                    variance_contributions[material_name] += variance
                else:
                    variance_contributions[material_name] = variance

                total_variance += variance

        # Normalize contributions to percentage
        for material_name, variance in variance_contributions.items():
            contributions[design_name][material_name] = (variance / total_variance) * 100

    return contributions

def plot_comparison_uncertainty_contributions(contributions_multiple):
    """
    Plot a 3x3 subplot grid comparing uncertainty contributions across databases and design options.

    Args:
        contributions_multiple (dict): Contributions structured by database and design option.
    """
    databases = list(contributions_multiple.keys())
    design_options = list(contributions_multiple[databases[0]].keys())

    # Collect all unique materials for consistent coloring
    all_materials = set()
    for db_data in contributions_multiple.values():
        for design_data in db_data.values():
            all_materials.update(design_data.keys())
    all_materials = sorted(all_materials)

    # Assign consistent colors to materials
    color_map = {material: color for material, color in zip(all_materials, tab20.colors)}

    fig, axes = plt.subplots(len(design_options), len(databases), figsize=(15, 12), sharex=True, sharey=True)

    for i, design_name in enumerate(design_options):
        for j, db_name in enumerate(databases):
            data = contributions_multiple[db_name][design_name]
            labels = list(data.keys())
            sizes = list(data.values())
            colors = [color_map[label] for label in labels]  # Use consistent colors

            ax = axes[i, j]
            wedges, texts, autotexts = ax.pie(
                sizes, labels=None, autopct='%1.1f%%',
                startangle=140, textprops={'fontsize': 8}, colors=colors
            )
            ax.set_aspect('equal')  # Ensure the pie is circular
            if i == 0:
                ax.set_title(db_name, fontsize=10)
            if j == 0:
                ax.annotate(design_name, xy=(0, 0.5), xytext=(-ax.yaxis.labelpad - 5, 0),
                            xycoords=ax.yaxis.label, textcoords='offset points',
                            size='medium', ha='right', va='center', rotation=90)

    # Create a global legend
    handles = [plt.Line2D([0], [0], marker='o', color=color_map[material], markersize=10, linestyle='') for material in all_materials]
    labels = all_materials
    fig.legend(handles, labels, loc='center right', title="Materials", fontsize=8)

    plt.suptitle("Uncertainty Contributions Comparison (A1)", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()