import pathlib

from pandora.core_types import Numeric, Nominal, Imputation
from pandora.imputers import impute_with_mean, impute_with_max
from pandora.core_fields import COUNTRY, REGION, YEAR

population_density_imputations = [
    Imputation(impute_with_max, [REGION, COUNTRY]),  # fallback to max for the same country and region
    Imputation(impute_with_max, [COUNTRY]),  # fallback to max for the same country
    Imputation(impute_with_mean, [YEAR]),  # fallback to the max population density globally, for the year
    Imputation(impute_with_mean, [])  # fallback to the average population density globally, for all years
]

population_imputations = [
    Imputation(impute_with_max, [REGION, COUNTRY])  # fallback to max population for the same country and region
]

population_percent_urban_imputations = [
    Imputation(impute_with_max, [REGION, COUNTRY]),  # fallback to max for the same country and region
    Imputation(impute_with_max, [COUNTRY]),  # fallback to max for the same country
    Imputation(impute_with_mean, [YEAR]),  # fallback to the mean for the year
    Imputation(impute_with_mean, [])  # fallback to the mean across all years
]

gdp_per_capita_imputations = [
    Imputation(impute_with_max, [REGION, COUNTRY]),  # fallback to max for the same country and region
    Imputation(impute_with_max, [COUNTRY]),  # fallback to max for the same country
    Imputation(impute_with_mean, [YEAR]),  # fallback to the mean for the year
    Imputation(impute_with_mean, [])  # fallback to the mean across all years
]

obesity_rate_imputations = [
    Imputation(impute_with_mean, [REGION, COUNTRY]),  # fallback to average
    Imputation(impute_with_mean, [COUNTRY]),  # fallback to average for the same country
    Imputation(impute_with_mean, [YEAR]),  # fallback to the mean for the year
    Imputation(impute_with_mean, [])  # fallback to the mean across all years
]

pneumonia_deaths_per_100k_imputations = [
    Imputation(impute_with_mean, [REGION, COUNTRY]),  # fallback to average
    Imputation(impute_with_mean, [COUNTRY]),  # fallback to average for the same country
    Imputation(impute_with_mean, [YEAR]),  # fallback to the mean for the year
    Imputation(impute_with_mean, [])  # fallback to the mean across all years
]

POPULATION = 'population'
POPULATION_DENSITY = 'population_density'
POPULATION_PERCENT_URBAN = 'population_percent_urban'
GDP_PER_CAPITA = 'gdp_per_capita'
OBESITY_RATE = 'obesity_rate'
PNEUMONIA_DEATHS_PER_100K = 'pneumonia_deaths_per_100k'

LOCATION = f"{pathlib.Path(__file__).parent.absolute()}/population.csv"

FIELDS = {
    COUNTRY: Nominal(),
    REGION: Nominal(),
    YEAR: Numeric(-1e4, 1e4),
    POPULATION: Numeric(0.0, 2e9, imputations=population_imputations),
    POPULATION_DENSITY: Numeric(0.0, 1e5, imputations=population_density_imputations),
    POPULATION_PERCENT_URBAN: Numeric(0.0, 100.0, imputations=population_percent_urban_imputations),
    GDP_PER_CAPITA: Numeric(0.0, 1e6, imputations=gdp_per_capita_imputations),
    OBESITY_RATE: Numeric(0.0, 100.0, imputations=obesity_rate_imputations),
    PNEUMONIA_DEATHS_PER_100K: Numeric(0.0, 1e4, imputations=pneumonia_deaths_per_100k_imputations)
}
