import pathlib

from pandora.core_fields import DAY_OF_WEEK, DATE, DAY_OF_YEAR
from pandora.core_types import Module, Imputation
from pandora.imputers import impute_with_median

WORKING_DAY = 'working_day'

module = Module(
    location=f"{pathlib.Path(__file__).parent.absolute()}/working_day.csv",
    imputations={
        WORKING_DAY: [
            Imputation(impute_with_median, [DATE]),
            Imputation(impute_with_median, [DAY_OF_YEAR]),
            Imputation(impute_with_median, [DAY_OF_WEEK]),
        ]
    },
    mark_missing=[WORKING_DAY])
