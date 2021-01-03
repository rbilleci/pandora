from logging import info, basicConfig, INFO
import pandas as pd
import datetime
from data import geo_iso, country_working_day
from data.country_working_day import WORKING_DAY
from data.geo_iso import COUNTRY_CODE
from pandora.core_fields import DATE
from workalendar.registry import registry

basicConfig(level=INFO, format='%(asctime)s\t%(levelname)s\t%(filename)s\t%(message)s')


def update(start_date, end_date):
    info(f"updating working days information for {start_date} to {end_date}")

    # get the unique list of countries
    df = pd.DataFrame({COUNTRY_CODE: pd.read_csv(geo_iso.LOCATION)[COUNTRY_CODE].unique()})

    # generate the series of dates for the time range,
    # then explode the dataset so there is one row per date per country
    datetime_index = pd.date_range(start_date, end_date, freq='D')
    df[DATE] = df.applymap(lambda r: datetime_index)
    df = df.explode(DATE, ignore_index=True).reset_index(0, drop=True)

    # calculate the working dates per country
    df = df.groupby(COUNTRY_CODE).apply(update_for_country_code).reset_index(drop=True)

    # persist the CSV
    df.to_csv(country_working_day.LOCATION, index=False)


def update_for_country_code(group: pd.DataFrame):
    working_registry = registry.get(group.name)
    if working_registry is None:
        info(f"no calendar found for {group.name}")
    else:
        working_registry = working_registry()
        group[WORKING_DAY] = group[DATE].apply(working_registry.is_working_day)
        group[WORKING_DAY] = group[WORKING_DAY].map(lambda v: 1.0 if v else 0.0 if not v else None)
    return group


update(datetime.date(2020, 1, 1), datetime.date(2021, 12, 31))