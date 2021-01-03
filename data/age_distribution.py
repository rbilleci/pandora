import pathlib

from pandora.core_types import Numeric, Nominal, Imputation
from pandora.imputers import impute_with_mean
from pandora.core_fields import COUNTRY_CODE, REGION, YEAR, COUNTRY

imputations = [
    Imputation(impute_with_mean, [YEAR, COUNTRY_CODE]),  # fallback to country average for the year
    Imputation(impute_with_mean, [YEAR]),  # fallback to worldwide average for the year
    Imputation(impute_with_mean, [])  # fallback to worldwide average
]

LOCATION = f"{pathlib.Path(__file__).parent.absolute()}/age_distribution.csv"
AGE_DISTRIBUTION_1 = 'age_distribution_00_04'
AGE_DISTRIBUTION_2 = 'age_distribution_05_14'
AGE_DISTRIBUTION_3 = 'age_distribution_15_34'
AGE_DISTRIBUTION_4 = 'age_distribution_34_64'
AGE_DISTRIBUTION_5 = 'age_distribution_65_plus'

FIELDS = {
    COUNTRY: Nominal(),
    REGION: Nominal(),
    YEAR: Numeric(-1e4, 1e4),
    AGE_DISTRIBUTION_1: Numeric(0.0, 1.0, imputations=imputations),
    AGE_DISTRIBUTION_2: Numeric(0.0, 1.0, imputations=imputations),
    AGE_DISTRIBUTION_3: Numeric(0.0, 1.0, imputations=imputations),
    AGE_DISTRIBUTION_4: Numeric(0.0, 1.0, imputations=imputations),
    AGE_DISTRIBUTION_5: Numeric(0.0, 1.0, imputations=imputations)
}
