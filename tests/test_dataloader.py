import unittest
from datetime import date
from logging import basicConfig, INFO

import data.age_distribution as age_dist
import data.oxford_data as oxford
import data.population as population
import data.temperatures as temperatures
from data import geo, geo_continent
from pandora.core_types import Data

basicConfig(level=INFO, format='%(asctime)s\t%(levelname)s\t%(filename)s\t%(message)s')


class DataLoaderTestCase(unittest.TestCase):

    def test_dataloader(self):
        self.assertTrue(True)
        start_date = date(2020, 1, 1)
        end_date = date(2021, 12, 31)

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
        data.df.info()
