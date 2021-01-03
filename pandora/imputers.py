import pandas as pd


def impute_with_median(df: pd.DataFrame, name):
    return df[name].fillna(df[name].median())


def impute_with_mean(df: pd.DataFrame, name):
    return df[name].fillna(df[name].mean())


def impute_with_max(df: pd.DataFrame, name):
    return df[name].fillna(df[name].max())


def impute_with_min(df: pd.DataFrame, name):
    return df[name].fillna(df[name].min())


def impute_with_forward_fill(df: pd.DataFrame, column_name):
    return df[column_name].ffill().fillna(0)
