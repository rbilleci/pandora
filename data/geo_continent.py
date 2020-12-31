import pathlib

from dataset import Nominal, DataSource, COUNTRY

CONTINENT = 'continent_name'
LOCATION = f"{pathlib.Path(__file__).parent.absolute()}/geo_continent.csv"

data_source = DataSource(LOCATION, [
    Nominal(COUNTRY),
    Nominal(CONTINENT)
])
