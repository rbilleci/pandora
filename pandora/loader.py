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
         imputation_window_start_date: datetime.date,
         imputation_window_end_date: datetime.date,
         geo_module: Module,
         modules: [Module]) -> pd.DataFrame:
    expansion_window = pd.date_range(min(imputation_window_start_date, start_date),
                                     max(imputation_window_end_date, end_date),
                                     freq='D')
    df = load_module(geo_module, expansion_window)
    df = merge_modules(df, modules, expansion_window)
    df = df[(df[DATE] >= pd.to_datetime(start_date)) & (df[DATE] <= pd.to_datetime(end_date))]
    df = df.sort_values(DATE)
    df = df.reindex(sorted(df.columns), axis=1)
    validate(df)
    return df


def merge_modules(df: pd.DataFrame, modules: [Module], expansion_window) -> pd.DataFrame:
    for module in modules:
        df = merge_module(df, module, expansion_window)
    return df


def merge_module(df: pd.DataFrame, module: Module, expansion_window: pd.DatetimeIndex) -> pd.DataFrame:
    df_new = load_module(module, expansion_window)
    df = df.merge(df_new, on=resolve_merge_keys(df_new), how="left", suffixes=[None, '_R'])
    for name in df.columns:
        if name.endswith('_R'):
            df = df.drop(name, axis=1)
    df = impute(df, module)
    return df


def load_module(module: Module, expansion_window: pd.DatetimeIndex) -> pd.DataFrame:
    info(f"{module.location} - loading")
    df = pd.read_csv(module.location, keep_default_na=False, na_values='')
    df = impute_keys(df)
    df = expand(df, expansion_window)
    return df


def impute_keys(df: pd.DataFrame) -> pd.DataFrame:
    if REGION_NAME in df.columns:
        df[REGION_NAME] = df[REGION_NAME].fillna('')
    if REGION_NAME in df.columns and COUNTRY_CODE in df.columns:
        df[GEO_CODE] = df[[COUNTRY_CODE, REGION_NAME]].apply(
            lambda x: x[COUNTRY_CODE] if x[REGION_NAME] == '' else (x[COUNTRY_CODE] + '/' + x[REGION_NAME]), axis=1)
    return df


def expand(df: pd.DataFrame, expansion_window: pd.DatetimeIndex) -> pd.DataFrame:
    # perform an expansion if there is no date/time column
    if DATE in df.columns:
        df[DATE] = pd.to_datetime(df[DATE])
    else:
        expansion_conditions = resolve_expansion_conditions(df)
        if expansion_conditions:
            df[DATE] = df.apply(lambda r: expansion_window[pd.eval(expansion_conditions,
                                                                   engine='python')], axis=1)
        else:
            df[DATE] = df.apply(lambda r: expansion_window, axis=1)
        df = df.explode(DATE, ignore_index=True).reset_index(0, drop=True)
    # after expanding, add date/time features
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
            conditions.append('expansion_window.year == r[YEAR]')
        elif name == MONTH:
            conditions.append('expansion_window.month == r[MONTH]')
        elif name == QUARTER:
            conditions.append('expansion_window.quarter == r[QUARTER]')
        elif name == WEEK:
            conditions.append('expansion_window.isocalendar().week == r[WEEK]')
        elif name == DAY_OF_WEEK:
            conditions.append('(expansion_window.day_of_week + 1) == r[DAY_OF_WEEK]')
        elif name == DAY_OF_MONTH:
            conditions.append('expansion_window.timetuple().tm_mday == r[DAY_OF_MONTH]')
        elif name == DAY_OF_YEAR:
            conditions.append('expansion_window.day_of_year == r[DAY_OF_YEAR]')
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
