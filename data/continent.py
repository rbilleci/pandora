import pathlib

from pandora.core_types import Nominal
from pandora.core_fields import COUNTRY

CONTINENT = 'continent'
LOCATION = f"{pathlib.Path(__file__).parent.absolute()}/continent.csv"

FIELDS = {
    COUNTRY: Nominal(),
    CONTINENT: Nominal()
}
