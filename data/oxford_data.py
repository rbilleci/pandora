import os
import pathlib
import re
import urllib.request
from datetime import datetime

from core_types import Numeric, Ordinal, DataSource, Nominal, Date, Imputation
from core_imputers import *
from core_constants import *

EXTERNAL_LOCATION = "https://github.com/OxCGRT/covid-policy-tracker/raw/master/data/OxCGRT_latest.csv"
FILE = "oxford_data.csv"
LOCATION = f"{pathlib.Path(__file__).parent.absolute()}/{FILE}"
LOCATION_FOR_PREPROCESSING = f"{pathlib.Path(__file__).parent.absolute()}/{FILE}.tmp"

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
ACCEPTED_COLUMNS = [COUNTRY, REGION, DATE, CONFIRMED_CASES, C1, C2, C3, C4, C5, C6, C6, C8, H1, H2, H3, H6]


def update():
    print('download oxford data set')
    urllib.request.urlretrieve(EXTERNAL_LOCATION, LOCATION_FOR_PREPROCESSING)
    df = pd.read_csv(LOCATION_FOR_PREPROCESSING,
                     parse_dates=['Date'],
                     date_parser=lambda value: datetime.strptime(value, "%Y%m%d").date(),
                     keep_default_na=False,
                     memory_map=True,
                     low_memory=False)
    df.columns = map(rename_column, df.columns)
    df = df.drop([column for column in df if column not in ACCEPTED_COLUMNS], axis=1)
    df.to_csv(LOCATION, index=False)
    os.remove(LOCATION_FOR_PREPROCESSING)


def rename_column(name: str) -> str:  # concerts to snake_case
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    name = name.replace(' ', '_').replace('__', '_').lower()
    return name


geo_imputations = [
    Imputation(impute_with_forward_fill, [REGION, COUNTRY])
]

npi_imputations = [
    Imputation(impute_with_forward_fill, [REGION, COUNTRY]),
    Imputation(impute_with_forward_fill, [COUNTRY])
]

data_source = DataSource(LOCATION, [
    Nominal(COUNTRY),
    Nominal(REGION),
    Date(DATE),
    Numeric(CONFIRMED_CASES, 0.0, 2e9, imputations=geo_imputations),
    Numeric(CONFIRMED_DEATHS, 0.0, 1e8, imputations=geo_imputations),
    Ordinal(C1, 0, 3, imputations=npi_imputations),
    Ordinal(C2, 0, 3, imputations=npi_imputations),
    Ordinal(C3, 0, 2, imputations=npi_imputations),
    Ordinal(C4, 0, 4, imputations=npi_imputations),
    Ordinal(C5, 0, 2, imputations=npi_imputations),
    Ordinal(C6, 0, 3, imputations=npi_imputations),
    Ordinal(C7, 0, 2, imputations=npi_imputations),
    Ordinal(C8, 0, 4, imputations=npi_imputations),
    Ordinal(H1, 0, 2, imputations=npi_imputations),
    Ordinal(H2, 0, 3, imputations=npi_imputations),
    Ordinal(H3, 0, 2, imputations=npi_imputations),
    Ordinal(H6, 0, 4, imputations=npi_imputations)
])
