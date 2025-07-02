import numpy as np
import json
import pandas as pd

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return super().default(obj)

def convert_statistical_data_to_json(statistical_data, json_output_path=None):
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

    if json_output_path:
        with open(json_output_path, 'w', encoding='utf-8') as json_file:
            json.dump(records, json_file, indent=4, cls=NpEncoder)
        print(f"JSON saved to {json_output_path}")

    return pd.DataFrame(records)
