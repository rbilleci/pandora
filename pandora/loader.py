from datetime import datetime
from logging import info
from typing import Optional, Dict

import pandas as pd

from data.country_code import COUNTRY_CODE
from pandora.core_fields import COUNTRY, REGION, WEEK, MONTH, QUARTER, YEAR, DAY_OF_MONTH, DAY_OF_WEEK, \
    DAY_OF_YEAR, DATE, CORE_FIELDS, COUNTRY_CODE3
from pandora.core_types import Numeric, Ordinal, Nominal, Boolean, Date, Field


def load(start_date: datetime.date,
         end_date: datetime.date,
         geos: {},
         data_sources: [{}]) -> (pd.DataFrame, Dict[str, Field]):
    info('loading geos and expanding to time range')
    datetime_index = pd.date_range(start_date, end_date, freq='D')
    df = expand(load_source(geos), datetime_index)
    schema = {**CORE_FIELDS, **geos.FIELDS, }

    info('adding date fields')
    df[WEEK] = df[DATE].map(lambda x: x.isocalendar()[1])
    df[MONTH] = df[DATE].map(lambda x: x.month)
    df[QUARTER] = df[DATE].map(lambda x: x.quarter)
    df[YEAR] = df[DATE].map(lambda x: x.year)
    df[DAY_OF_YEAR] = df[DATE].map(lambda x: x.timetuple().tm_yday)
    df[DAY_OF_MONTH] = df[DATE].map(lambda x: x.timetuple().tm_mday)
    df[DAY_OF_WEEK] = df[DATE].map(lambda x: x.weekday() + 1)

    info('merging data files')
    for data_source in data_sources:
        df, schema = merge(df, schema, data_source, datetime_index)

    info('reindexing')
    df = df.reindex(sorted(df.columns), axis=1)
    return df, schema


def merge(df: pd.DataFrame,
          schema: Dict[str, Field],
          data_source: {},
          datetime_index: pd.DatetimeIndex) -> (pd.DataFrame, Dict[str, Field]):
    info(f"merging {data_source.LOCATION}")
    df_new = expand(load_source(data_source), datetime_index)
    df_merge_keys = list({resolve_country_key(df_new),
                          resolve_region_key(df_new),
                          DATE}.intersection(df_new))
    df = df.merge(df_new,
                  on=df_merge_keys,
                  how="left",
                  suffixes=[None, '_R'],
                  copy=False)
    for name in df.columns:
        if name.endswith('_R'):
            df = df.drop(name, axis=1)
    return df, {**data_source.FIELDS, **schema}


def load_source(source: {}) -> pd.DataFrame:
    df = pd.read_csv(source.LOCATION,
                     usecols=source.FIELDS,
                     keep_default_na=False,
                     error_bad_lines=True,
                     memory_map=True,
                     low_memory=False)
    for name, field in source.FIELDS.items():
        df.attrs[f"@{name}"] = field
        if isinstance(field, Numeric):
            df[name] = pd.to_numeric(df[name])
        elif isinstance(field, Ordinal):
            df[name] = pd.to_numeric(df[name]).astype('Int64')  # nullable
        elif isinstance(field, Nominal):
            df[name] = df[name].astype('str')
        elif isinstance(field, Boolean):
            df[name] = df[name].astype('boolean')  # nullable
        elif isinstance(field, Date):
            df[name] = pd.to_datetime(df[name])
        else:
            raise KeyError(name)
    return df


def expand(df: pd.DataFrame,
           datetime_index: pd.DatetimeIndex) -> pd.DataFrame:
    if DATE in df.columns:
        return df
    else:
        query = resolve_expansion_conditions(df)
        if query:
            df[DATE] = df.apply(lambda r: datetime_index[pd.eval(query)], axis=1)
        else:
            df[DATE] = df.apply(lambda r: datetime_index, axis=1)
        return df.explode(DATE, ignore_index=True).reset_index(0, drop=True)


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


def resolve_country_key(df: pd.DataFrame) -> Optional[str]:
    if COUNTRY_CODE in df.columns:
        return COUNTRY_CODE
    elif COUNTRY_CODE3 in df.columns:
        return COUNTRY_CODE3
    elif COUNTRY in df.columns:
        return COUNTRY
    else:
        return None


def resolve_region_key(df: pd.DataFrame) -> Optional[str]:
    if REGION in df.columns:
        return REGION
    else:
        return None
