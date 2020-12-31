import inspect
from logging import info

import pandas as pd

import dataset
from dataset import MISSING_INDICATOR_SUFFIX


def clean(data: dataset.Data) -> None:
    mark_missing(data)
    impute(data)
    validate(data)
    coerce_types(data)
    data.df = data.df.reindex(sorted(data.df.columns), axis=1)  # sort columns by name


def mark_missing(data: dataset.Data) -> None:
    for field in data.fields:
        if field.name in data.df and field.mark_missing:
            info(f"marking missing values for column: {field.name}")
            data.df[f"{field.name}{MISSING_INDICATOR_SUFFIX}"] = data.df[field.name].isna()


def impute(data: dataset.Data) -> None:
    for field in data.fields:
        if field.name in data.df:
            if field.imputations:
                impute_series(data, field)


def impute_series(data: dataset.Data, field: dataset.Field) -> None:
    info(f"imputing {field.name}")
    for imputation in field.imputations:
        if imputation.keys:
            if data.df[field.name].isna().any():
                data.df = data.df.groupby(imputation.keys).apply(
                    lambda group: impute_series_by_group(group, field.name, imputation.function)).reset_index(drop=True)
        else:
            data.df = impute_series_by_group(data.df, field.name, imputation.function)


def impute_series_by_group(group, name, function) -> pd.DataFrame:
    group[name] = function(group, name)
    return group


def validate(data: dataset.Data) -> None:
    info(f"validating fields")
    for field in data.fields:
        name = field.name
        if name in data.df:
            # validate N/As / nulls
            if data.df[name].isna().any():
                raise ValueError(f"{name} has NA values")
            # validate limits
            if isinstance(field, dataset.Numeric) or isinstance(field, dataset.Ordinal):
                if not inspect.isfunction(field.maximum) and data.df[name].max() > field.maximum:
                    raise ValueError(f"{field.name} has values greater than maximum allowed")
                if not inspect.isfunction(field.minimum) and data.df[name].min() < field.minimum:
                    raise ValueError(f"{field.name} has values less than minimum allowed")


def coerce_types(data: dataset.Data) -> None:
    for field in data.fields:
        name = field.name
        if name in data.df:
            if isinstance(field, dataset.Ordinal):
                data.df[name] = data.df[name].astype('int64')
            elif isinstance(field, dataset.Boolean):
                data.df[name] = data.df[name].astype('bool')
