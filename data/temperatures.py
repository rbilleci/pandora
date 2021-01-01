import pathlib

from pandora.types import Numeric, DataSource, Nominal, Imputation, Date
from pandora.imputers import *
from pandora.constants import *

LOCATION = f"{pathlib.Path(__file__).parent.absolute()}/temperatures.csv"

imputations = [
    Imputation(impute_with_mean, [QUARTER, YEAR, REGION, COUNTRY]),
    Imputation(impute_with_mean, [QUARTER, REGION, COUNTRY]),
    Imputation(impute_with_mean, [QUARTER, YEAR, COUNTRY]),
    Imputation(impute_with_mean, [QUARTER, COUNTRY]),
    Imputation(impute_with_mean, [YEAR, COUNTRY]),
    Imputation(impute_with_mean, [COUNTRY]),
    Imputation(impute_with_mean, [QUARTER, YEAR]),
    Imputation(impute_with_mean, [QUARTER]),
    Imputation(impute_with_mean, [])
]

TEMPERATURE = 'temperature'
SPECIFIC_HUMIDITY = 'specific_humidity'

data_source = DataSource(LOCATION, [
    Nominal(COUNTRY),
    Nominal(REGION),
    Date(DATE),
    Numeric(TEMPERATURE, 0.0, 500, imputations=imputations),
    Numeric(SPECIFIC_HUMIDITY, 0.0, 0.10, imputations=imputations)
])
