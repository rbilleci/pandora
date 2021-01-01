import pathlib

from pandora.core_types import Nominal
from pandora.core_fields import COUNTRY

CONTINENT = 'continent_name'
LOCATION = f"{pathlib.Path(__file__).parent.absolute()}/geo_continent.csv"

FIELDS = {
    COUNTRY: Nominal(),
    CONTINENT: Nominal()
}
