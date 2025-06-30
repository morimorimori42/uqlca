import openturns as ot
import math
from typing import List
from models.models import Layer, EmissionFactor, DesignOption, SampledEmissionFactor, StageA1, StageA2, StageA3, StageA4, StageA5
from models.results import A1Result, A2Result, A3Result, A4Result, A5Result
from calculator.deterministic_calculator import LCACalculator

class DesignOptionProbabilisticLCACalculator(LCACalculator):
    def __init__(self, layers: List[Layer], emission_factors: List[EmissionFactor], design_options: List[DesignOption], length_road: float):
        # Call the parent constructor
        super().__init__(layers, emission_factors)
        self.design_options = design_options  # New attribute for design options
        self.length_road = length_road

    def get_lognormal_distribution(self, mean, cov):
        """Return a lognormal distribution for positive means, normal distribution for negative means."""
        if mean > 0:
            variance = (cov * mean) ** 2
            sigma = (math.log(variance / mean**2 + 1)) ** 0.5
            mu = math.log(mean) - 0.5 * sigma**2
            return ot.LogNormal(mu, sigma)
        else:
            ## Handle negative means with a normal distribution
            variance = (cov * abs(mean)) ** 2
            return ot.Normal(mean, variance**0.5)


    def calculate_do_probabilistic_impact(self, n_samples: int):
        """Calculate the LCA with probabilistic sampling using OpenTURNS for multiple design options."""
        probabilistic_results_for_design_options = []
        
        # Loop over each design option
        for design_option in self.design_options:
            print(f"Calculating probabilistic LCA for Design Option: {design_option.name}")
            probabilistic_results_for_design_option = self._calculate_probabilistic_impact_for_design_option(design_option, n_samples)
            probabilistic_results_for_design_options.append(probabilistic_results_for_design_option)
        
        return probabilistic_results_for_design_options

    def _calculate_probabilistic_impact_for_design_option(self, design_option, n_samples):
        """Calculate probabilistic impact for each design option."""
        # Sample emission factors and calculate impacts for each layer in the design option
        distributions = self._get_emission_factor_distributions()  # Get distribution for each emission factor
        
        # Sample from the distributions
        ot_samples = ot.Sample(n_samples, len(distributions))
        for i in range(len(distributions)):
            ot_samples[:, i] = distributions[i].getSample(n_samples)
        
        # Results to store for this design option
        layer_results = []

        # Loop through layers in the design option
        for layer_type in design_option.layer:
            # Find the corresponding layer in the layers list
            layer = next(l for l in self.layers if l.name == layer_type.name)
            
            ## current layer type in design_options json for density and thickness
            layer_type = layer_type

            layer_results_for_current_layer = []

            # Loop through each sample iteration
            for i in range(n_samples):
                # Sampled emission factors for the current iteration
                sampled_factors = ot_samples[i, :]
                
                # Create SampledEmissionFactor instances for each material in this layer
                sampled_emission_factors = self._create_sampled_emission_factor_instances(sampled_factors, layer)
                
                # Calculate impacts for each stage (A1, A2, A3, A4, A5)
                a1_impact = self._calculate_stage_impact(layer_type, layer, sampled_emission_factors, "A1")
                a2_impact = self._calculate_stage_impact(layer_type, layer, sampled_emission_factors, "A2")
                a3_impact = self._calculate_stage_impact(layer_type, layer, sampled_emission_factors, "A3")
                a4_impact = self._calculate_stage_impact(layer_type, layer, sampled_emission_factors, "A4")
                a5_impact = self._calculate_stage_impact(layer_type, layer, sampled_emission_factors, "A5")
                
                # Collect results for the current sample iteration
                layer_results_for_current_layer.append({
                    'iteration': i,
                    'A1_result': a1_impact,
                    'A2_result': a2_impact,
                    'A3_result': a3_impact,
                    'A4_result': a4_impact,
                    'A5_result': a5_impact
                })
            
            # Store the results of all iterations for this layer
            # including thickness, density and quantity for final calculation per design option 
            layer_results.append({
                'layer': layer.name,
                'thickness': layer_type.thickness,
                'density': layer_type.density,
                'quantity': layer_type.quantity,
                'results': layer_results_for_current_layer
            })
        
        return {
            'design_option': design_option.name,
            'layer_results': layer_results
        }


    def _get_emission_factor_distributions(self):
        """Create and return a list of distributions for the emission factors."""
        distributions = []
        for ef in self.emission_factors:
            # Create distributions for total, fossil, biogenic, luluc emissions
            total_dist = self.get_lognormal_distribution(ef.mean_total, ef.cov)
            fossil_dist = self.get_lognormal_distribution(ef.mean_fossil, ef.cov)
            biogenic_dist = self.get_lognormal_distribution(ef.mean_biogenic, ef.cov)
            luluc_dist = self.get_lognormal_distribution(ef.mean_luluc, ef.cov)
            
            # Append each distribution to the list
            distributions.append(total_dist)
            distributions.append(fossil_dist)
            distributions.append(biogenic_dist)
            distributions.append(luluc_dist)
        
        return distributions

    def _create_sampled_emission_factor_instances(self, sampled_factors, layer):
        """Create SampledEmissionFactor instances for each material using the sampled values."""
        sampled_emission_factors = []
        idx = 0
        
        for ef in self.emission_factors:
            material = ef.material
            total_ef = SampledEmissionFactor(
                material=material,
                mean_total=sampled_factors[idx],
                mean_fossil=sampled_factors[idx + 1],
                mean_biogenic=sampled_factors[idx + 2],
                mean_luluc=sampled_factors[idx + 3],
                unit=ef.unit
            )
            sampled_emission_factors.append(total_ef)
            idx += 4
        
        return sampled_emission_factors

    def _calculate_stage_impact(self, layer_type, layer, sampled_emission_factors, stage_name):
        """Calculate the impact for a given stage and sampled emission factors."""
        if stage_name == "A1":
            stage_a1 = StageA1(
                name="Stage A1",
                emission_factors=sampled_emission_factors,
                materials=layer.materials
            )
            impact_data = stage_a1.calculate_stage_impact(surfaceArea=113970, density=layer_type.density, thickness=layer_type.thickness)
            return A1Result(
                gwp_total=impact_data['gwp-total'] / self.length_road,
                gwp_fossil=impact_data['gwp-fossil'] / self.length_road,
                gwp_biogenic=impact_data['gwp-biogenic'] / self.length_road,
                gwp_luluc=impact_data['gwp-luluc'] / self.length_road
            )
        elif stage_name == "A2":
            stage_a2 = StageA2(
                name="Stage A2",
                emission_factors=sampled_emission_factors,
                materials=layer.materials
            )
            impact_data = stage_a2.calculate_stage_impact(fuel_consumption_rate=0.359, actual_load=22000.0, load_capacity=22000.0, empty_return_rate=1, surfaceArea=113970, density=layer_type.density, thickness=layer_type.thickness)
            return A2Result(
                gwp_total=impact_data['gwp-total'] / self.length_road,
                gwp_fossil=impact_data['gwp-fossil'] / self.length_road,
                gwp_biogenic=impact_data['gwp-biogenic'] / self.length_road,
                gwp_luluc=impact_data['gwp-luluc'] / self.length_road
            )
        elif stage_name == "A3":
            stage_a3 = StageA3(
                name="Stage A3",
                emission_factors=sampled_emission_factors,
                energy_consumption=layer.energy_consumption_a3,
                energy_type=layer.energy_used_a3
            )
            impact_data = stage_a3.calculate_stage_impact(surfaceArea=113970, density=layer_type.density, thickness=layer_type.thickness)
            return A3Result(
                gwp_total=impact_data['gwp-total'] / self.length_road,
                gwp_fossil=impact_data['gwp-fossil'] / self.length_road,
                gwp_biogenic=impact_data['gwp-biogenic'] / self.length_road,
                gwp_luluc=impact_data['gwp-luluc'] / self.length_road
            )
        elif stage_name == "A4":
            stage_a4 = StageA4(
                name="Stage A4",
                emission_factors=sampled_emission_factors,
                transport_distance=layer.transport_distance_a4
            )
            impact_data = stage_a4.calculate_stage_impact(fuel_consumption_rate=0.359, actual_load=22000.0, load_capacity=22000.0, empty_return_rate=1, surfaceArea=113970, density=layer_type.density, thickness=layer_type.thickness)
            return A4Result(
                gwp_total=impact_data['gwp-total'] / self.length_road,
                gwp_fossil=impact_data['gwp-fossil'] / self.length_road,
                gwp_biogenic=impact_data['gwp-biogenic'] / self.length_road,
                gwp_luluc=impact_data['gwp-luluc'] / self.length_road
            )
        elif stage_name == "A5":
            stage_a5 = StageA5(
                name="Stage A5",
                emission_factors=sampled_emission_factors,
                equipments=layer.construction_a5
            )
            impact_data = stage_a5.calculate_stage_impact(equipments=layer.construction_a5, surfaceArea=113970, density=layer_type.density, thickness=layer_type.thickness)
            return A5Result(
                gwp_total=impact_data['gwp-total'] / self.length_road,
                gwp_fossil=impact_data['gwp-fossil'] / self.length_road,
                gwp_biogenic=impact_data['gwp-biogenic'] / self.length_road,
                gwp_luluc=impact_data['gwp-luluc'] / self.length_road
            )
        else:
            raise ValueError(f"Unknown stage: {stage_name}")
        

    def collect_aggregated_data(self, do_probabilistic_results):
        """
        Collect and aggregate GWP data for each design option, stage, and impact category.

        Parameters:
        - do_probabilistic_results: List of probabilistic LCA results for different design options and layers.

        Returns:
        - aggregated_data: Dictionary structured by design option, then by stage and category, containing lists of summed iteration results.
        """
        # Define the stages and GWP impact categories
        stages = ['A1', 'A2', 'A3', 'A4', 'A5']
        impact_categories = ['gwp_total', 'gwp_fossil', 'gwp_biogenic', 'gwp_luluc']

        # Initialize the structure to hold aggregated data
        aggregated_data = {}

        # Collect and sum data for each design option
        for option in do_probabilistic_results:
            design_option_name = option['design_option']
            option_results = option['layer_results']

            if design_option_name not in aggregated_data:
                aggregated_data[design_option_name] = {stage: {category: [] for category in impact_categories} for stage in stages}
            
            # Sum up results for each iteration
            num_iterations = len(option_results[0]['results'])
            for iteration_idx in range(num_iterations):
                # Initialize a temporary structure to hold summed values for this iteration
                iteration_sum = {stage: {category: 0 for category in impact_categories} for stage in stages}

                for layer in option_results:
                    iteration_data = layer['results'][iteration_idx]
                    for stage in stages:
                        stage_result = iteration_data[f'{stage}_result']
                        for category in impact_categories:
                            value = getattr(stage_result, category, 0)
                            iteration_sum[stage][category] += value

                # Append the summed results to the aggregated data
                for stage in stages:
                    for category in impact_categories:
                        aggregated_data[design_option_name][stage][category].append(iteration_sum[stage][category])
        
        return aggregated_data
    
    def collect_overall_aggregated_data(self, do_probabilistic_results):
        """
        Collect and aggregate GWP data across all stages (A1 to A5) for each design option and impact category.

        Parameters:
        - do_probabilistic_results: List of probabilistic LCA results for different design options and layers.

        Returns:
        - overall_aggregated_data: Dictionary structured by design option, containing lists of summed iteration results across all stages for each impact category.
        """
        # Define the GWP impact categories
        impact_categories = ['gwp_total', 'gwp_fossil', 'gwp_biogenic', 'gwp_luluc']

        # Initialize the structure to hold overall aggregated data
        overall_aggregated_data = {}

        # Collect and sum data for each design option
        for option in do_probabilistic_results:
            design_option_name = option['design_option']
            option_results = option['layer_results']

            if design_option_name not in overall_aggregated_data:
                overall_aggregated_data[design_option_name] = {category: [] for category in impact_categories}

            # Sum up results for each iteration across all stages
            num_iterations = len(option_results[0]['results'])
            for iteration_idx in range(num_iterations):
                # Initialize a temporary structure to hold summed values for this iteration
                iteration_sum = {category: 0 for category in impact_categories}

                for layer in option_results:
                    iteration_data = layer['results'][iteration_idx]
                    for stage in ['A1', 'A2', 'A3', 'A4', 'A5']:
                        stage_result = iteration_data[f'{stage}_result']
                        for category in impact_categories:
                            value = getattr(stage_result, category, 0)
                            iteration_sum[category] += value

                # Append the summed results to the overall aggregated data
                for category in impact_categories:
                    overall_aggregated_data[design_option_name][category].append(iteration_sum[category])

        return overall_aggregated_data
