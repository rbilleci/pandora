import pathlib

from pandora.core_types import Nominal, DataSource
from pandora.core_fields import *

CONTINENT = 'continent_name'
LOCATION = f"{pathlib.Path(__file__).parent.absolute()}/geo_continent.csv"

data_source = DataSource(LOCATION, [
    Nominal(COUNTRY),
    Nominal(CONTINENT)
])
