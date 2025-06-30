import openturns as ot
import math
from typing import List
from models.models import Layer, EmissionFactor, StageA1, StageA2, StageA3, StageA4, StageA5, SampledEmissionFactor, Equipment
from models.results import A1Result, A2Result, A3Result, A4Result, A5Result
from calculator.deterministic_calculator import LCACalculator  # Assuming LCACalculator is imported from another file

class ProbabilisticLCACalculator(LCACalculator):
    def __init__(self, layers: List[Layer], emission_factors: List[EmissionFactor]):
        # Call the parent constructor
        super().__init__(layers, emission_factors)

    def get_lognormal_distribution(self, mean, cov):
        """Return a lognormal distribution for a given mean and variance."""
        ## first converting the mean and variance to the parameters (mu and sigma) of the underlying normal distribution
        ## then sampling based on those parameters
        if mean > 0:
            variance = (cov * mean) ** 2
            sigma = (math.log(variance / mean**2 + 1)) ** 0.5
            mu = math.log(mean) - 0.5 * sigma**2
            return ot.LogNormal(mu, sigma)
        else:
            variance = (cov * abs(mean)) ** 2
            return ot.Normal(mean, variance**0.5)

    def calculate_probabilistic_impact(self, n_samples: int):
        """Calculate the LCA with probabilistic sampling using OpenTURNS."""
        # Define the probabilistic distributions for each emission factor
        distributions = self._get_emission_factor_distributions()
        
        # Sample from the distributions
        ot_samples = ot.Sample(n_samples, len(distributions))
        for i in range(len(distributions)):
            ot_samples[:, i] = distributions[i].getSample(n_samples)
        
        probabilistic_results = []
        
        for layer in self.layers:
            layer_results = []
            
            # Loop over each sample iteration
            for i in range(n_samples):
                # Sampled emission factors for the current iteration
                sampled_factors = ot_samples[i, :]
                
                # Create SampledEmissionFactor instances for each material using the sampled values
                sampled_emission_factors = self._create_sampled_emission_factor_instances(sampled_factors=sampled_factors, layer=layer)
                
                # Calculate impacts for each stage using the sampled SampledEmissionFactor instances
                a1_impact = self._calculate_stage_impact(layer, sampled_emission_factors, "A1")
                a2_impact = self._calculate_stage_impact(layer, sampled_emission_factors, "A2")
                a3_impact = self._calculate_stage_impact(layer, sampled_emission_factors, "A3")
                a4_impact = self._calculate_stage_impact(layer, sampled_emission_factors, "A4")
                a5_impact = self._calculate_stage_impact(layer, sampled_emission_factors, "A5")
                
                # Collect results for the current sample iteration
                layer_results.append({
                    'iteration': i,
                    'A1_result': a1_impact,
                    'A2_result': a2_impact,
                    'A3_result': a3_impact,
                    'A4_result': a4_impact,
                    'A5_result': a5_impact
                })
            
            # Store the results of all iterations for this design option
            probabilistic_results.append({
                'layer': layer.name,
                'results': layer_results
            })
        
        return probabilistic_results

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
            # Assume each EmissionFactor corresponds to a material
            material = ef.material
            
            # Create new SampledEmissionFactor instances for total, fossil, biogenic, and luluc emissions
            total_ef = SampledEmissionFactor(
                material=material,
                mean_total=sampled_factors[idx],
                mean_fossil=sampled_factors[idx + 1],
                mean_biogenic=sampled_factors[idx + 2],
                mean_luluc=sampled_factors[idx + 3],
                unit=ef.unit  # Assuming units are the same for each emission type
            )
            sampled_emission_factors.append(total_ef)
            idx += 4
        
        return sampled_emission_factors

    def _calculate_stage_impact(self, layer, sampled_emission_factors, stage_name):
        """Calculate the impact for a given stage and sampled emission factors."""
        # Assuming `sampled_emission_factors` is a list of SampledEmissionFactor objects
        if stage_name == "A1":
            stage_a1 = StageA1(
                name="Stage A1",
                emission_factors=sampled_emission_factors,
                materials=layer.materials
            )
            ## surfaceArea, density and thickness are only important for the design option calculations
            impact_data = stage_a1.calculate_stage_impact(surfaceArea=1, density=1, thickness=1)
            return A1Result(
                gwp_total=impact_data['gwp-total'],
                gwp_fossil=impact_data['gwp-fossil'],
                gwp_biogenic=impact_data['gwp-biogenic'],
                gwp_luluc=impact_data['gwp-luluc']
            )
        elif stage_name == "A2":
            stage_a2 = StageA2(
                name="Stage A2",
                emission_factors=sampled_emission_factors,
                materials=layer.materials
            )
            impact_data = stage_a2.calculate_stage_impact(fuel_consumption_rate=0.359, actual_load=22000.0, load_capacity=22000.0, empty_return_rate=1, surfaceArea=1, density=1, thickness=1)
            return A2Result(
                gwp_total=impact_data['gwp-total'],
                gwp_fossil=impact_data['gwp-fossil'],
                gwp_biogenic=impact_data['gwp-biogenic'],
                gwp_luluc=impact_data['gwp-luluc']
            )
        elif stage_name == "A3":
            stage_a3 = StageA3(
                name="Stage A3",
                emission_factors=sampled_emission_factors,
                energy_consumption=layer.energy_consumption_a3,
                energy_type=layer.energy_used_a3
            )
            impact_data = stage_a3.calculate_stage_impact(surfaceArea=1, density=1, thickness=1)
            return A3Result(
                gwp_total=impact_data['gwp-total'],
                gwp_fossil=impact_data['gwp-fossil'],
                gwp_biogenic=impact_data['gwp-biogenic'],
                gwp_luluc=impact_data['gwp-luluc']
            )
        elif stage_name == "A4":
            stage_a4 = StageA4(
                name="Stage A4",
                emission_factors=sampled_emission_factors,
                transport_distance=layer.transport_distance_a4
            )
            impact_data = stage_a4.calculate_stage_impact(fuel_consumption_rate=0.359, actual_load=22000.0, load_capacity=22000.0, empty_return_rate=1, surfaceArea=1, density=1, thickness=1)
            return A4Result(
                gwp_total=impact_data['gwp-total'],
                gwp_fossil=impact_data['gwp-fossil'],
                gwp_biogenic=impact_data['gwp-biogenic'],
                gwp_luluc=impact_data['gwp-luluc']
            )
        elif stage_name == "A5":
            stage_a5 = StageA5(
                name="Stage A5",
                emission_factors=sampled_emission_factors,
                equipments=layer.construction_a5
            )
            impact_data = stage_a5.calculate_stage_impact(equipments=layer.construction_a5, surfaceArea=1, density=1, thickness=1)
            return A5Result(
                gwp_total=impact_data['gwp-total'],
                gwp_fossil=impact_data['gwp-fossil'],
                gwp_biogenic=impact_data['gwp-biogenic'],
                gwp_luluc=impact_data['gwp-luluc']
            )
        else:
            raise ValueError(f"Unknown stage: {stage_name}")
