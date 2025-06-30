from dataclasses import dataclass
from typing import List, Optional

@dataclass
class EmissionFactor:
    material: str
    mean_total: float
    mean_fossil: float
    mean_biogenic: float
    mean_luluc: float
    cov: float
    unit: str

@dataclass
class SampledEmissionFactor:
    material: str
    mean_total: float
    mean_fossil: float
    mean_biogenic: float
    mean_luluc: float
    unit: str


@dataclass
class LayerType:
    name: str
    thickness: float                # in m
    quantity: float                 # in t
    density: float                  # in t/m3


@dataclass
class DesignOption:
    name: str
    layer: List[LayerType]


@dataclass
class Material:
    name: str
    composition: float              # in fraction (e.g., 0.3318)
    transport_distance_a2: float    # in km for transport A2
    mass_a2: float                  # in kg for transport A2

@dataclass
class Equipment:
    name: str
    number: int                 # number of equipments
    productivity: float         # in t/h or m2/h
    productivity_unit: str
    energy_type: str            # diesel, electricity, ...
    energy: float               # in L/h or kWh/h
    energy_unit: str            # L/h or kWh/h


@dataclass
class Layer:
    name: str
    abbreviation: str
    materials: List[Material]
    energy_used_a3: str 
    energy_consumption_a3: float            # in MJ/t
    transport_distance_a4: float            # in km
    mass_a4: float                          # in tons
    construction_a5: List[Equipment]        
    quantity_a5_ton: float                  # in tons
    quantity_a5_m2: float                   # in m2
    density: Optional[float]                # in t/m3
    thickness: Optional[float]              # in m

@dataclass
class LifeCycleStage:
    name: str
    emission_factors: List[EmissionFactor] | List[SampledEmissionFactor] # List of EmissionFactor or SampledEmissionFactor instances

    def get_emission_factor(self, material_name: str) -> Optional[EmissionFactor]:
        """ Retrieve the emission factor for a specific material by name. """
        for ef in self.emission_factors:
            if isinstance(ef, str):  # Check if ef is a string
                if ef.lower() == material_name.lower():  # Case-insensitive comparison for string
                    return ef
            elif isinstance(ef, EmissionFactor):  # Check if ef is an instance of EmissionFactor
                if ef.material.lower() == material_name.lower():  # Case-insensitive comparison for material name
                    return ef
            elif isinstance(ef, SampledEmissionFactor):
                if ef.material.lower() == material_name.lower():
                    return ef
        return None

@dataclass
class StageA1(LifeCycleStage):
    materials: List[Material]  # List of Material instances

    def calculate_stage_impact(self, surfaceArea: float, density: float, thickness: float):
        total_impact = {
            "gwp-total": 0,
            "gwp-fossil": 0,
            "gwp-biogenic": 0,
            "gwp-luluc": 0,
        }
        for material in self.materials:
            ef = self.get_emission_factor(material.name)
            if ef:
                total_impact["gwp-total"] += material.composition * ef.mean_total * surfaceArea * density * thickness
                total_impact["gwp-fossil"] += material.composition * ef.mean_fossil * surfaceArea * density * thickness
                total_impact["gwp-biogenic"] += material.composition * ef.mean_biogenic * surfaceArea * density * thickness
                total_impact["gwp-luluc"] += material.composition * ef.mean_luluc * surfaceArea * density * thickness
        return total_impact

@dataclass
class StageA2(LifeCycleStage):
    materials: List[Material]  # List of Material instances

    def calculate_stage_impact(self, fuel_consumption_rate: float, actual_load: float, load_capacity: float, empty_return_rate: float, surfaceArea: float, density: float, thickness: float):
        total_impact = {
            "gwp-total": 0,
            "gwp-fossil": 0,
            "gwp-biogenic": 0,
            "gwp-luluc": 0,
        }
        for material in self.materials:
            mass_diesel = (
                fuel_consumption_rate * material.transport_distance_a2 *
                (1/3 * (actual_load/load_capacity) + 2/3 + 2/3 * empty_return_rate) *
                ((material.mass_a2) / load_capacity)
            )
            ef = self.get_emission_factor("diesel")  # Always search for diesel
            if ef:
                total_impact["gwp-total"] += mass_diesel * ef.mean_total*(surfaceArea * density * thickness)
                total_impact["gwp-fossil"] += mass_diesel * ef.mean_fossil*(surfaceArea * density * thickness)
                total_impact["gwp-biogenic"] += mass_diesel * ef.mean_biogenic*(surfaceArea * density * thickness)
                total_impact["gwp-luluc"] += mass_diesel * ef.mean_luluc*(surfaceArea * density * thickness)
        return total_impact

