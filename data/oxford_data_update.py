import os
import pathlib
import re
import urllib.request
from datetime import datetime
from logging import info

import pandas as pd

from pandora.core_fields import COUNTRY_NAME, REGION_NAME, DATE
from data.oxford_data import LOCATION, FILE, CONFIRMED_CASES, \
    C1, C2, C3, C4, C5, C6, C7, C8, H1, H2, H3, H6, CONFIRMED_DEATHS

EXTERNAL_LOCATION = "https://github.com/OxCGRT/covid-policy-tracker/raw/master/data/OxCGRT_latest.csv"
LOCATION_FOR_PREPROCESSING = f"{pathlib.Path(__file__).parent.absolute()}/{FILE}.tmp"
ACCEPTED_COLUMNS = [COUNTRY_NAME, REGION_NAME, DATE,
                    CONFIRMED_CASES, CONFIRMED_DEATHS,
                    C1, C2, C3, C4, C5, C6, C7, C8,
                    H1, H2, H3, H6]


def update():
    info('download oxford data set')
    urllib.request.urlretrieve(EXTERNAL_LOCATION, LOCATION_FOR_PREPROCESSING)
    df = pd.read_csv(LOCATION_FOR_PREPROCESSING,
                     parse_dates=['Date'],
                     date_parser=lambda value: datetime.strptime(value, "%Y%m%d").date(),
                     keep_default_na=False)
    df.columns = map(rename_column, df.columns)
    df = df.drop([column for column in df if column not in ACCEPTED_COLUMNS], axis=1)
    df.to_csv(LOCATION, index=False)
    os.remove(LOCATION_FOR_PREPROCESSING)


def rename_column(name: str) -> str:
    # concerts to snake_case
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    name = name.replace(' ', '_').replace('__', '_').lower()
    return name


update()
