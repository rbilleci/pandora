import pathlib

from pandora.core_fields import REGION_NAME, COUNTRY_NAME
from pandora.core_types import Module, Imputation
from pandora.imputers import impute_with_forward_fill, impute_with_zero

CONFIRMED_CASES = 'confirmed_cases'
CONFIRMED_DEATHS = 'confirmed_deaths'
C1 = 'c1_school_closing'
C2 = 'c2_workplace_closing'
C3 = 'c3_cancel_public_events'
C4 = 'c4_restrictions_on_gatherings'
C5 = 'c5_close_public_transport'
C6 = 'c6_stay_at_home_requirements'
C7 = 'c7_restrictions_on_internal_movement'
C8 = 'c8_international_travel_controls'
H1 = 'h1_public_information_campaigns'
H2 = 'h2_testing_policy'
H3 = 'h3_contact_tracing'
H6 = 'h6_facial_coverings'

GEO_IMPUTATION_STRATEGY = [
    Imputation(impute_with_forward_fill, [REGION_NAME, COUNTRY_NAME])
]

NPI_IMPUTATION_STRATEGY = [
    Imputation(impute_with_forward_fill, [REGION_NAME, COUNTRY_NAME]),
    Imputation(impute_with_forward_fill, [COUNTRY_NAME]),
    Imputation(impute_with_zero, [])
]

FILE = "oxford_data.csv"
LOCATION = f"{pathlib.Path(__file__).parent.absolute()}/{FILE}"

module = Module(
    LOCATION,
    imputations={
        CONFIRMED_CASES: GEO_IMPUTATION_STRATEGY,
        CONFIRMED_DEATHS: GEO_IMPUTATION_STRATEGY,
        C1: NPI_IMPUTATION_STRATEGY,
        C2: NPI_IMPUTATION_STRATEGY,
        C3: NPI_IMPUTATION_STRATEGY,
        C4: NPI_IMPUTATION_STRATEGY,
        C5: NPI_IMPUTATION_STRATEGY,
        C6: NPI_IMPUTATION_STRATEGY,
        C7: NPI_IMPUTATION_STRATEGY,
        C8: NPI_IMPUTATION_STRATEGY,
        H1: NPI_IMPUTATION_STRATEGY,
        H2: NPI_IMPUTATION_STRATEGY,
        H3: NPI_IMPUTATION_STRATEGY,
        H6: NPI_IMPUTATION_STRATEGY,
    },
    mark_missing=[CONFIRMED_CASES])
