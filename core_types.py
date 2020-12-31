from abc import ABC
from datetime import datetime
from logging import info
from typing import Optional
from core_constants import *
import pandas as pd


class Imputation:
    def __init__(self, function: callable, keys: [str]):
        self._keys = keys
        self._function = function

    @property
    def keys(self) -> [str]:
        return self._keys

    @property
    def function(self) -> callable:
        return self._function


class Field(ABC):
    def __init__(self, name, datatype, imputations: [Imputation], mark_missing: bool):
        self._mark_missing = mark_missing
        self._imputations = imputations
        self._name = name
        self._datatype = datatype

    @property
    def imputations(self) -> [Imputation]:
        return self._imputations

    @property
    def mark_missing(self) -> bool:
        return self._mark_missing

    @property
    def name(self) -> str:
        return self._name

    @property
    def datatype(self) -> str:
        return self._datatype


class Date(Field):
    def __init__(self, name, imputations: [Imputation] = None, mark_missing=False):
        super().__init__(name, 'datetime64', imputations, mark_missing)


class Ordinal(Field):
    def __init__(self, name, minimum, maximum, imputations: [Imputation] = None, mark_missing=False):
        super().__init__(name, 'int32', imputations, mark_missing)
        self._minimum = minimum
        self._maximum = maximum

    @property
    def minimum(self):
        return self._minimum

    @property
    def maximum(self):
        return self._maximum


class Numeric(Field):
    def __init__(self, name, minimum, maximum, imputations: [Imputation] = None, mark_missing=False):
        super().__init__(name, 'float64', imputations, mark_missing)
        self._minimum = minimum
        self._maximum = maximum

    @property
    def minimum(self):
        return self._minimum

    @property
    def maximum(self):
        return self._maximum


class Nominal(Field):
    def __init__(self, name, imputations: [Imputation] = None, mark_missing=False):
        super().__init__(name, 'str', imputations, mark_missing)


class Boolean(Field):
    def __init__(self, name, imputations: [Imputation] = None, mark_missing=False):
        super().__init__(name, 'bool', imputations, mark_missing)


class DataSource:
    def __init__(self, location, fields: [Field]):
        self._location = location
        self._fields = fields

    @property
    def location(self):
        return self._location

    @property
    def fields(self):
        return self._fields


class Data:
    def __init__(self,
                 start_date: datetime.date,
                 end_date: datetime.date,
                 geos: DataSource,
                 data_sources: [DataSource]):
        self._datetime_index = pd.date_range(start_date, end_date, freq='D')
        self._df = Data.explode(Data.load(geos), self._datetime_index)
        self._start_date = start_date
        self._end_date = end_date
        self._fields = [] + geos.fields

        for data_source in data_sources:
            self.merge(data_source)

        # Add the GEO ID to the dataframe, which can be used for easier grouping of the dataset
        # For datasets that are country specific, we set the GEO_ID to only the country name
        # this will allow to to match all regions
        self._df[GEO_ID] = self._df[[COUNTRY, REGION]].apply(
            lambda x: x[COUNTRY] if x[REGION] == '' else (x[COUNTRY] + '/' + x[REGION]), axis=1)

        # Fill in time related fields (replacing existing values)
        # in the future, we want to allow exclusion for of any of these fields, based on configuration
        info('adding date fields')
        self._df[WEEK] = self._df[DATE].apply(lambda v: v.isocalendar()[1])
        self._df[MONTH] = self._df[DATE].apply(lambda v: v.month)
        self._df[QUARTER] = self._df[DATE].apply(lambda v: v.quarter)
        self._df[YEAR] = self._df[DATE].apply(lambda v: v.year)
        self._df[DAY_OF_YEAR] = self._df[DATE].apply(lambda v: v.timetuple().tm_yday)
        self._df[DAY_OF_MONTH] = self._df[DATE].apply(lambda v: v.timetuple().tm_mday)
        self._df[DAY_OF_WEEK] = self._df[DATE].apply(lambda v: v.weekday() + 1)

        # sort fields by column name
        self._df = self._df.reindex(sorted(self._df.columns), axis=1)

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    @df.setter
    def df(self, value: pd.DataFrame):
        self._df = value

    @property
    def fields(self) -> [Field]:
        return self._fields

    def merge(self, data_source: DataSource) -> None:
        info(f"merging {data_source.location}")

        # add the new fields to the dataset
        for merged_field in data_source.fields:
            found = False
            for existing_field in self._fields:
                if merged_field.name == existing_field.name:
                    found = True
            if not found:
                self._fields.append(merged_field)

        # load and impute
        df_new = Data.explode(Data.load(data_source), self._datetime_index)

        # merge
        self._df = self._df.merge(df_new,
                                  on=list({COUNTRY, REGION, DATE}.intersection(df_new)),
                                  how="left",
                                  suffixes=[None, '++++'])

        # drop duplicated columns
        for name in self._df:
            if name.endswith('++++'):
                self._df = self._df.drop(name, axis=1)

    @staticmethod
    def load(data_source: DataSource) -> pd.DataFrame:
        df = pd.read_csv(data_source.location, keep_default_na=False, error_bad_lines=False)
        for field in data_source.fields:
            if field.name in df:
                if isinstance(field, Numeric):
                    df[field.name] = pd.to_numeric(df[field.name])
                if isinstance(field, Ordinal):
                    df[field.name] = pd.to_numeric(df[field.name]).astype('Int64')  # nullable
                elif isinstance(field, Nominal):
                    df[field.name] = df[field.name].astype('str')
                elif isinstance(field, Boolean):
                    df[field.name] = df[field.name].astype('boolean')  # nullable
                elif isinstance(field, Date):
                    df[field.name] = pd.to_datetime(df[field.name])
        return df

    @staticmethod
    def explode(df: pd.DataFrame, datetime_index: pd.DatetimeIndex) -> pd.DataFrame:
        if DATE in df:
            return df  # nothing to explode
        else:
            query = Data.resolve_explosion_filter(df)
            if query:
                df[DATE] = df.apply(lambda r: datetime_index[pd.eval(query)], axis=1)
            else:
                df[DATE] = df.apply(lambda r: datetime_index, axis=1)
            return df.explode(DATE, ignore_index=True).reset_index(0, drop=True)

    @staticmethod
    def resolve_explosion_filter(df: pd.DataFrame) -> Optional[str]:
        conditions = []
        for name in df:
            if name == YEAR:
                conditions.append('datetime_index.year == r[YEAR]')
            elif name == MONTH:
                conditions.append('datetime_index.month == r[MONTH]')
            elif name == QUARTER:
                conditions.append('datetime_index.quarter == r[QUARTER]')
            elif name == WEEK:
                conditions.append('datetime_index.isocalendar().week == r[WEEK]')
            elif name == DAY_OF_WEEK:
                conditions.append('(datetime_index.weekday() + 1) == r[DAY_OF_WEEK]')
            elif name == DAY_OF_MONTH:
                conditions.append('datetime_index.timetuple().tm_mday == r[DAY_OF_MONTH]')
            elif name == DAY_OF_YEAR:
                conditions.append('datetime_index.timetuple().tm_yday == r[DAY_OF_YEAR]')
        if conditions:
            return ' and '.join([condition for condition in conditions])
        else:
            return None
