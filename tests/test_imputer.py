from datetime import date
from logging import basicConfig, INFO

import pandas as pd

import unittest
import data.age_distribution as age_dist
import data.oxford_data as oxford
import data.population as population
import data.temperatures as temperatures
from pandora import imputer, loader
from data import geo, continent, country_code, working_day

basicConfig(level=INFO, format='%(asctime)s\t%(levelname)s\t%(filename)s\t%(message)s')

pd.options.display.max_columns = None
pd.options.display.max_rows = None
pd.options.display.max_info_columns = 1000


class ImputerTestCase(unittest.TestCase):

    def test_imputer(self):
        start_date = date(2020, 1, 1)
        end_date = date(2021, 6, 30)
        df, schema = loader.load(start_date,
                                 end_date,
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
        df, schema = imputer.impute(df, schema)
        df.info()
        print(df.describe())
        print(df.isna().any())
