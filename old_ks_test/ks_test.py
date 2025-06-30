import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns

def ks_test_for_full_results(full_results_dbs, design_options, num_bins=30, alpha=0.05):
    """
    Conduct Kolmogorov-Smirnov (K-S) test for the full results between multiple databases, and check for statistical significance.

    Parameters:
    - full_results_dbs: List of dictionaries where each dictionary contains design option names and their results (e.g., [{'design_option1': {'gwp_total': [...], 'gwp_fossil': [...], ...}}, {...}, ...])
    - design_options: List of design option names to test
    - impact_categories: List of impact categories to test (e.g., ['gwp_total', 'gwp_fossil', 'gwp_biogenic', 'gwp_luluc'])
    - num_bins: Number of bins for histogram plotting (default is 30)
    - alpha: Significance level for the K-S test (default is 0.05)
    """
    impact_categories = ['gwp_total', 'gwp_fossil', 'gwp_biogenic', 'gwp_luluc']

    # Loop through each impact category
    for category in impact_categories:
        all_data = []  # List to hold all results for this category across databases
        
        # Loop through each database results
        for db_results in full_results_dbs:
            db_data = []  # To hold the results for this database
            
            # Collect the data for each design_option in this database
            for design_option in design_options:
                # Assuming db_results is a dict with design_option names as keys
                # Access the corresponding design_option's results for the given category
                if design_option.name in db_results:
                    db_data.extend(db_results[design_option.name][category])
            
            # After collecting all results for this database, add it to all_data
            all_data.append(np.array(db_data))
        
        # Perform the K-S test between the first dataset and all subsequent datasets
        ks_statistic = 0
        p_value = None
        
        for i in range(1, len(all_data)):
            ks_stat, p_val = stats.ks_2samp(all_data[0], all_data[i])
            ks_statistic += ks_stat
            if p_value is None or p_val < p_value:
                p_value = p_val
        
        # Output the results of the K-S test
        print(f"Impact Category: {category}")
        print(f"Aggregated K-S Statistic: {ks_statistic:.4f}, p-value: {p_value:.4f}")
        
        # Determine if the result is significant
        if p_value < alpha:
            print(f"Result is statistically significant (p < {alpha})")
        else:
            print(f"Result is not statistically significant (p >= {alpha})")
        
        # Plot distributions with histograms and KDE for visual comparison
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for i, db_data in enumerate(all_data):
            sns.histplot(db_data, bins=num_bins, alpha=0.5, label=f"DB{i+1} - {category}", kde=True)
        
        ax.set_title(f"Distributions Comparison for {category}")
        ax.set_xlabel('GWP Value')
        ax.set_ylabel('Density')
        ax.legend()
        
        # Show the plot for the current category
        plt.show()