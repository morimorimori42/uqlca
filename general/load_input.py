import json

def load_data(layers_path: str, emission_factors_paths: list, design_options_path: str):
    """
    Load data from JSON files.

    Parameters:
    - layers_path: Path to the layers data JSON file.
    - emission_factors_paths: List of paths to emission factors JSON files.
    - design_options_path: Path to the design options JSON file.

    Returns:
    - layers_data: Data from the layers JSON file.
    - emission_factors_data: Combined data from all emission factors JSON files.
    - design_options_data: Data from the design options JSON file.
    """
    # Load layers and design options
    with open(layers_path, 'r') as f:
        layers_data = json.load(f)
    with open(design_options_path, 'r') as f:
        design_options_data = json.load(f)
    
    # Load and combine emission factors
    emission_factors_data = []
    for path in emission_factors_paths:
        with open(path, 'r') as f:
            emission_factors_data.append(json.load(f))
    
    return layers_data, emission_factors_data, design_options_data
