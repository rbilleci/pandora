import pathlib

from pandora.core_types import Nominal
from pandora.core_fields import COUNTRY

COUNTRY_CODE_NUMERIC = 'country_code_numeric'
COUNTRY_CODE = 'country_code'
COUNTRY_CODE3 = 'country_code3'
LOCATION = f"{pathlib.Path(__file__).parent.absolute()}/geo_iso.csv"

FIELDS = {
    COUNTRY: Nominal(),
    COUNTRY_CODE_NUMERIC: Nominal(),
    COUNTRY_CODE: Nominal(),
    COUNTRY_CODE3: Nominal()
}
