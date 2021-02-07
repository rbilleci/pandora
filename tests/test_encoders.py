import unittest
from datetime import date
from logging import basicConfig, INFO

import pandas as pd

import pandora.data.population as population
from pandora.data import geo, country_code
from pandora import imputer, loader, encoders
from pandora.core_fields import COUNTRY_NAME, DAY_OF_WEEK

basicConfig(level=INFO, format='%(asctime)s\t%(levelname)s\t%(filename)s\t%(message)s')

pd.options.display.max_columns = None
pd.options.display.max_rows = None
pd.options.display.max_info_columns = 1000


class EncoderTestCase(unittest.TestCase):

    def test_hash_encode(self):
        df = loader.load(date(2020, 1, 1),
                         date(2020, 3, 1),
                         geo,
                         [country_code, population])
        df = imputer.impute(df)
        df = encoders.HashEncoder(COUNTRY_NAME, 8).fit_transform(df)
        self.assertIn(f"{COUNTRY_NAME}_hash_0", df.columns)
        df.info()

    def test_cyclical_encode(self):
        df = loader.load(date(2020, 1, 1),
                         date(2020, 3, 1),
                         geo,
                         [country_code, population])
        df = imputer.impute(df)
        df[DAY_OF_WEEK] = df[DAY_OF_WEEK] / 7.0
        df = encoders.CyclicalEncoder(DAY_OF_WEEK).fit_transform(df)
        self.assertIn(f"{DAY_OF_WEEK}_sin", df.columns)
        self.assertIn(f"{DAY_OF_WEEK}_cos", df.columns)

    def test_one_hot_encode(self):
        df = loader.load(date(2020, 1, 1),
                         date(2020, 3, 1),
                         geo,
                         [country_code, population])
        df = imputer.impute(df)
        df = encoders.OneHotEncoder(COUNTRY_NAME).fit_transform(df)
        self.assertIn(f"{COUNTRY_NAME}_ohe_Germany", df.columns)
        df.info()

    def test_binary_encoder(self):
        df = loader.load(date(2020, 1, 1),
                         date(2020, 3, 1),
                         geo,
                         [country_code, population])
        df = imputer.impute(df)
        df = encoders.BinaryEncoder(COUNTRY_NAME).fit_transform(df)
        self.assertIn(f"{COUNTRY_NAME}_bin_0", df.columns)

    def test_sum_encoder(self):
        df = loader.load(date(2020, 1, 1),
                         date(2020, 12, 31),
                         geo,
                         [country_code, population])
        df = imputer.impute(df)
        df = encoders.SumEncoder(COUNTRY_NAME).fit_transform(df)
        self.assertIn(f"{COUNTRY_NAME}_sum_0", df.columns)

    def test_backward_difference_encode(self):
        df = loader.load(date(2020, 1, 1),
                         date(2020, 3, 1),
                         geo,
                         [country_code, population])
        df = imputer.impute(df)
        df = encoders.BackwardDifferenceEncoder(COUNTRY_NAME).fit_transform(df)
        self.assertIn(f"{COUNTRY_NAME}_bde_0", df.columns)

    def test_base_n_encode(self):
        df = loader.load(date(2020, 1, 1),
                         date(2020, 3, 1),
                         geo,
                         [country_code, population])
        df = imputer.impute(df)
        df = encoders.BaseNEncoder(COUNTRY_NAME, 8).fit_transform(df)
        self.assertIn(f"{COUNTRY_NAME}_base_n_0", df.columns)

    def test_helmert_contrast_encode(self):
        df = loader.load(date(2020, 1, 1),
                         date(2020, 3, 1),
                         geo,
                         [country_code, population])
        df = imputer.impute(df)
        df = encoders.HelmertContrastEncoder(COUNTRY_NAME).fit_transform(df)
        self.assertIn(f"{COUNTRY_NAME}_helmert_0", df.columns)

    def test_polynomial_encode(self):
        df = loader.load(date(2020, 1, 1),
                         date(2020, 3, 1),
                         geo,
                         [country_code, population])
        df = imputer.impute(df)
        df = encoders.PolynomialEncoder(COUNTRY_NAME).fit_transform(df)
        self.assertIn(f"{COUNTRY_NAME}_poly_0", df.columns)

    def test_bloom_filter_encode(self):
        df = loader.load(date(2020, 1, 1),
                         date(2020, 3, 1),
                         geo,
                         [country_code, population])
        df = imputer.impute(df)
        df = encoders.BloomFilterEncoder(COUNTRY_NAME, 3, 31).fit_transform(df)
        self.assertIn(f"{COUNTRY_NAME}_bloom_0", df.columns)
