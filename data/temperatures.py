import pathlib

from pandora.core_fields import COUNTRY, REGION, DATE, QUARTER, YEAR, COUNTRY_CODE
from pandora.imputers import impute_with_mean
from pandora.core_types import Numeric, Imputation, Nominal, Date

imputations = [
    Imputation(impute_with_mean, [QUARTER, YEAR, REGION, COUNTRY_CODE]),
    Imputation(impute_with_mean, [QUARTER, REGION, COUNTRY_CODE]),
    Imputation(impute_with_mean, [QUARTER, YEAR, COUNTRY_CODE]),
    Imputation(impute_with_mean, [QUARTER, COUNTRY_CODE]),
    Imputation(impute_with_mean, [YEAR, COUNTRY_CODE]),
    Imputation(impute_with_mean, [COUNTRY_CODE]),
    Imputation(impute_with_mean, [QUARTER, YEAR]),
    Imputation(impute_with_mean, [QUARTER]),
    Imputation(impute_with_mean, [])
]

TEMPERATURE = 'temperature'
SPECIFIC_HUMIDITY = 'specific_humidity'

FIELDS = {
    COUNTRY: Nominal(),
    REGION: Nominal(),
    DATE: Date(),
    TEMPERATURE: Numeric(0.0, 500.0, imputations=imputations),
    SPECIFIC_HUMIDITY: Numeric(0.0, 0.10, imputations=imputations)
}

LOCATION = f"{pathlib.Path(__file__).parent.absolute()}/temperatures.csv"
