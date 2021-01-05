from calendar import monthrange, isleap

GEO_CODE = 'geo_code'
COUNTRY_NAME = 'country_name'
COUNTRY_CODE_NUMERIC = 'country_code_numeric'
COUNTRY_CODE = 'country_code'
COUNTRY_CODE3 = 'country_code3'
REGION_NAME = 'region_name'
DATE = 'date'
YEAR = 'year'
QUARTER = 'quarter'
MONTH = 'month'
WEEK = 'week'
DAY_OF_WEEK = 'day_of_week'
DAY_OF_MONTH = 'day_of_month'
DAY_OF_YEAR = 'day_of_year'

MISSING_INDICATOR_SUFFIX = '--'


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
