from models.models import EmissionFactor, Material, Layer, Equipment, DesignOption, LayerType
from typing import Dict, List, Tuple

def create_layers(layers_data: Dict) -> List[Layer]:    
    layers = []
    for option in layers_data["layers"]:
        materials = [
            Material(
                material["name"],
                material["composition"],
                material["transport_distance_a2"],
                material["mass_a2"]
            ) for material in option["materials"]
        ]
        layer = Layer(
            option["name"],
            option["abbreviation"],
            materials,
            option["energy_used_a3"], 
            option["energy_consumption_a3"],
            option["transport_distance_a4"],
            option["mass_a4"],
            # Positional arguments first
            construction_a5=[
                Equipment(
                    equipment["name"],
                    equipment["number"],
                    equipment["productivity"],
                    equipment["productivity_unit"],
                    equipment["energy_type"],
                    equipment["energy"],
                    equipment["energy_unit"]
                ) for equipment in option["construction_a5"]
            ],
            # Keyword arguments for the quantity_a5_ton and quantity_a5_m2
            quantity_a5_ton=option["quantity_a5_ton"],
            quantity_a5_m2=option["quantity_a5_m2"],
            density=option["density"],
            thickness=option["thickness"]
        )
        layers.append(layer)
    
    return layers

def create_emission_factors(emission_factors_data: Dict) -> List[EmissionFactor]:
    emission_factors = [
        EmissionFactor(
            item["material"],
            item.get("mean_total", 0.0),
            item.get("mean_fossil", 0.0),
            item.get("mean_biogenic", 0.0),
            item.get("mean_luluc", 0.0),
            item.get("cov", 0.0),
            item["unit"]
        )
        for item in emission_factors_data["emission_factors"]
    ]

    return emission_factors


def create_design_options(layers: List[Layer], design_option_data: Dict) -> List[DesignOption]:
    """Creates design options using provided layers.

    Args:
        layers (List[LayerType]): List of LayerType objects already created.
        design_option_data (Dict): Dictionary with design option structure.

    Returns:
        List[DesignOption]: List of DesignOption objects.
    """
    design_options = []

    for option in design_option_data["design_options"]:
        layer_types = []

        for layer_data in option["layer_type"]:
            # Find the corresponding layer by matching the name
            matching_layer = next((layer for layer in layers if layer.name == layer_data["name"]), None)

            if matching_layer:
                # Create a LayerType instance
                layer_type = LayerType(
                    name=matching_layer.name,
                    thickness=layer_data["thickness"],
                    quantity=layer_data["quantity"],
                    density=layer_data["density"]
                )
                layer_types.append(layer_type)
            else:
                print(f"Warning: Layer '{layer_data['name']}' not found in the provided layers.")

        # Create a DesignOption instance
        design_option = DesignOption(
            name=option["name"],
            layer=layer_types
        )
        design_options.append(design_option)

    return design_options
