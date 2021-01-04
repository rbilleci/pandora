from calendar import monthrange, isleap

from pandora.core_types import Nominal, Date, Numeric

GEO_CODE = 'geo_code'
COUNTRY = 'country'
COUNTRY_CODE_NUMERIC = 'country_code_numeric'
COUNTRY_CODE = 'country_code'
COUNTRY_CODE3 = 'country_code3'
REGION = 'region'
DATE = 'date'
YEAR = 'year'
QUARTER = 'quarter'
MONTH = 'month'
WEEK = 'week'
DAY_OF_WEEK = 'day_of_week'
DAY_OF_MONTH = 'day_of_month'
DAY_OF_YEAR = 'day_of_year'

MISSING_INDICATOR_SUFFIX = '_missing'

CORE_FIELDS = {
    GEO_CODE: Nominal(),
    COUNTRY: Nominal(),
    REGION: Nominal(),
    DATE: Date(),
    YEAR: Numeric(-1e4, 1e4),
    QUARTER: Numeric(1, 4),
    MONTH: Numeric(1, 12),
    WEEK: Numeric(1, lambda row: scale_week_of_year(row)),
    DAY_OF_WEEK: Numeric(1, 7),
    DAY_OF_MONTH: Numeric(1, lambda row: scale_day_of_month(row)),
    DAY_OF_YEAR: Numeric(1, lambda row: scale_day_of_year(row))
}


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
