from dataclasses import dataclass

@dataclass
class Result:
    gwp_total: float
    gwp_fossil: float
    gwp_biogenic: float
    gwp_luluc: float

@dataclass
class A1Result(Result):
    pass

@dataclass
class A2Result(Result):
    pass

@dataclass
class A3Result(Result):
    pass

@dataclass
class A4Result(Result):
    pass

@dataclass
class A5Result(Result):
    pass

@dataclass
class LayerResult:
    name: str
    a1_result: A1Result
    a2_result: A2Result
    a3_result: A3Result
    a4_result: A4Result
    a5_result: A5Result


@dataclass
class DesignOptionResult:
    name: str
    a1_result: A1Result
    a2_result: A2Result
    a3_result: A3Result
    a4_result: A4Result
    a5_result: A5Result