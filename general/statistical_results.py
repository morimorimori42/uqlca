import pandas as pd
import numpy as np

def count_outliers(data):
    """
    Count the number of outliers in a list of numerical data using the IQR method.

    Parameters:
    - data: A list of numerical values.

    Returns:
    - outlier_count: The number of outliers in the data.
    """
    # Convert the list to a numpy array for easier calculations
    data_array = np.array(data)
    
    # Calculate the first (Q1) and third (Q3) quartiles
    Q1 = np.percentile(data_array, 25)
    Q3 = np.percentile(data_array, 75)
    
    # Calculate the Interquartile Range (IQR)
    IQR = Q3 - Q1
    
    # Define the lower and upper bounds for outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # Count the number of outliers
    outlier_count = np.sum((data_array < lower_bound) | (data_array > upper_bound))
    
    return outlier_count


## function for design options
def calculate_statistical_parameters(aggregated_data):
    """
    Calculate statistical parameters for each design option and impact category.

    Parameters:
    - aggregated_data: Dictionary of aggregated GWP data for each design option.

    Returns:
    - statistical_data: Dictionary of statistical parameters (mean, std, min, max, and 95th percentile) for each design option and impact category.
    """
    # Initialize a dictionary to store the statistical parameters
    statistical_data = {}

    # Iterate over each design option in the aggregated data
    for design_option, data in aggregated_data.items():
        statistical_data[design_option] = {}

        # Iterate over each impact category (GWP type)
        for category, values in data.items():
            # Convert the list of values to a numpy array for easier statistical operations
            values_array = np.array(values)

            # Calculate the desired statistics
            mean_val = np.mean(values_array)
            std_val = np.std(values_array)
            min_val = np.min(values_array)
            max_val = np.max(values_array)
            median_val = np.median(values_array)
            cov_val = abs(std_val) / abs(mean_val) if mean_val != 0 else 0
            percentile_95 = np.percentile(values_array, 95)

            outlier_count = count_outliers(values)

            # Store the statistical parameters in the dictionary
            statistical_data[design_option][category] = {
                'mean': mean_val,
                'std': std_val,
                'min': min_val,
                'max': max_val,
                'median': median_val,
                'cov': cov_val,
                '95th_percentile': percentile_95,
                'outliers': outlier_count
            }

    return statistical_data

def display_statistical_table(statistical_data, database_name):
    """
    Converts the statistical data into a pandas DataFrame and prints it in a table format.

    Parameters:
    - statistical_data: Dictionary of statistical parameters for each design option and impact category.
    """
    # Flatten the dictionary into a list of records for DataFrame
    records = []

    for design_option, categories in statistical_data.items():
        for category, stats in categories.items():
            records.append({
                'Design Option': design_option,
                'Database': database_name,
                'Impact Category': category,
                'Mean': stats['mean'],
                'STD': stats['std'],
                'COV': stats['cov'],
                'Min': stats['min'],
                'Max': stats['max'],
                '95th Percentile': stats['95th_percentile'],
                'Median': stats['median'],
                'Unit': 'kgCO2eq/FU',
                'Outliers': stats['outliers']
            })

    # Create a pandas DataFrame
    df = pd.DataFrame(records)

    # Print the DataFrame as a table
    print(df.to_string(index=False))

def convert_statistical_data_to_table(statistical_data, database_name):
    """
    Converts the statistical data into a pandas DataFrame.

    Parameters:
    - statistical_data: Dictionary of statistical parameters for each design option and impact category.
    - database_name: Name of the database corresponding to the data.

    Returns:
    - df: Pandas DataFrame containing the statistical data.
    """
    # Flatten the dictionary into a list of records for DataFrame
    records = []

    for design_option, categories in statistical_data.items():
        for category, stats in categories.items():
            records.append({
                'Design Option': design_option,
                'Database': database_name,
                'Impact Category': category,
                'Mean': stats['mean'],
                'STD': stats['std'],
                'COV': stats['cov'],
                'Min': stats['min'],
                'Max': stats['max'],
                '95th Percentile': stats['95th_percentile'],
                'Median': stats['median'],
                'Unit': 'kgCO2eq/FU'
            })

    # Create a pandas DataFrame
    return pd.DataFrame(records)

## function for life cycle stages 
def calculate_statistical_parameters_life_cycle_stages(aggregated_data):
    """
    Calculate statistical parameters for each design option, life cycle stage, and impact category.

    Parameters:
    - aggregated_data: Dictionary of aggregated GWP data structured as:
      {'design_option': {'life_cycle_stage': {'impact_category': [values]}}}

    Returns:
    - statistical_data: Dictionary of statistical parameters (mean, std, min, max, median, cov, and 95th percentile)
      for each design option, life cycle stage, and impact category.
    """
    # Initialize a dictionary to store the statistical parameters
    statistical_data = {}

    # Iterate over each design option in the aggregated data
    for design_option, stages in aggregated_data.items():
        statistical_data[design_option] = {}

        # Iterate over each life cycle stage
        for stage, categories in stages.items():
            statistical_data[design_option][stage] = {}

            # Iterate over each impact category
            for category, values in categories.items():
                # Convert the list of values to a numpy array for easier statistical operations
                values_array = np.array(values)

                # Calculate the desired statistics
                mean_val = np.mean(values_array)
                std_val = np.std(values_array)
                min_val = np.min(values_array)
                max_val = np.max(values_array)
                median_val = np.median(values_array)
                cov_val = abs(std_val) / abs(mean_val) if mean_val != 0 else 0
                percentile_95 = np.percentile(values_array, 95)

                # Count the outliers
                outlier_count = count_outliers(values)

                # Store the statistical parameters in the dictionary
                statistical_data[design_option][stage][category] = {
                    'mean': mean_val,
                    'std': std_val,
                    'min': min_val,
                    'max': max_val,
                    'median': median_val,
                    'cov': cov_val,
                    '95th_percentile': percentile_95,
                    'outliers': outlier_count
                }

    return statistical_data


def convert_statistical_data_to_table_life_cycle_stages(statistical_data):
    """
    Converts the nested statistical data into a pandas DataFrame.

    Parameters:
    - statistical_data: Nested dictionary of statistical parameters for each design option, life cycle stage, and impact category.
    - database_name: Name of the database corresponding to the data.

    Returns:
    - df: Pandas DataFrame containing the statistical data in tabular format.
    """
    # Flatten the dictionary into a list of records for DataFrame
    records = []

    for design_option, stages in statistical_data.items():
        for stage, categories in stages.items():
            for category, stats in categories.items():
                records.append({
                    'Design Option': design_option,
                    'Life Cycle Stage': stage,
                    'Impact Category': category,
                    'Mean': stats['mean'],
                    'STD': stats['std'],
                    'COV': stats['cov'],
                    'Min': stats['min'],
                    'Max': stats['max'],
                    '95th Percentile': stats['95th_percentile'],
                    'Median': stats['median'],
                    'Unit': 'kgCO2eq/FU',
                    'Outliers': stats['outliers']
                })

    # Create a pandas DataFrame
    return pd.DataFrame(records)
