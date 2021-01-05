import pathlib

from pandora.core_fields import REGION_NAME, QUARTER, YEAR, COUNTRY_NAME
from pandora.core_types import Module, Imputation
from pandora.imputers import impute_with_mean

TEMPERATURE = 'temperature'
SPECIFIC_HUMIDITY = 'specific_humidity'

IMPUTATION_STRATEGY = [
    Imputation(impute_with_mean, [QUARTER, YEAR, REGION_NAME, COUNTRY_NAME]),
    Imputation(impute_with_mean, [QUARTER, REGION_NAME, COUNTRY_NAME]),
    Imputation(impute_with_mean, [QUARTER, YEAR, COUNTRY_NAME]),
    Imputation(impute_with_mean, [QUARTER, COUNTRY_NAME]),
    Imputation(impute_with_mean, [YEAR, COUNTRY_NAME]),
    Imputation(impute_with_mean, [COUNTRY_NAME]),
    Imputation(impute_with_mean, [QUARTER, YEAR]),
    Imputation(impute_with_mean, [QUARTER]),
    Imputation(impute_with_mean, [])
]

module = Module(
    f"{pathlib.Path(__file__).parent.absolute()}/temperatures.csv",
    {
        TEMPERATURE: IMPUTATION_STRATEGY,
        SPECIFIC_HUMIDITY: IMPUTATION_STRATEGY
    })
