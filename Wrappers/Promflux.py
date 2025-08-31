from . import PrometheusWrapper, InfluxWrapper
from .RuleParser import Rule

class Promflux:

    def __init__(self,rules: list[Rule], prometheus: PrometheusWrapper, influx: InfluxWrapper):
        self.rules = rules
        self.prometheus = PrometheusWrapper
        self.influx = InfluxWrapper

    def exec():
        pass