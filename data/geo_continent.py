import pathlib

from pandora.types import Nominal, DataSource
from pandora.constants import *

CONTINENT = 'continent_name'
LOCATION = f"{pathlib.Path(__file__).parent.absolute()}/geo_continent.csv"

data_source = DataSource(LOCATION, [
    Nominal(COUNTRY),
    Nominal(CONTINENT)
])
