import pathlib

from pandora.core_types import Module

module = Module(f"{pathlib.Path(__file__).parent.absolute()}/country_code.csv")
