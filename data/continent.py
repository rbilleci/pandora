import pathlib

from pandora.core_types import Module

CONTINENT = 'continent'

module = Module(f"{pathlib.Path(__file__).parent.absolute()}/continent.csv")
