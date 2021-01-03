import pathlib

from data.country_code import COUNTRY_CODE
from pandora.core_fields import DAY_OF_WEEK, DATE, DAY_OF_YEAR
from pandora.core_types import Imputation, Nominal, Numeric, Date
from pandora.imputers import impute_with_median

LOCATION = f"{pathlib.Path(__file__).parent.absolute()}/working_day.csv"
WORKING_DAY = 'working_day'

FIELDS = {
    COUNTRY_CODE: Nominal(),
    DATE: Date(),
    WORKING_DAY: Numeric(minimum=0, maximum=1, imputations=[
        Imputation(impute_with_median, [DATE]),
        Imputation(impute_with_median, [DAY_OF_YEAR]),
        Imputation(impute_with_median, [DAY_OF_WEEK]),
    ])
}
