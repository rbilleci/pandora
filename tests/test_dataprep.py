from datetime import date
from logging import basicConfig, INFO

import pandas as pd

import unittest
import data.age_distribution as age_dist
import data.oxford_data as oxford
import data.population as population
import data.temperatures as temperatures
from pandora import dataprep
from pandora.core_types import Data
from data import geo, geo_continent

basicConfig(level=INFO, format='%(asctime)s\t%(levelname)s\t%(filename)s\t%(message)s')


class DataPrepTestCase(unittest.TestCase):

    def test_dataprep(self):
        self.assertTrue(True)
        start_date = date(2020, 1, 1)
        end_date = date(2021, 6, 30)

        data = Data(start_date,
                    end_date,
                    geo.data_source,
                    [
                        geo_continent.data_source,
                        population.data_source,
                        age_dist.data_source,
                        temperatures.data_source,
                        oxford.data_source
                    ])

        pd.options.display.max_columns = None
        pd.options.display.max_rows = None
        pd.options.display.max_info_columns = 1000

        dataprep.clean(data)
        df = data.df

        df.info()
