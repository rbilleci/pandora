from datetime import datetime
from logging import info
from typing import Optional

import pandas as pd

from pandora.core_fields import COUNTRY_CODE, COUNTRY_CODE3, COUNTRY_NAME, REGION_NAME, WEEK, MONTH, QUARTER, YEAR, \
    DAY_OF_MONTH, DAY_OF_WEEK, DAY_OF_YEAR, DATE, GEO_CODE, COUNTRY_CODE_NUMERIC
from pandora.core_types import Module
from pandora.imputer import impute


def load(start_date: datetime.date,
         end_date: datetime.date,
         geo_module: Module,
         modules: [Module]) -> pd.DataFrame:
    datetime_index = pd.date_range(start_date, end_date, freq='D')
    df = load_module(geo_module, datetime_index)
    df = apply_geo_code_feature(df)
    df = merge_modules(df, modules, datetime_index)
    df = df.reindex(sorted(df.columns), axis=1)
    validate(df)
    return df


def merge_modules(df: pd.DataFrame,
                  modules: [Module],
                  datetime_index) -> pd.DataFrame:
    for module in modules:
        df = merge_module(df, module, datetime_index)
    return df


def merge_module(df: pd.DataFrame,
                 module: Module,
                 datetime_index: pd.DatetimeIndex) -> pd.DataFrame:
    # Modules may have date ranges outside of the datetime index we are evaluating.
    # Since imputing of missing values may benefit from the additional time range, we perform
    # an **outer** merge, run the imputations, then trim the records by time, after the imputation
    df_new = load_module(module, datetime_index)
    df = df.merge(df_new, on=resolve_merge_keys(df_new), how="outer", suffixes=[None, '_R'])

    # Strip additional columns from the  merge
    for name in df.columns:
        if name.endswith('_R'):
            df = df.drop(name, axis=1)

    # Perform the imputation, then strip any records outside of the datetime_index,
    df = impute(df, module)
    df = df[df[DATE].isin(datetime_index)]

    # then strip out any countries or regions not in the dataset, remaining from the merge
    df = df[~df[COUNTRY_CODE].isnull()]
    df = df[~df[REGION_NAME].isnull()]
    return df


def load_module(module: Module,
                datetime_index: pd.DatetimeIndex) -> pd.DataFrame:
    info(f"{module.location} - loading")
    df = pd.read_csv(module.location, keep_default_na=False, na_values='')
    df = apply_key_imputations(df)
    df = apply_datetime_expansion(df, datetime_index)
    df = apply_datetime_features(df)
    return df


def apply_datetime_expansion(df: pd.DataFrame,
                             datetime_index: pd.DatetimeIndex) -> pd.DataFrame:
    if DATE not in df.columns:
        expansion_conditions = resolve_expansion_conditions(df)
        if expansion_conditions:
            df[DATE] = df.apply(lambda r: datetime_index[pd.eval(expansion_conditions)], axis=1)
        else:
            df[DATE] = df.apply(lambda r: datetime_index, axis=1)
        df = df.explode(DATE, ignore_index=True).reset_index(0, drop=True)
    df[DATE] = pd.to_datetime(df[DATE])
    return df


def apply_key_imputations(df: pd.DataFrame) -> pd.DataFrame:
    if REGION_NAME in df.columns:
        df[REGION_NAME] = df[REGION_NAME].fillna('')
    return df


def apply_geo_code_feature(df: pd.DataFrame) -> pd.DataFrame:
    df[GEO_CODE] = df[[COUNTRY_CODE, REGION_NAME]].apply(
        lambda x: x[COUNTRY_CODE] if x[REGION_NAME] == '' else (x[COUNTRY_CODE] + '/' + x[REGION_NAME]), axis=1)
    return df


def apply_datetime_features(df: pd.DataFrame) -> pd.DataFrame:
    df[WEEK] = df[DATE].map(lambda x: x.isocalendar()[1])
    df[MONTH] = df[DATE].map(lambda x: x.month)
    df[QUARTER] = df[DATE].map(lambda x: x.quarter)
    df[YEAR] = df[DATE].map(lambda x: x.year)
    df[DAY_OF_YEAR] = df[DATE].map(lambda x: x.timetuple().tm_yday)
    df[DAY_OF_MONTH] = df[DATE].map(lambda x: x.timetuple().tm_mday)
    df[DAY_OF_WEEK] = df[DATE].map(lambda x: x.weekday() + 1)
    return df


def resolve_expansion_conditions(df: pd.DataFrame) -> Optional[str]:
    conditions = []
    for name in df.columns:
        if name == YEAR:
            conditions.append('datetime_index.year == r[YEAR]')
        elif name == MONTH:
            conditions.append('datetime_index.month == r[MONTH]')
        elif name == QUARTER:
            conditions.append('datetime_index.quarter == r[QUARTER]')
        elif name == WEEK:
            conditions.append('datetime_index.isocalendar().week == r[WEEK]')
        elif name == DAY_OF_WEEK:
            conditions.append('(datetime_index.day_of_week + 1) == r[DAY_OF_WEEK]')
        elif name == DAY_OF_MONTH:
            conditions.append('datetime_index.timetuple().tm_mday == r[DAY_OF_MONTH]')
        elif name == DAY_OF_YEAR:
            conditions.append('datetime_index.day_of_year == r[DAY_OF_YEAR]')
    if conditions:
        return ' and '.join([condition for condition in conditions])
    else:
        return None


def resolve_merge_keys(df: pd.DataFrame) -> [str]:
    keys = [DATE]
    # add country key
    if COUNTRY_CODE in df.columns:
        keys += [COUNTRY_CODE]
    elif COUNTRY_CODE3 in df.columns:
        keys += [COUNTRY_CODE3]
    elif COUNTRY_CODE_NUMERIC in df.columns:
        keys += [COUNTRY_CODE_NUMERIC]
    elif COUNTRY_NAME in df.columns:
        keys += [COUNTRY_NAME]
    # add region key
    if REGION_NAME in df.columns:
        keys += [REGION_NAME]
    return keys


def validate(df: pd.DataFrame) -> None:
    info(f"validating fields")
    for name in df.columns:
        if df[name].isna().any():
            print(df[[COUNTRY_CODE, COUNTRY_NAME]].tail(10))
            raise ValueError(f"{name} has NA values")
