import pathlib

from pandora.core_types import Nominal
from pandora.core_fields import COUNTRY

ISO_3166_NUMERIC = 'iso_3166_numeric'
ISO_3166_2 = 'iso_3166_2'
ISO_3166_3 = 'iso_3166_3'
LOCATION = f"{pathlib.Path(__file__).parent.absolute()}/geo_iso.csv"

FIELDS = {
    COUNTRY: Nominal(),
    ISO_3166_NUMERIC: Nominal(),
    ISO_3166_2: Nominal(),
    ISO_3166_3: Nominal()
}
