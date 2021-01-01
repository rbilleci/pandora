import pathlib

from pandora.core_fields import *

LOCATION = f"{pathlib.Path(__file__).parent.absolute()}/geo.csv"

FIELDS = {
    COUNTRY: Nominal(),
    REGION: Nominal()
}
