from datetime import date
from logging import basicConfig, INFO

import pandas as pd

import unittest
import data.age_distribution as age_dist
import data.oxford_data as oxford
import data.population as population
import data.temperatures as temperatures
from pandora import imputer, loader
from data import geo, geo_continent, geo_iso

basicConfig(level=INFO, format='%(asctime)s\t%(levelname)s\t%(filename)s\t%(message)s')

pd.options.display.max_columns = None
pd.options.display.max_rows = None
pd.options.display.max_info_columns = 1000


class DataPrepTestCase(unittest.TestCase):

    def test_dataprep(self):
        start_date = date(2020, 1, 1)
        end_date = date(2021, 6, 30)
        df, schema = loader.load(start_date,
                                 end_date,
                                 geo,
                                 [geo_continent,
                                  geo_iso,
                                  population,
                                  age_dist,
                                  temperatures,
                                  oxford])
        df, schema = imputer.impute(df, schema)
        df.info()
        print(df.describe())
        print(df.isna().any())
