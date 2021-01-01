import pathlib

from pandora.core_fields import COUNTRY, REGION, DATE
from pandora.imputers import impute_with_forward_fill
from pandora.core_types import Ordinal, Imputation, Numeric, Nominal, Date

FILE = "oxford_data.csv"
LOCATION = f"{pathlib.Path(__file__).parent.absolute()}/{FILE}"

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

geo_imputations = [
    Imputation(impute_with_forward_fill, [REGION, COUNTRY])
]

npi_imputations = [
    Imputation(impute_with_forward_fill, [REGION, COUNTRY]),
    Imputation(impute_with_forward_fill, [COUNTRY])
]

FIELDS = {
    COUNTRY: Nominal(),
    REGION: Nominal(),
    DATE: Date(),
    CONFIRMED_CASES: Numeric(0.0, 2e9, imputations=geo_imputations),
    CONFIRMED_DEATHS: Numeric(0.0, 1e8, imputations=geo_imputations),
    C1: Ordinal(0, 3, imputations=npi_imputations),
    C2: Ordinal(0, 3, imputations=npi_imputations),
    C3: Ordinal(0, 2, imputations=npi_imputations),
    C4: Ordinal(0, 4, imputations=npi_imputations),
    C5: Ordinal(0, 2, imputations=npi_imputations),
    C6: Ordinal(0, 3, imputations=npi_imputations),
    C7: Ordinal(0, 2, imputations=npi_imputations),
    C8: Ordinal(0, 4, imputations=npi_imputations),
    H1: Ordinal(0, 2, imputations=npi_imputations),
    H2: Ordinal(0, 3, imputations=npi_imputations),
    H3: Ordinal(0, 2, imputations=npi_imputations),
    H6: Ordinal(0, 4, imputations=npi_imputations)
}
