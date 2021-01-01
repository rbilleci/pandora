import pathlib
from calendar import monthrange, isleap

from pandora.types import Numeric, DataSource, Nominal, Date
from pandora.constants import *


def scale_week_of_year(row):
    return row[DATE].isocalendar()[1] / 53


def scale_day_of_month(row):
    date = row[DATE]
    days_in_month = monthrange(date.year, date.month)
    return date.day / days_in_month


def scale_day_of_year(row):
    date = row[DATE]
    days_in_year = 366 if isleap(date.year) else 365
    return float(date.timetuple().tm_yday) / float(days_in_year)


LOCATION = f"{pathlib.Path(__file__).parent.absolute()}/geo.csv"

data_source = DataSource(LOCATION, [
    Nominal(GEO_ID),
    Nominal(COUNTRY),
    Nominal(REGION),
    Date(DATE),
    Numeric(YEAR, -1e4, 1e4),
    Numeric(QUARTER, 1, 4),
    Numeric(MONTH, 1, 12),
    Numeric(WEEK, 1, lambda row: scale_week_of_year(row)),
    Numeric(DAY_OF_WEEK, 1, 7),
    Numeric(DAY_OF_MONTH, 1, lambda row: scale_day_of_month(row)),
    Numeric(DAY_OF_YEAR, 1, lambda row: scale_day_of_year(row))
])
