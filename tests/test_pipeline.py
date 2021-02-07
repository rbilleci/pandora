import unittest
from datetime import date
from logging import INFO, basicConfig, info

import pandas as pd
from category_encoders import BinaryEncoder
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.linear_model import SGDRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import StandardScaler

from pandora.data import country_code, geo, continent, age_distribution, population, temperatures, oxford_data, \
    working_day
from pandora.data.age_distribution import AGE_DISTRIBUTION_1, AGE_DISTRIBUTION_2, AGE_DISTRIBUTION_3, \
    AGE_DISTRIBUTION_4, \
    AGE_DISTRIBUTION_5
from pandora.data.continent import CONTINENT
from pandora.data.oxford_data import CONFIRMED_CASES, C1, C2, C3, C4, C5, C6, C7, C8, H1, H2, H3, H6
from pandora.data.population import POPULATION, POPULATION_DENSITY, OBESITY_RATE, POPULATION_PERCENT_URBAN, \
    PNEUMONIA_DEATHS_PER_100K, GDP_PER_CAPITA
from pandora.data.temperatures import SPECIFIC_HUMIDITY, TEMPERATURE
from pandora.data.working_day import WORKING_DAY
from pandora import loader
from pandora.core_fields import COUNTRY_CODE, DATE, DAY_OF_WEEK, DAY_OF_YEAR, GEO_CODE

basicConfig(level=INFO, format='%(asctime)s\t%(levelname)s\t%(filename)s\t%(message)s')

pd.options.display.max_columns = None
pd.options.display.max_rows = None
pd.options.display.max_info_columns = 1000

import warnings

warnings.filterwarnings('ignore', category=FutureWarning)  # ignore FutureWarning from scikit learn

PREDICTED_NEW_CASES = 'new_cases'


class PipelineTestCase(unittest.TestCase):

    def test_sklearn_pipeline(self):
        # load the dataset
        start_date = date(2020, 1, 1)
        end_date = date(2021, 1, 3)
        imputation_window_start_date = date(2019, 1, 1)
        imputation_window_end_date = end_date
        df = loader.load(start_date,
                         end_date,
                         imputation_window_start_date,
                         imputation_window_end_date,
                         geo.module,
                         [
                             country_code.module,
                             continent.module,
                             population.module,
                             age_distribution.module,
                             temperatures.module,
                             oxford_data.module,
                             working_day.module
                         ])

        # derive the label columns, and move new cases to the front
        info('calculating label')
        df = df.groupby(GEO_CODE).apply(self.determine_new_cases).reset_index(drop=True)
        df = df.groupby(GEO_CODE).apply(lambda group: group_add_ma_a(group, PREDICTED_NEW_CASES)).reset_index(drop=True)
        df = df.groupby(GEO_CODE).apply(lambda group: group_add_ma_b(group, PREDICTED_NEW_CASES)).reset_index(drop=True)
        df = df.groupby(GEO_CODE).apply(lambda group: group_add_ma_c(group, PREDICTED_NEW_CASES)).reset_index(drop=True)
        df = df.groupby(GEO_CODE).apply(lambda group: group_add_ma_a(group, CONFIRMED_CASES)).reset_index(drop=True)
        df = df.groupby(GEO_CODE).apply(lambda group: group_add_ma_b(group, CONFIRMED_CASES)).reset_index(drop=True)
        df = df.groupby(GEO_CODE).apply(lambda group: group_add_ma_c(group, CONFIRMED_CASES)).reset_index(drop=True)
        df = df.groupby(GEO_CODE).apply(lambda group: add_working_day_tomorrow(group)).reset_index(drop=True)
        df = df.groupby(GEO_CODE).apply(lambda group: add_working_day_yesterday(group)).reset_index(drop=True)

        # move the label to the front
        df = transform_column_order(df)

        # create the pipeline
        info('creating pipeline')
        pipeline = Pipeline([
            ('features', FeatureUnion([
                # geographic location
                nominal(CONTINENT),
                nominal(COUNTRY_CODE),
                # it is important to have the geo code, to help distinguish from different countries with no regions,
                # otherwise, if we only use a region code, all countries have the same 0 value. This way, we do not
                # need to rely on the algorithm determining this from the combo of country + region. we make it explicit
                nominal(GEO_CODE),
                # case information
                numeric(PREDICTED_NEW_CASES + SUFFIX_MA_A),
                numeric(PREDICTED_NEW_CASES + SUFFIX_MA_B),
                numeric(PREDICTED_NEW_CASES + SUFFIX_MA_C),
                numeric(CONFIRMED_CASES),
                numeric(CONFIRMED_CASES + SUFFIX_MA_A),
                numeric(CONFIRMED_CASES + SUFFIX_MA_B),
                numeric(CONFIRMED_CASES + SUFFIX_MA_C),
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
                numeric(WORKING_DAY + '_tomorrow'),
                numeric(WORKING_DAY + '_yesterday'),
                # date/time fields
                # numeric(DATE),
                # numeric(DAY_OF_MONTH),
                nominal(DAY_OF_WEEK),
                numeric(DAY_OF_YEAR),
                # numeric(WEEK),
                # numeric(MONTH),
                # numeric(QUARTER),
                # numeric(YEAR)
            ])),
            ('estimator', SGDRegressor(max_iter=10000,
                                       early_stopping=True,
                                       n_iter_no_change=2000,
                                       shuffle=True))
        ])

        info('getting train/val/test split')
        train, val, test = split(df, 30, 1)
        train_x, train_y, validation_x, validation_y, test_x, test_y = (train.iloc[:, 1:], train.iloc[:, :1],
                                                                        val.iloc[:, 1:], val.iloc[:, :1],
                                                                        test.iloc[:, 1:], test.iloc[:, :1])

        # split our dataset
        """
        Best so far:
            -1009.1139305621175
            {'estimator__alpha': 0.0004, 'estimator__epsilon': 0.0075, 
            'estimator__learning_rate': 'adaptive', 'estimator__loss': 'squared_epsilon_insensitive'}
        """
        parameters = {
            'estimator__alpha': [0.0003, 0.0004, 0.0006],
            'estimator__epsilon': [0.004, 0.008, 0.017],
            'estimator__loss': ['huber', 'squared_epsilon_insensitive'],
            # ['squared_loss', 'huber', 'epsilon_insensitive', 'squared_epsilon_insensitive'],
            'estimator__learning_rate': ['invscaling', 'adaptive']  # ['invscaling', 'adaptive', 'optimal', 'constant']
        }
        grid = GridSearchCV(pipeline,
                            param_grid=parameters,
                            cv=5,
                            scoring='neg_root_mean_squared_error',
                            n_jobs=10,
                            verbose=10)
        grid.fit(train_x, train_y.values.ravel())
        print("score A = %3.2f" % (grid.score(validation_x, validation_y.values.ravel())))
        print("score C = %3.2f" % (grid.best_estimator_.score(validation_x, validation_y.values.ravel())))
        print(grid.best_score_)
        print(grid.best_params_)

    @staticmethod
    def determine_new_cases(grouped):
        grouped[PREDICTED_NEW_CASES] = grouped[CONFIRMED_CASES].copy()
        grouped[PREDICTED_NEW_CASES] = grouped[PREDICTED_NEW_CASES].diff(-1).fillna(0.0).apply(lambda x: max(0, -x))
        return grouped

    @staticmethod
    def determine_moving_averages(grouped):
        grouped[PREDICTED_NEW_CASES] = grouped[CONFIRMED_CASES].copy()
        grouped[PREDICTED_NEW_CASES] = grouped[PREDICTED_NEW_CASES].diff(-1).fillna(0.0).apply(lambda x: max(0, -x))
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
    df_label = df[PREDICTED_NEW_CASES]
    df = df.drop(labels=[PREDICTED_NEW_CASES], axis=1)
    df.insert(0, PREDICTED_NEW_CASES, df_label)
    return df


