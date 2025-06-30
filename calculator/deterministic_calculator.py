from uqlca.models.models import StageA1, StageA2, StageA3, StageA4, StageA5, Layer, EmissionFactor, DesignOption
from uqlca.models.results import A1Result, A2Result, A3Result, A4Result, A5Result, LayerResult, DesignOptionResult
from typing import List

class LCACalculator:
    def __init__(self, layers: List[Layer], emission_factors: List[EmissionFactor]):
        self.layers = layers
        self.emission_factors = emission_factors
        self.results = []  # Change to a list for storing results

    def calculate_stage_impacts(self):
        for layer in self.layers:
            # Create A1 Stage
            stage_a1 = StageA1(
                name="Stage A1",
                emission_factors=self.emission_factors,
                materials=layer.materials
            )
            ## surfaceArea, density and thickness are only important for the design option calculations
            a1_impact_data = stage_a1.calculate_stage_impact(surfaceArea=1, density=1, thickness=1)
            a1_impact = A1Result(
                gwp_total=a1_impact_data['gwp-total'],
                gwp_fossil=a1_impact_data['gwp-fossil'],
                gwp_biogenic=a1_impact_data['gwp-biogenic'],
                gwp_luluc=a1_impact_data['gwp-luluc']
            )

            # Create A2 Stage
            stage_a2 = StageA2(
                name="Stage A2",
                emission_factors=self.emission_factors,
                materials=layer.materials
            )
            a2_impact_data = stage_a2.calculate_stage_impact(fuel_consumption_rate=0.359, actual_load=22000.0, load_capacity=22000.0, empty_return_rate=1, surfaceArea=1, density=1, thickness=1)
            a2_impact = A2Result(
                gwp_total=a2_impact_data['gwp-total'],
                gwp_fossil=a2_impact_data['gwp-fossil'],
                gwp_biogenic=a2_impact_data['gwp-biogenic'],
                gwp_luluc=a2_impact_data['gwp-luluc']
            )

            # Create A3 Stage
            stage_a3 = StageA3(
                name="Stage A3",
                emission_factors=self.emission_factors,
                energy_consumption=layer.energy_consumption_a3,
                energy_type=layer.energy_used_a3
            )
            a3_impact_data = stage_a3.calculate_stage_impact(surfaceArea=1, density=1, thickness=1)
            a3_impact = A3Result(
                gwp_total=a3_impact_data['gwp-total'],
                gwp_fossil=a3_impact_data['gwp-fossil'],
                gwp_biogenic=a3_impact_data['gwp-biogenic'],
                gwp_luluc=a3_impact_data['gwp-luluc']
            )

            # Create A4 Stage
            stage_a4 = StageA4(
                name="Stage A4",
                emission_factors=self.emission_factors,
                transport_distance=layer.transport_distance_a4
            )
            a4_impact_data = stage_a4.calculate_stage_impact(fuel_consumption_rate=0.359, actual_load=22000.0, load_capacity=22000.0, empty_return_rate=1, surfaceArea=1, density=1, thickness=1)
            a4_impact = A4Result(
                gwp_total=a4_impact_data['gwp-total'],
                gwp_fossil=a4_impact_data['gwp-fossil'],
                gwp_biogenic=a4_impact_data['gwp-biogenic'],
                gwp_luluc=a4_impact_data['gwp-luluc']
            )

            # Create A5 Stage
            stage_a5 = StageA5(
                name="Stage A5",
                emission_factors=self.emission_factors,
                equipments=layer.construction_a5
            )
            a5_impact_data = stage_a5.calculate_stage_impact(equipments=layer.construction_a5, surfaceArea=1, density=1, thickness=1)
            a5_impact = A5Result(
                gwp_total=a5_impact_data['gwp-total'],
                gwp_fossil=a5_impact_data['gwp-fossil'],
                gwp_biogenic=a5_impact_data['gwp-biogenic'],
                gwp_luluc=a5_impact_data['gwp-luluc']
            )

            # Append the results to the list
            self.results.append(LayerResult(
                name=layer.name,
                a1_result=a1_impact,
                a2_result=a2_impact,
                a3_result=a3_impact,
                a4_result=a4_impact,
                a5_result=a5_impact
            ))

    def get_results(self):
        return self.results
    
    def divide_attributes_by(self, obj, divisor):
        """Divides all numeric attributes of an object by a given divisor."""
        for attr, value in vars(obj).items():
            if isinstance(value, (int, float)):  # Check if the attribute is a number
                setattr(obj, attr, value / divisor)

    def calculate_deterministic_lca_design_option(self, deterministic_result: List[LayerResult], design_options: List[DesignOption], length_road: float) -> List[DesignOptionResult]:
        results = []

        for design_option in design_options:
            # Initialize totals for each life cycle stage
            a1_total = A1Result(0, 0, 0, 0)
            a2_total = A2Result(0, 0, 0, 0)
            a3_total = A3Result(0, 0, 0, 0)
            a4_total = A4Result(0, 0, 0, 0)
            a5_total = A5Result(0, 0, 0, 0)

            # Loop through each layer in the design option and find the corresponding LayerResult
            for layer in design_option.layer:
                matching_layer_result = next((lr for lr in deterministic_result if lr.name == layer.name), None)

                if matching_layer_result:
                    surfaceArea = 113970
                    scaling_factor = layer.density * layer.thickness * surfaceArea
                    # Aggregate A1 results
                    a1_total.gwp_total += matching_layer_result.a1_result.gwp_total * scaling_factor
                    a1_total.gwp_fossil += matching_layer_result.a1_result.gwp_fossil * scaling_factor
                    a1_total.gwp_biogenic += matching_layer_result.a1_result.gwp_biogenic * scaling_factor
                    a1_total.gwp_luluc += matching_layer_result.a1_result.gwp_luluc * scaling_factor

                    # Aggregate A2 results
                    a2_total.gwp_total += matching_layer_result.a2_result.gwp_total * scaling_factor
                    a2_total.gwp_fossil += matching_layer_result.a2_result.gwp_fossil * scaling_factor
                    a2_total.gwp_biogenic += matching_layer_result.a2_result.gwp_biogenic * scaling_factor
                    a2_total.gwp_luluc += matching_layer_result.a2_result.gwp_luluc * scaling_factor

                    # Aggregate A3 results
                    a3_total.gwp_total += matching_layer_result.a3_result.gwp_total * scaling_factor
                    a3_total.gwp_fossil += matching_layer_result.a3_result.gwp_fossil * scaling_factor
                    a3_total.gwp_biogenic += matching_layer_result.a3_result.gwp_biogenic * scaling_factor
                    a3_total.gwp_luluc += matching_layer_result.a3_result.gwp_luluc * scaling_factor

                    # Aggregate A4 results
                    a4_total.gwp_total += matching_layer_result.a4_result.gwp_total * scaling_factor
                    a4_total.gwp_fossil += matching_layer_result.a4_result.gwp_fossil * scaling_factor
                    a4_total.gwp_biogenic += matching_layer_result.a4_result.gwp_biogenic * scaling_factor 
                    a4_total.gwp_luluc += matching_layer_result.a4_result.gwp_luluc * scaling_factor

                    # Aggregate A5 results
                    a5_total.gwp_total += matching_layer_result.a5_result.gwp_total * scaling_factor
                    a5_total.gwp_fossil += matching_layer_result.a5_result.gwp_fossil * scaling_factor
                    a5_total.gwp_biogenic += matching_layer_result.a5_result.gwp_biogenic * scaling_factor
                    a5_total.gwp_luluc += matching_layer_result.a5_result.gwp_luluc * scaling_factor
                else:
                    print(f"Warning: Layer '{layer.name}' not found in deterministic results.")

            # Normalize the results by length_road using the helper function
            self.divide_attributes_by(a1_total, length_road)
            self.divide_attributes_by(a2_total, length_road)
            self.divide_attributes_by(a3_total, length_road)
            self.divide_attributes_by(a4_total, length_road)
            self.divide_attributes_by(a5_total, length_road)

            # Create a DesignOptionResult instance and add to results
            design_option_result = DesignOptionResult(
                name=design_option.name,
                a1_result=a1_total,
                a2_result=a2_total,
                a3_result=a3_total,
                a4_result=a4_total,
                a5_result=a5_total
            )
            results.append(design_option_result)

        return results
