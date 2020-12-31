import pathlib

from core_types import Nominal, DataSource
from core_constants import *

CONTINENT = 'continent_name'
LOCATION = f"{pathlib.Path(__file__).parent.absolute()}/geo_continent.csv"

data_source = DataSource(LOCATION, [
    Nominal(COUNTRY),
    Nominal(CONTINENT)
])
