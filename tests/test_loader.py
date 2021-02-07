import unittest
from datetime import date
from logging import basicConfig, INFO

import pandas as pd

import pandora.data.age_distribution as age_dist
import pandora.data.oxford_data as oxford
import pandora.data.population as population
import pandora.data.temperatures as temperatures
from pandora.data import geo, continent, country_code, working_day
from pandora import loader
from pandora.core_fields import DATE, COUNTRY_CODE

basicConfig(level=INFO, format='%(asctime)s\t%(levelname)s\t%(filename)s\t%(message)s')

pd.options.display.max_columns = None
pd.options.display.max_rows = None
pd.options.display.max_info_columns = 1000


class LoaderTestCase(unittest.TestCase):

    def test_loader(self):
        start_date = date(2020, 1, 1)
        end_date = date(2020, 12, 31)
        imputation_window_start_date = date(2020, 1, 1)
        imputation_window_end_date = date(2020, 12, 31)
        df = loader.load(start_date,
                         end_date,
                         imputation_window_start_date,
                         imputation_window_end_date,
                         geo.module,
                         [
                             country_code.module,
                             continent.module,
                             population.module,
                             age_dist.module,
                             temperatures.module,
                             oxford.module,
                             working_day.module
                         ])
        # verify the date merging worked properly, for the given date range
        self.assertEqual(df[DATE].min(), start_date)
        self.assertEqual(df[DATE].max(), end_date)
        df.info()

    def test_start_date_before_actual_data(self):
        start_date = date(2018, 1, 10)
        end_date = date(2018, 1, 11)
        imputation_window_start_date = date(2020, 1, 1)
        imputation_window_end_date = date(2020, 1, 8)
        df = loader.load(start_date,
                         end_date,
                         imputation_window_start_date,
                         imputation_window_end_date,
                         geo.module,
                         [
                             country_code.module,
                             working_day.module
                         ])
        df.info()
        print(df[[COUNTRY_CODE, DATE]].head(10))
        # verify the date merging worked properly, for the given date range
        self.assertEqual(df[DATE].min(), start_date)
        self.assertEqual(df[DATE].max(), end_date)

    def test_start_date_before_expansion_window(self):
        start_date = date(2020, 1, 10)
        end_date = date(2020, 1, 11)
        imputation_window_start_date = date(2020, 2, 1)
        imputation_window_end_date = date(2020, 12, 31)
        df = loader.load(start_date,
                         end_date,
                         imputation_window_start_date,
                         imputation_window_end_date,
                         geo.module,
                         [
                             country_code.module,
                             working_day.module
                         ])
        df.info()
        print(df[[COUNTRY_CODE, DATE]].head(10))
        # verify the date merging worked properly, for the given date range
        self.assertEqual(df[DATE].min(), start_date)
        self.assertEqual(df[DATE].max(), end_date)

    def test_end_date_after_expansion_window(self):
        start_date = date(2020, 1, 10)
        end_date = date(2020, 1, 11)
        imputation_window_start_date = date(2020, 1, 1)
        imputation_window_end_date = date(2020, 1, 8)
        df = loader.load(start_date,
                         end_date,
                         imputation_window_start_date,
                         imputation_window_end_date,
                         geo.module,
                         [
                             country_code.module,
                             working_day.module
                         ])
        df.info()
        print(df[[COUNTRY_CODE, DATE]].head(10))
        # verify the date merging worked properly, for the given date range
        self.assertEqual(df[DATE].min(), start_date)
        self.assertEqual(df[DATE].max(), end_date)
