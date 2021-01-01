import inspect
from logging import info
from typing import Dict

import pandas as pd

from pandora.core_fields import MISSING_INDICATOR_SUFFIX
from pandora.core_types import Ordinal, Boolean, Imputation, Numeric, Field


def impute(df: pd.DataFrame, schema: Dict[str, Field]) -> (pd.DataFrame, Dict[str, Field]):
    df, schema = mark_missing(df, schema)
    df, schema = impute_df(df, schema)
    df = df.reindex(sorted(df.columns), axis=1)
    coerce_types(df, schema)
    validate(df, schema)
    return df, schema


def mark_missing(df: pd.DataFrame,
                 schema: Dict[str, Field]) -> (pd.DataFrame, Dict[str, Field]):
    for name in df:
        if name in schema and schema[name].mark_missing:
            info(f"marking missing values for column: {name}")
            df[f"{name}{MISSING_INDICATOR_SUFFIX}"] = df[name].isna()
    return df, schema


def impute_df(df: pd.DataFrame,
              schema: Dict[str, Field]) -> (pd.DataFrame, Dict[str, Field]):
    for name in df:
        if name in schema and schema[name].imputations:
            info(f"imputing {name}")
            for imputation in schema[name].imputations:
                if df[name].isna().any():
                    df, schema = impute_df_series(df, schema, name, imputation)
    return df, schema


def impute_df_series(df: pd.DataFrame,
                     schema: Dict[str, Field],
                     name: str,
                     imputation: Imputation) -> (pd.DataFrame, Dict[str, Field]):
    if imputation.keys:
        return df.groupby(imputation.keys).apply(
            lambda group: impute_df_series_by_group(group, name, imputation.function)).reset_index(drop=True), schema
    else:
        return impute_df_series_by_group(df, name, imputation.function), schema


def impute_df_series_by_group(group, name, function) -> pd.DataFrame:
    group[name] = function(group, name)
    return group


def validate(df: pd.DataFrame, schema: Dict[str, Field]) -> None:
    info(f"validating fields")
    for name in df:
        # validate N/As / nulls
        if df[name].isna().any():
            raise ValueError(f"{name} has NA values")
        # validate limits
        if name in schema:
            field = schema[name]
            if isinstance(field, Numeric) or isinstance(field, Ordinal):
                if not inspect.isfunction(field.maximum) and df[name].max() > field.maximum:
                    raise ValueError(f"{name} has values greater than maximum allowed")
                if not inspect.isfunction(field.minimum) and df[name].min() < field.minimum:
                    raise ValueError(f"{name} has values less than minimum allowed")


def coerce_types(df: pd.DataFrame, schema: Dict[str, Field]) -> None:
    for name in df:
        if name in schema:
            field = schema[name]
            if isinstance(field, Ordinal):
                df[name] = df[name].astype('int64')
            elif isinstance(field, Boolean):
                df[name] = df[name].astype('bool')
