import unittest
from datetime import date
from logging import basicConfig, INFO

import data.age_distribution as age_dist
import data.oxford_data as oxford
import data.population as population
import data.temperatures as temperatures
from data import geo, geo_continent, geo_iso
from pandora import loader

basicConfig(level=INFO, format='%(asctime)s\t%(levelname)s\t%(filename)s\t%(message)s')


class DataLoaderTestCase(unittest.TestCase):

    def test_loader(self):
        start_date = date(2020, 1, 1)
        end_date = date(2021, 12, 31)
        df, schema = loader.load(start_date, end_date, geo,
                                 [geo_continent,
                                  geo_iso,
                                  population,
                                  age_dist,
                                  temperatures,
                                  oxford])
        df.info()
        for name in schema:
            print(name)
