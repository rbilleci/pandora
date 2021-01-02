import math
from typing import Dict

import category_encoders as ce
import pandas as pd

from pandora.core_types import Field, Numeric

HASH_METHOD = 'md5'
BIN_ENCODER_INFIX = '_bin_'
SUM_ENCODER_INFIX = '_sum_'
OHE_ENCODER_INFIX = '_ohe_'
BDE_ENCODER_INFIX = '_bde_'
HASH_ENCODER_INFIX = '_hash_'
BASE_N_ENCODER_INFIX = '_base_n_'
HELMERT_CONTRAST_ENCODER_INFIX = '_hce_'
POLYNOMIAL_ENCODER_INFIX = '_poly_'


def cyclical_encode(df: pd.DataFrame,
                    schema: Dict[str, Field],
                    name: str,
                    fun: callable,
                    limit: float) -> (pd.DataFrame, Dict[str, Field]):
    df[f"{name}_sin"] = df[name].map(lambda x: math.sin(2 * math.pi * fun(x) / limit))
    df[f"{name}_cos"] = df[name].map(lambda x: math.cos(2 * math.pi * fun(x) / limit))
    schema = dict(schema)
    schema.update({f"{name}_sin": Numeric(-1.0, 1.0)})
    schema.update({f"{name}_cos": Numeric(-1.0, 1.0)})
    return df, schema


def hash_encode(df: pd.DataFrame,
                schema: Dict[str, Field],
                name: str,
                bits: int = 16) -> (pd.DataFrame, Dict[str, Field]):
    encoder = ce.HashingEncoder(cols=[name], n_components=bits, hash_method=HASH_METHOD)
    return encode(encoder, df, schema, name, HASH_ENCODER_INFIX)


def one_hot_encode(df: pd.DataFrame, schema: Dict[str, Field], name: str) -> (pd.DataFrame, Dict[str, Field]):
    encoder = ce.OneHotEncoder(cols=[name], use_cat_names=True)
    return encode(encoder, df, schema, name, OHE_ENCODER_INFIX)


def binary_encode(df: pd.DataFrame,
                  schema: Dict[str, Field],
                  name: str) -> (pd.DataFrame, Dict[str, Field]):
    encoder = ce.BinaryEncoder(cols=[name])
    return encode(encoder, df, schema, name, BIN_ENCODER_INFIX)


def sum_encode(df: pd.DataFrame,
               schema: Dict[str, Field],
               name: str) -> (pd.DataFrame, Dict[str, Field]):
    encoder = ce.SumEncoder(cols=[name])
    return encode(encoder, df, schema, name, SUM_ENCODER_INFIX)


def backward_difference_encode(df: pd.DataFrame,
                               schema: Dict[str, Field],
                               name: str) -> (pd.DataFrame, Dict[str, Field]):
    encoder = ce.SumEncoder(cols=[name])
    return encode(encoder, df, schema, name, BDE_ENCODER_INFIX)


def base_n_encode(df: pd.DataFrame,
                  schema: Dict[str, Field],
                  name: str,
                  base: int = 2) -> (pd.DataFrame, Dict[str, Field]):
    encoder = ce.BaseNEncoder(cols=[name], base=base)
    return encode(encoder, df, schema, name, BASE_N_ENCODER_INFIX)


def helmert_contrast_encode(df: pd.DataFrame,
                            schema: Dict[str, Field],
                            name: str) -> (pd.DataFrame, Dict[str, Field]):
    encoder = ce.HelmertEncoder(cols=[name])
    return encode(encoder, df, schema, name, HELMERT_CONTRAST_ENCODER_INFIX)


def polynomial_encode(df: pd.DataFrame,
                      schema: Dict[str, Field],
                      name: str) -> (pd.DataFrame, Dict[str, Field]):
    encoder = ce.PolynomialEncoder(cols=[name])
    return encode(encoder, df, schema, name, POLYNOMIAL_ENCODER_INFIX)


def encode(encoder,
           df: pd.DataFrame,
           schema: Dict[str, Field],
           name: str,
           infix: str) -> (pd.DataFrame, Dict[str, Field]):
    df_encoded = encoder.fit_transform(df[name])
    df_encoded = df_encoded.rename(columns=lambda s: s.replace(f"col_", f"{name}_", 1) if s.startswith('col_') else s)
    df_encoded = df_encoded.rename(columns=lambda s: s.replace(f"{name}_", f"{name}{infix}", 1))
    return df.join(df_encoded), dict(**schema, **{name: Numeric(0.0, 1.0) for name in df_encoded.columns})
