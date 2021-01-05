from logging import info

import pandas as pd

from pandora.core_fields import MISSING_INDICATOR_SUFFIX
from pandora.core_types import Module, Imputation


def impute(df: pd.DataFrame, module: Module) -> pd.DataFrame:
    df = mark_missing(df, module)
    df = impute_features(df, module)
    df = df.reindex(sorted(df.columns), axis=1)
    return df


def mark_missing(df: pd.DataFrame, module: Module) -> pd.DataFrame:
    for name in module.mark_missing:
        df[f"{name}{MISSING_INDICATOR_SUFFIX}"] = df[name].isna()
    return df


def impute_features(df: pd.DataFrame, module: Module) -> pd.DataFrame:
    for name in module.imputations:
        info(f"{module.location} - imputing {name}")
        for imputation in module.imputations[name]:
            if df[name].isna().any():
                df = impute_feature_by_series(df, name, imputation)
    return df


def impute_feature_by_series(df: pd.DataFrame, name: str, imputation: Imputation) -> pd.DataFrame:
    if imputation.keys:
        return df.groupby(imputation.keys).apply(
            lambda group: impute_group(group, name, imputation.function)).reset_index(drop=True)
    else:
        return impute_group(df, name, imputation.function)


def impute_group(group, name, function) -> pd.DataFrame:
    group[name] = function(group, name)
    return group
