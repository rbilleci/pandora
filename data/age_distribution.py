import pathlib

from pandora.core_fields import YEAR, COUNTRY_NAME
from pandora.core_types import Module, Imputation
from pandora.imputers import impute_with_mean

AGE_DISTRIBUTION_1 = 'age_distribution_00_04'
AGE_DISTRIBUTION_2 = 'age_distribution_05_14'
AGE_DISTRIBUTION_3 = 'age_distribution_15_34'
AGE_DISTRIBUTION_4 = 'age_distribution_34_64'
AGE_DISTRIBUTION_5 = 'age_distribution_65_plus'

AGE_DISTRIBUTION_IMPUTATION_STRATEGY = [
    Imputation(impute_with_mean, [YEAR, COUNTRY_NAME]),  # fallback to country average for the year
    Imputation(impute_with_mean, [YEAR]),  # fallback to worldwide average for the year
    Imputation(impute_with_mean, [])  # fallback to worldwide average
]

module = Module(
    f"{pathlib.Path(__file__).parent.absolute()}/age_distribution.csv",
    {
        AGE_DISTRIBUTION_1: AGE_DISTRIBUTION_IMPUTATION_STRATEGY,
        AGE_DISTRIBUTION_2: AGE_DISTRIBUTION_IMPUTATION_STRATEGY,
        AGE_DISTRIBUTION_3: AGE_DISTRIBUTION_IMPUTATION_STRATEGY,
        AGE_DISTRIBUTION_4: AGE_DISTRIBUTION_IMPUTATION_STRATEGY,
        AGE_DISTRIBUTION_5: AGE_DISTRIBUTION_IMPUTATION_STRATEGY
    })
