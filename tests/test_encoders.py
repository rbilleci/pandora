import unittest
from datetime import date
from logging import basicConfig, INFO

import pandas as pd

import data.population as population
from data import geo, geo_iso
from pandora import imputer, loader, encoders
from pandora.core_fields import COUNTRY, DAY_OF_WEEK

basicConfig(level=INFO, format='%(asctime)s\t%(levelname)s\t%(filename)s\t%(message)s')

pd.options.display.max_columns = None
pd.options.display.max_rows = None
pd.options.display.max_info_columns = 1000


class EncoderTestCase(unittest.TestCase):

    def test_hash_encode(self):
        df, schema = loader.load(date(2020, 1, 1),
                                 date(2020, 3, 1),
                                 geo,
                                 [geo_iso, population])
        df, schema = imputer.impute(df, schema)
        df, schema = encoders.hash_encode(df, schema, COUNTRY, 8)
        self.assertIn(f"{COUNTRY}_hash_0", df.columns)
        self.assertIn(f"{COUNTRY}_hash_0", schema)
        df.info()

    def test_cyclical_encode(self):
        df, schema = loader.load(date(2020, 1, 1),
                                 date(2020, 3, 1),
                                 geo,
                                 [geo_iso, population])
        df, schema = imputer.impute(df, schema)
        df, schema = encoders.cyclical_encode(df, schema, DAY_OF_WEEK, lambda x: x, 7)
        self.assertIn(f"{DAY_OF_WEEK}_sin", schema)
        self.assertIn(f"{DAY_OF_WEEK}_cos", schema)
        self.assertIn(f"{DAY_OF_WEEK}_sin", df.columns)
        self.assertIn(f"{DAY_OF_WEEK}_cos", df.columns)

    def test_one_hot_encode(self):
        df, schema = loader.load(date(2020, 1, 1),
                                 date(2020, 3, 1),
                                 geo,
                                 [geo_iso, population])
        df, schema = imputer.impute(df, schema)
        df, schema = encoders.one_hot_encode(df, schema, COUNTRY)
        self.assertIn(f"{COUNTRY}_ohe_Germany", df.columns)
        self.assertIn(f"{COUNTRY}_ohe_Germany", schema)
        df.info()

    def test_binary_encoder(self):
        df, schema = loader.load(date(2020, 1, 1),
                                 date(2020, 3, 1),
                                 geo,
                                 [geo_iso, population])
        df, schema = imputer.impute(df, schema)
        df, schema = encoders.binary_encode(df, schema, COUNTRY)
        self.assertIn(f"{COUNTRY}_bin_0", df.columns)
        self.assertIn(f"{COUNTRY}_bin_0", schema)

    def test_sum_encoder(self):
        df, schema = loader.load(date(2020, 1, 1),
                                 date(2020, 12, 31),
                                 geo,
                                 [geo_iso, population])
        df, schema = imputer.impute(df, schema)
        df, schema = encoders.sum_encode(df, schema, COUNTRY)
        self.assertIn(f"{COUNTRY}_sum_0", df.columns)
        self.assertIn(f"{COUNTRY}_sum_0", schema)

    def test_backward_difference_encode(self):
        df, schema = loader.load(date(2020, 1, 1),
                                 date(2020, 3, 1),
                                 geo,
                                 [geo_iso, population])
        df, schema = imputer.impute(df, schema)
        df, schema = encoders.backward_difference_encode(df, schema, COUNTRY)
        self.assertIn(f"{COUNTRY}_bde_0", df.columns)
        self.assertIn(f"{COUNTRY}_bde_0", schema)

    def test_base_n_encode(self):
        df, schema = loader.load(date(2020, 1, 1),
                                 date(2020, 3, 1),
                                 geo,
                                 [geo_iso, population])
        df, schema = imputer.impute(df, schema)
        df, schema = encoders.base_n_encode(df, schema, COUNTRY, 8)
        self.assertIn(f"{COUNTRY}_base_n_0", df.columns)
        self.assertIn(f"{COUNTRY}_base_n_0", schema)

    def test_helmert_contrast_encode(self):
        df, schema = loader.load(date(2020, 1, 1),
                                 date(2020, 3, 1),
                                 geo,
                                 [geo_iso, population])
        df, schema = imputer.impute(df, schema)
        df, schema = encoders.helmert_contrast_encode(df, schema, COUNTRY)
        self.assertIn(f"{COUNTRY}_helmert_0", df.columns)
        self.assertIn(f"{COUNTRY}_helmert_0", schema)

    def test_polynomial_encode(self):
        df, schema = loader.load(date(2020, 1, 1),
                                 date(2020, 3, 1),
                                 geo,
                                 [geo_iso, population])
        df, schema = imputer.impute(df, schema)
        df, schema = encoders.polynomial_encode(df, schema, COUNTRY)
        self.assertIn(f"{COUNTRY}_poly_0", df.columns)
        self.assertIn(f"{COUNTRY}_poly_0", schema)

    def test_bloom_filter_encode(self):
        df, schema = loader.load(date(2020, 1, 1),
                                 date(2020, 3, 1),
                                 geo,
                                 [geo_iso, population])
        df, schema = imputer.impute(df, schema)
        df, schema = encoders.bloom_filter_encode(df, schema, COUNTRY, 3, 31)
        self.assertIn(f"{COUNTRY}_bloom_0", df.columns)
        self.assertIn(f"{COUNTRY}_bloom_0", schema)
