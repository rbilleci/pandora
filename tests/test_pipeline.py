import unittest
from datetime import date
from logging import INFO, basicConfig, info

import numpy as np
import pandas as pd
from category_encoders import BinaryEncoder
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import StandardScaler

from data import country_code, geo, continent, age_distribution, population, temperatures, oxford_data, working_day
from data.age_distribution import AGE_DISTRIBUTION_1, AGE_DISTRIBUTION_2, AGE_DISTRIBUTION_3, AGE_DISTRIBUTION_4, \
    AGE_DISTRIBUTION_5
from data.continent import CONTINENT
from data.oxford_data import CONFIRMED_CASES, C1, C2, C3, C4, C5, C6, C7, C8, H1, H2, H3, H6
from data.population import POPULATION, POPULATION_DENSITY, OBESITY_RATE, POPULATION_PERCENT_URBAN, \
    PNEUMONIA_DEATHS_PER_100K, GDP_PER_CAPITA
from data.temperatures import SPECIFIC_HUMIDITY, TEMPERATURE
from data.working_day import WORKING_DAY
from pandora import loader, imputer
from pandora.core_fields import COUNTRY_CODE, REGION, DATE, DAY_OF_WEEK, DAY_OF_MONTH, DAY_OF_YEAR, MONTH, QUARTER, YEAR

basicConfig(level=INFO, format='%(asctime)s\t%(levelname)s\t%(filename)s\t%(message)s')

pd.options.display.max_columns = None
pd.options.display.max_rows = None
pd.options.display.max_info_columns = 1000


class PipelineTestCase(unittest.TestCase):

    def test_sklearn_pipeline(self):
        # load the dataset
        start_date = date(2020, 1, 1)
        end_date = date(2020, 12, 31)
        df, schema = loader.load(start_date,
                                 end_date,
                                 geo,
                                 [
                                     country_code,
                                     continent,
                                     population,
                                     age_distribution,
                                     temperatures,
                                     oxford_data,
                                     working_day,
                                 ])
        # impute
        df, schema = imputer.impute(df, schema)

        # derive the label columns, and move new cases to the front
        info('calculating label')
        df = df.groupby([COUNTRY_CODE, REGION]).apply(self.determine_new_cases).reset_index(drop=True)
        df = transform_column_order(df)
        df.info()

        # create the pipeline
        info('creating pipeline')
        pipeline = Pipeline([
            ('features', FeatureUnion([
                # geographic location
                nominal(CONTINENT),
                nominal(COUNTRY_CODE),
                nominal(REGION),
                # case information
                numeric(CONFIRMED_CASES),
                # non-pharmaceutical interventions
                numeric(C1),
                numeric(C2),
                numeric(C3),
                numeric(C4),
                numeric(C5),
                numeric(C6),
                numeric(C7),
                numeric(C8),
                numeric(H1),
                numeric(H2),
                numeric(H3),
                numeric(H6),
                # country and regional information
                numeric(AGE_DISTRIBUTION_1),
                numeric(AGE_DISTRIBUTION_2),
                numeric(AGE_DISTRIBUTION_3),
                numeric(AGE_DISTRIBUTION_4),
                numeric(AGE_DISTRIBUTION_5),
                numeric(GDP_PER_CAPITA),
                numeric(OBESITY_RATE),
                numeric(POPULATION),
                numeric(POPULATION_DENSITY),
                numeric(POPULATION_PERCENT_URBAN),
                numeric(PNEUMONIA_DEATHS_PER_100K),
                numeric(SPECIFIC_HUMIDITY),
                numeric(TEMPERATURE),
                numeric(WORKING_DAY),
                # date/time fields
                numeric(DATE),
                numeric(DAY_OF_MONTH),
                numeric(DAY_OF_WEEK),
                numeric(DAY_OF_YEAR),
                numeric(MONTH),
                numeric(QUARTER),
                numeric(YEAR)
            ])),
            ('logistic', LogisticRegression(max_iter=10000, tol=0.1))
        ])

        info('getting train/val/test split')
        train, val, test = split(df, 30, 1)
        train_x, train_y, validation_x, validation_y, test_x, test_y = (train.iloc[:, 1:], train.iloc[:, :1],
                                                                        val.iloc[:, 1:], val.iloc[:, :1],

                                                                        test.iloc[:, 1:], test.iloc[:, :1])
        info('fitting pipeline')

        # split our dataset
        parameters = {'logistic__C': np.logspace(-4, 4, 4)}
        grid = GridSearchCV(pipeline, param_grid=parameters, cv=5, verbose=1)
        grid.fit(train_x, train_y.values.ravel())

        print("score = %3.2f" % (grid.score(validation_x, validation_y)))

        """
        pipeline.fit(train_x, train_y)
        info('predicting validation')
        predictions = pipeline.predict(validation_x)
        info('generating error')
        mse0 = (np.square(predictions - validation_y)).mean(axis=0)
        mse1 = (np.square(predictions - validation_y)).mean(axis=1)
        mse2 = (np.square(predictions - validation_y)).mean(axis=2)
        print(mse0)
        print(mse1)
        print(mse2)
        """

    @staticmethod
    def determine_new_cases(grouped):
        grouped['new_cases'] = grouped[CONFIRMED_CASES].copy()
        grouped['new_cases'] = grouped['new_cases'].diff(-1).fillna(0.0).apply(lambda x: max(0, -x))
        return grouped


def numeric(name: str):
    return (name, Pipeline([
        (name + '.select', DataFrameSelector([name])),
        (name + '.scale', StandardScaler())
    ]))


def nominal(name: str):
    return (name, Pipeline([
        (name + '.select', DataFrameSelector([name])),
        (name + '.scale', BinaryEncoder())
    ]))


def split(df: pd.DataFrame, days_for_validation: int, days_for_test: int) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame):
    # First, sort the data by date
    df = df.sort_values(DATE)

    # Determine the maximum date
    date_start_test = df[DATE].max() - pd.to_timedelta(days_for_test - 1, unit='d')
    date_start_validation = date_start_test - pd.to_timedelta(days_for_validation, unit='d')

    df_train = df[df[DATE] < date_start_validation]
    df_validation = df[(df[DATE] >= date_start_validation) & (df[DATE] < date_start_test)]
    df_test = df[df[DATE] >= date_start_test]

    # Debug the outpoint
    info(f"Training Range:   {df_train[DATE].min().date()} - {df_train[DATE].max().date()}")
    info(f"Validation Range: {df_validation[DATE].min().date()} - {df_validation[DATE].max().date()}")
    info(f"Test Range:       {df_test[DATE].min().date()} - {df_test[DATE].max().date()}")

    # Sanity Check
    if len(df.index) != len(df_train.index) + len(df_validation.index) + len(df_test.index):
        raise Exception('entries do not add up')

    return df_train, df_validation, df_test


def transform_column_order(df: pd.DataFrame) -> pd.DataFrame:
    df = df.reindex(sorted(df.columns), axis=1)  # Sort columns by name
    df_label = df['new_cases']
    df = df.drop(labels=['new_cases'], axis=1)
    df.insert(0, 'new_cases', df_label)
    return df


class DataFrameSelector(BaseEstimator, TransformerMixin):
    def __init__(self, attribute_names):
        self.attribute_names = attribute_names

    def fit(self, x, y=None):
        return self

    def transform(self, x):
        return x[self.attribute_names]
