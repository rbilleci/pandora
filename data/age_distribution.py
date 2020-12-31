import pathlib

from dataset import impute_with_mean, Numeric, COUNTRY, YEAR, REGION, DataSource, Nominal, Imputation

imputations = [
    Imputation(impute_with_mean, [YEAR, COUNTRY]),  # fallback to country average for the year
    Imputation(impute_with_mean, [YEAR]),  # fallback to worldwide average for the year
    Imputation(impute_with_mean, [])  # fallback to worldwide average
]

AGE_DISTRIBUTION_1 = 'age_distribution_00_04'
AGE_DISTRIBUTION_2 = 'age_distribution_05_14'
AGE_DISTRIBUTION_3 = 'age_distribution_15_34'
AGE_DISTRIBUTION_4 = 'age_distribution_34_64'
AGE_DISTRIBUTION_5 = 'age_distribution_65_plus'

LOCATION = f"{pathlib.Path(__file__).parent.absolute()}/age_distribution.csv"

data_source = DataSource(LOCATION, [
    Nominal(COUNTRY),
    Nominal(REGION),
    Numeric(AGE_DISTRIBUTION_1, 0.0, 1.0, imputations=imputations),
    Numeric(AGE_DISTRIBUTION_1, 0.0, 1.0, imputations=imputations),
    Numeric(AGE_DISTRIBUTION_2, 0.0, 1.0, imputations=imputations),
    Numeric(AGE_DISTRIBUTION_3, 0.0, 1.0, imputations=imputations),
    Numeric(AGE_DISTRIBUTION_4, 0.0, 1.0, imputations=imputations),
    Numeric(AGE_DISTRIBUTION_5, 0.0, 1.0, imputations=imputations),
])
