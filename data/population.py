import pathlib

from pandora.core_fields import REGION_NAME, YEAR, COUNTRY_NAME
from pandora.core_types import Module, Imputation
from pandora.imputers import impute_with_mean, impute_with_max

POPULATION = 'population'
POPULATION_DENSITY = 'population_density'
POPULATION_PERCENT_URBAN = 'population_percent_urban'
GDP_PER_CAPITA = 'gdp_per_capita'
OBESITY_RATE = 'obesity_rate'
PNEUMONIA_DEATHS_PER_100K = 'pneumonia_deaths_per_100k'

module = Module(
    f"{pathlib.Path(__file__).parent.absolute()}/population.csv",
    imputations={
        POPULATION: [
            Imputation(impute_with_max, [REGION_NAME, COUNTRY_NAME])
            # fallback to max population for the same country and region

        ],
        POPULATION_DENSITY: [
            Imputation(impute_with_max, [REGION_NAME, COUNTRY_NAME]),  # fallback to max for the same country and region
            Imputation(impute_with_max, [COUNTRY_NAME]),  # fallback to max for the same country
            Imputation(impute_with_mean, [YEAR]),  # fallback to the max population density globally, for the year
            Imputation(impute_with_mean, [])  # fallback to the average population density globally, for all years
        ],
        POPULATION_PERCENT_URBAN: [
            Imputation(impute_with_max, [REGION_NAME, COUNTRY_NAME]),  # fallback to max for the same country and region
            Imputation(impute_with_max, [COUNTRY_NAME]),  # fallback to max for the same country
            Imputation(impute_with_mean, [YEAR]),  # fallback to the mean for the year
            Imputation(impute_with_mean, [])  # fallback to the mean across all years
        ],
        GDP_PER_CAPITA: [
            Imputation(impute_with_max, [REGION_NAME, COUNTRY_NAME]),  # fallback to max for the same country and region
            Imputation(impute_with_max, [COUNTRY_NAME]),  # fallback to max for the same country
            Imputation(impute_with_mean, [YEAR]),  # fallback to the mean for the year
            Imputation(impute_with_mean, [])  # fallback to the mean across all years
        ],
        OBESITY_RATE: [
            Imputation(impute_with_mean, [REGION_NAME, COUNTRY_NAME]),  # fallback to average
            Imputation(impute_with_mean, [COUNTRY_NAME]),  # fallback to average for the same country
            Imputation(impute_with_mean, [YEAR]),  # fallback to the mean for the year
            Imputation(impute_with_mean, [])  # fallback to the mean across all years
        ],
        PNEUMONIA_DEATHS_PER_100K: [
            Imputation(impute_with_mean, [REGION_NAME, COUNTRY_NAME]),  # fallback to average
            Imputation(impute_with_mean, [COUNTRY_NAME]),  # fallback to average for the same country
            Imputation(impute_with_mean, [YEAR]),  # fallback to the mean for the year
            Imputation(impute_with_mean, [])  # fallback to the mean across all years
        ]
    },
    mark_missing=[POPULATION,
                  POPULATION_DENSITY,
                  POPULATION_PERCENT_URBAN,
                  GDP_PER_CAPITA,
                  OBESITY_RATE,
                  PNEUMONIA_DEATHS_PER_100K])