class DataFrameSelector(BaseEstimator, TransformerMixin):
    def __init__(self, attribute_names):
        self.attribute_names = attribute_names

    def fit(self, x, y=None):
        return self

    def transform(self, x):
        return x[self.attribute_names]


MA_WINDOW_A = 3
MA_WINDOW_B = 7
MA_WINDOW_C = 21
SUFFIX_MA_A = '_MA_A'
SUFFIX_MA_B = '_MA_B'
SUFFIX_MA_C = '_MA_C'


def group_add_ma_a(grouped, name: str):
    return group_add_ma_n(grouped, name, SUFFIX_MA_A, MA_WINDOW_A)


def group_add_ma_b(grouped, name: str):
    return group_add_ma_n(grouped, name, SUFFIX_MA_B, MA_WINDOW_B)


def group_add_ma_c(grouped, name: str):
    return group_add_ma_n(grouped, name, SUFFIX_MA_C, MA_WINDOW_C)


def group_add_ma_n(grouped, name: str, suffix: str, window: int):
    name_ma = name + suffix
    # shift by 1 so we look only at past days
    # NOTE: the shift is also important so we don't include today's predicted data in the value
    grouped[name_ma] = grouped[name].copy().shift(1).bfill().ffill()  # NOTE copy is needed?
    grouped[name_ma] = grouped[name_ma].rolling(window=window, min_periods=1).mean().bfill().ffill()
    return grouped


def add_working_day_tomorrow(grouped):
    grouped[WORKING_DAY + '_tomorrow'] = grouped[WORKING_DAY].copy().shift(-1).bfill().ffill()  # NOTE copy is needed?
    return grouped


def add_working_day_yesterday(grouped):
    grouped[WORKING_DAY + '_yesterday'] = grouped[WORKING_DAY].copy().shift(1).bfill().ffill()  # NOTE copy is needed?
    return grouped
