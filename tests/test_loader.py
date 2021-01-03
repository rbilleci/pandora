import unittest
from datetime import date
from logging import basicConfig, INFO

import pandas as pd

import data.age_distribution as age_dist
import data.oxford_data as oxford
import data.population as population
import data.temperatures as temperatures
from data import geo, continent, country_code, working_day
from pandora import loader
from pandora.core_fields import DATE, QUARTER, MONTH, WEEK, DAY_OF_MONTH

basicConfig(level=INFO, format='%(asctime)s\t%(levelname)s\t%(filename)s\t%(message)s')

pd.options.display.max_columns = None
pd.options.display.max_rows = None
pd.options.display.max_info_columns = 1000


class LoaderTestCase(unittest.TestCase):

    def test_loader(self):
        start_date = date(2020, 1, 1)
        end_date = date(2020, 1, 31)
        df, schema = loader.load(start_date, end_date,
                                 geo,
                                 [
                                     country_code,
                                     continent,
                                     population,
                                     age_dist,
                                     temperatures,
                                     oxford,
                                     working_day
                                 ])
        # verify the date merging worked properly, for the given date range
        self.assertEqual(df[DATE].min(), start_date)
        self.assertEqual(df[DATE].max(), end_date)
        self.assertEqual(df[QUARTER].min(), 1)
        self.assertEqual(df[QUARTER].max(), 1)
        self.assertEqual(df[MONTH].min(), 1)
        self.assertEqual(df[MONTH].max(), 1)
        self.assertEqual(df[WEEK].min(), 1)
        self.assertEqual(df[WEEK].max(), 5)
        self.assertEqual(df[DAY_OF_MONTH].min(), 1)
        self.assertEqual(df[DAY_OF_MONTH].max(), 31)
        df.info()
