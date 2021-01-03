import pathlib

from pandora.core_types import Nominal
from pandora.core_fields import COUNTRY, COUNTRY_CODE_NUMERIC, COUNTRY_CODE, COUNTRY_CODE3

LOCATION = f"{pathlib.Path(__file__).parent.absolute()}/country_code.csv"

FIELDS = {
    COUNTRY_CODE: Nominal(),
    COUNTRY_CODE3: Nominal(),
    COUNTRY: Nominal(),
    COUNTRY_CODE_NUMERIC: Nominal(),
}