@dataclass
class StageA3(LifeCycleStage):
    energy_consumption: float   # Energy consumption in kWh/t
    energy_type: str            # Energy type used (e.g., "thermal_energy", "electricity")

    def calculate_stage_impact(self, surfaceArea: float, density: float, thickness: float):
        ef = self.get_emission_factor(self.energy_type)
        if ef:
            total_impact = {
                "gwp-total": ef.mean_total * self.energy_consumption * surfaceArea * density * thickness,
                "gwp-fossil": ef.mean_fossil * self.energy_consumption * surfaceArea * density * thickness,
                "gwp-biogenic": ef.mean_biogenic * self.energy_consumption * surfaceArea * density * thickness,
                "gwp-luluc": ef.mean_luluc * self.energy_consumption * surfaceArea * density * thickness,
            }
            return total_impact
        return None  # or return 0 for all categories if no factor is found

@dataclass
class StageA4(LifeCycleStage):
    transport_distance: float   # Transport distance for manufactured material to site (km)

    def calculate_stage_impact(self, fuel_consumption_rate: float, actual_load: float, load_capacity: float, empty_return_rate: float, surfaceArea: float, density: float, thickness: float):
        mass_diesel = (
            fuel_consumption_rate * self.transport_distance *
            (1/3 * (actual_load / load_capacity) + 2/3 + 2/3 * empty_return_rate) *
            ((surfaceArea*density*thickness*1000) / load_capacity)
        )
        ef = self.get_emission_factor("diesel")  # Always search for diesel
        if ef:
            total_impact = {
                "gwp-total": mass_diesel * ef.mean_total,
                "gwp-fossil": mass_diesel * ef.mean_fossil,
                "gwp-biogenic": mass_diesel * ef.mean_biogenic,
                "gwp-luluc": mass_diesel * ef.mean_luluc,
            }
            return total_impact
        return None  # or return 0 for all categories if no factor is found

@dataclass
class StageA5(LifeCycleStage): 
    equipments: List[Equipment]                

    def calculate_stage_impact(self, equipments: List[Equipment], surfaceArea: float, density: float, thickness: float):
        # Iterate over the equipments in the DesignOption
        for equipment in equipments:
            # Get the appropriate emission factor based on the energy type of the equipment
            ef = self.get_emission_factor_for_equipment(equipment.energy_type) 
            if ef:
                # Select the correct quantity based on the productivity unit
                if equipment.productivity_unit == "t/h":
                    quantity = surfaceArea*density*thickness  # Quantity in tons
                elif equipment.productivity_unit == "m2/h":
                    quantity = surfaceArea # Quantity in m²
                elif equipment.productivity_unit == "m3/h":
                    quantity = surfaceArea*thickness
                else:
                    raise ValueError(f"Unsupported productivity unit: {equipment.productivity_unit}")
            
            number = equipment.number
            if ef:
                total_impact = {
                    "gwp-total": ef.mean_total * (equipment.energy / (equipment.productivity*number)) * quantity,
                    "gwp-fossil": ef.mean_fossil * (equipment.energy / (equipment.productivity*number)) * quantity,
                    "gwp-biogenic": ef.mean_biogenic * (equipment.energy / (equipment.productivity*number)) * quantity,
                    "gwp-luluc": ef.mean_luluc * (equipment.energy / (equipment.productivity*number)) * quantity,
                }
                return total_impact
            return None  # or return 0 for all categories if no factor is found
        
    def get_emission_factor_for_equipment(self, energy_type: str) -> Optional[EmissionFactor]:
        """ Retrieve the emission factor for a specific energy type (e.g., diesel, electricity). """
        for ef in self.emission_factors:
            if isinstance(ef, EmissionFactor) and ef.material == energy_type:
                return ef
            elif isinstance(ef, SampledEmissionFactor) and ef.material == energy_type:
                return ef
        return None
