import math
from abc import ABC, abstractmethod

import fnvhash
from typing import Dict, Optional

import category_encoders as ce
import pandas as pd

from pandora.core_types import Field, Numeric


class Encoder(ABC):
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self):
        return self._name

    @abstractmethod
    def fit_transform(self, df: pd.DataFrame, schema: Dict[str, Field]) -> (pd.DataFrame, Dict[str, Field]):
        raise RuntimeError('unimplemented')

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        raise RuntimeError('unimplemented')


class CEEncoder(Encoder, ABC):

    def __init__(self, name: str, infix: str, internal_encoder, minimum: float, maximum: Optional[float]):
        super().__init__(name)
        self._infix = infix
        self._internal_encoder = internal_encoder
        self._minimum = minimum
        self._maximum = maximum

    def fit_transform(self,
                      df: pd.DataFrame,
                      schema: Dict[str, Field]) -> (pd.DataFrame, Dict[str, Field]):
        df_encoded = self._internal_encoder.fit_transform(df[self.name])
        df_encoded = df_encoded.drop(columns=['intercept'], errors='ignore')
        df_encoded = self.update_column_names(df_encoded)
        return df.join(df_encoded), self.update_schema(df_encoded, schema)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df_encoded = self._internal_encoder.transform(df[self.name])
        df_encoded = df_encoded.drop(columns=['intercept'], errors='ignore')
        df_encoded = self.update_column_names(df_encoded)
        return df.join(df_encoded)

    def update_column_names(self, df_encoded: pd.DataFrame) -> pd.DataFrame:
        col = 'col_'
        old = f"{self.name}_"
        new = f"{self.name}{self._infix}"
        df_encoded = df_encoded.rename(columns=lambda s: s.replace(col, old, 1) if s.startswith(col) else s)
        df_encoded = df_encoded.rename(columns=lambda s: s.replace(old, new, 1))
        return df_encoded

    def update_schema(self, df_encoded: pd.DataFrame, schema) -> Dict[str, Field]:
        schema = dict(schema)
        for name in df_encoded.columns:
            schema.update({name: Numeric(self._minimum,
                                         self._maximum if self._maximum else df_encoded[name].max())})
        return schema


class BinaryEncoder(CEEncoder):
    def __init__(self, name: str):
        super().__init__(name, '_bin_', ce.BinaryEncoder(cols=[name]), 0, 1)


class SumEncoder(CEEncoder):
    def __init__(self, name: str):
        super().__init__(name, '_sum_', ce.SumEncoder(cols=[name]), -1.0, 1.0)


class HelmertContrastEncoder(CEEncoder):
    def __init__(self, name: str):
        super().__init__(name, '_helmert_', ce.HelmertEncoder(cols=[name]), -1.0, None)


class HashEncoder(CEEncoder):
    def __init__(self, name: str, bits: int):
        super().__init__(name, '_hash_', ce.HashingEncoder(cols=[name], n_components=bits), 0, 1)


class OneHotEncoder(CEEncoder):
    def __init__(self, name: str):
        super().__init__(name, '_ohe_', ce.OneHotEncoder(cols=[name], use_cat_names=True), 0, 1)


class BackwardDifferenceEncoder(CEEncoder):
    def __init__(self, name: str):
        super().__init__(name, '_bde_', ce.BackwardDifferenceEncoder(cols=[name]), -1.0, 1.0)


class BaseNEncoder(CEEncoder):
    def __init__(self, name: str, base: int = 8):
        super().__init__(name, '_base_n_', ce.BaseNEncoder(cols=[name]), 0, base - 1)


class PolynomialEncoder(CEEncoder):
    def __init__(self, name: str):
        super().__init__(name, '_poly_', ce.PolynomialEncoder(cols=[name]), -1.0, None)


class CyclicalEncoder(Encoder):
    def __init__(self, name: str):
        super().__init__(name)

    def fit_transform(self, df: pd.DataFrame, schema: Dict[str, Field]) -> (pd.DataFrame, Dict[str, Field]):
        return self.transform(df), self.update_schema(schema)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if df[f"{self.name}"].max() > 1.0 or df[f"{self.name}"].min() < 0.0:
            raise ValueError(f"column {self.name} must be scaled in the range of 0.0 -> 1.0 before cyclical encoding")
        df[f"{self.name}_sin"] = df[self.name].map(lambda x: math.sin(2 * math.pi * x))
        df[f"{self.name}_cos"] = df[self.name].map(lambda x: math.cos(2 * math.pi * x))
        return df

    def update_schema(self, schema: Dict[str, Field]) -> (pd.DataFrame, Dict[str, Field]):
        schema = dict(schema)
        schema.update({f"{self.name}_sin": Numeric(-1.0, 1.0)})
        schema.update({f"{self.name}_cos": Numeric(-1.0, 1.0)})
        return schema


class BloomFilterEncoder(CEEncoder):
    def __init__(self, name: str, hashes: int, bits: int):
        super().__init__(name, '_bloom_', None, 0, 1)
        self._hashes = hashes
        self._bits = bits

    @property
    def hashes(self):
        return self._hashes

    @property
    def bits(self):
        return self._bits

    def fit_transform(self, df: pd.DataFrame, schema: Dict[str, Field]) -> (pd.DataFrame, Dict[str, Field]):
        df_encoded = self.transform(df)
        return df.join(df_encoded), super().update_schema(df_encoded, schema)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df_encoded = pd.DataFrame()
        for i in range(0, self.hashes):
            df_encoded['tmp'] = df[self.name].map(lambda v: BloomFilterEncoder.hash(i, v, self.bits))
            for bit in range(0, self.bits):
                bit_column = f"{self.name}{'_bloom_'}{bit}"
                df_encoded.loc[df_encoded['tmp'] == bit, bit_column] = 1
        return df_encoded.drop(columns=['tmp']).fillna(0)

    @staticmethod
    def hash(hash_index, value, bits) -> int:
        return fnvhash.fnv1a_32((str(value) + str(hash_index)).encode()) % bits
