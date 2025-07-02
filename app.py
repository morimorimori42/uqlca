""" application to run the calculations """
from calculator.deterministic_calculator import LCACalculator
from calculator.probabilistic_calculator import (
    ProbabilisticLCACalculator,
)
from calculator.do_probabilistic_lca_calculator import DesignOptionProbabilisticLCACalculator
from general.generate_designs import create_layers, create_design_options, create_emission_factors
from general.load_input import load_data
from general.statistical_results import calculate_statistical_parameters_life_cycle_stages
from visualizations.old_visualizations import plot_overall_lca_distributions
from visualizations.do_visualizations import plot_lca_distributions_by_design_option
from general.save_json import convert_statistical_data_to_json

layers_data, emission_factors_data, design_options_data = load_data(
    "/Users/marlontheis/Desktop/UNIVERSITY/TU_BERLIN/Master_Thesis/master-thesis-project/uncertainty-project/uncertainty-quantification-lca/uqlca/data/layers.json",
    ["/Users/marlontheis/Desktop/UNIVERSITY/TU_BERLIN/Master_Thesis/master-thesis-project/uncertainty-project/uncertainty-quantification-lca/uqlca/data/ecoinvent_background_data.json", "/Users/marlontheis/Desktop/UNIVERSITY/TU_BERLIN/Master_Thesis/master-thesis-project/uncertainty-project/uncertainty-quantification-lca/uqlca/data/national_background_data.json", "/Users/marlontheis/Desktop/UNIVERSITY/TU_BERLIN/Master_Thesis/master-thesis-project/uncertainty-project/uncertainty-quantification-lca/uqlca/data/epd_background_data.json"],
    "/Users/marlontheis/Desktop/UNIVERSITY/TU_BERLIN/Master_Thesis/master-thesis-project/uncertainty-project/uncertainty-quantification-lca/uqlca/data/design_options.json"
)

## Create the instances of layers, design options and emission factors
layers = create_layers(layers_data)
emission_factors_ecoinvent = create_emission_factors(emission_factors_data[0])
emission_factors_national = create_emission_factors(emission_factors_data[1])
emission_factors_epd = create_emission_factors(emission_factors_data[2])
design_options = create_design_options(layers, design_options_data)

## Deterministic LCA on layer level and design option level
deterministic_lca_calculator = LCACalculator(layers, emission_factors_national)
deterministic_lca_calculator.calculate_stage_impacts()
deterministic_layer_results = deterministic_lca_calculator.get_results()
deterministic_design_option_results = deterministic_lca_calculator.calculate_deterministic_lca_design_option(deterministic_layer_results, design_options, length_road=3.39)
# print(deterministic_design_option_results)

## Probabilistic LCA on layer level
probabilistic_lca_calculator = ProbabilisticLCACalculator(layers, emission_factors_ecoinvent)
probabilistic_results = probabilistic_lca_calculator.calculate_probabilistic_impact(n_samples=1000)

## Probabilistic LCA on design option level - ECOINVENT
do_probabilistic_lca_calculator = DesignOptionProbabilisticLCACalculator(layers=layers, emission_factors=emission_factors_ecoinvent, design_options=design_options, length_road=3.390)
db1_probabilistic_results = do_probabilistic_lca_calculator.calculate_do_probabilistic_impact(n_samples=1000)
aggregated_db1_results = do_probabilistic_lca_calculator.collect_aggregated_data(db1_probabilistic_results)
full_db1_results = do_probabilistic_lca_calculator.collect_overall_aggregated_data(db1_probabilistic_results)

## Probabilistic LCA on design option level - NATIONAL
do_probabilistic_lca_calculator = DesignOptionProbabilisticLCACalculator(layers=layers, emission_factors=emission_factors_national, design_options=design_options, length_road=3.390)
db2_probabilistic_results = do_probabilistic_lca_calculator.calculate_do_probabilistic_impact(n_samples=1000)
aggregated_db2_results = do_probabilistic_lca_calculator.collect_aggregated_data(db2_probabilistic_results)
full_db2_results = do_probabilistic_lca_calculator.collect_overall_aggregated_data(db2_probabilistic_results)

## Probabilistic LCA on design option level - EPD
do_probabilistic_lca_calculator = DesignOptionProbabilisticLCACalculator(layers=layers, emission_factors=emission_factors_epd, design_options=design_options, length_road=3.390)
db3_probabilistic_results = do_probabilistic_lca_calculator.calculate_do_probabilistic_impact(n_samples=1000)
aggregated_db3_results = do_probabilistic_lca_calculator.collect_aggregated_data(db3_probabilistic_results)
full_db3_results = do_probabilistic_lca_calculator.collect_overall_aggregated_data(db3_probabilistic_results)

full_results = [full_db1_results, full_db2_results, full_db3_results]
aggregated_results = [aggregated_db1_results, aggregated_db2_results, aggregated_db3_results]

stat_results_ecoinvent = calculate_statistical_parameters_life_cycle_stages(aggregated_db1_results)
stat_results_ecoinvent_json = convert_statistical_data_to_json(stat_results_ecoinvent, "ecoinvent_results.json")
stat_results_national = calculate_statistical_parameters_life_cycle_stages(aggregated_db2_results)
stat_results_national_json = convert_statistical_data_to_json(stat_results_national, "national_results.json")
stat_results_epd = calculate_statistical_parameters_life_cycle_stages(aggregated_db3_results)
stat_results_epd_json = convert_statistical_data_to_json(stat_results_epd, "epd_results.json")

## Visualizations
# plot_lca_distributions_by_design_option(full_results)
# plot_overall_lca_distributions(full_results)
