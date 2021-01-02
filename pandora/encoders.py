import math
from typing import Dict, Optional

import category_encoders as ce
import pandas as pd

from pandora.core_types import Field, Numeric

DROP_INTERCEPT = True
HASH_METHOD = 'md5'
INTERCEPT_COLUMN = 'intercept'
INFIX_HASH = '_hash_'
INFIX_OHE = '_ohe_'
INFIX_BINARY = '_bin_'
INFIX_SUM = '_sum_'
INFIX_BACKWARD_DIFFERENCE = '_bde_'
INFIX_BASE_N = '_base_n_'
INFIX_HELMERT = '_helmert_'
INFIX_POLYNOMIAL = '_poly_'


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
    return encode(encoder,
                  df,
                  schema,
                  name,
                  0.0,
                  1.0,
                  INFIX_HASH)


def one_hot_encode(df: pd.DataFrame, schema: Dict[str, Field], name: str) -> (pd.DataFrame, Dict[str, Field]):
    encoder = ce.OneHotEncoder(cols=[name], use_cat_names=True)
    return encode(encoder,
                  df,
                  schema,
                  name,
                  0.0,
                  1.0,
                  INFIX_OHE)


def binary_encode(df: pd.DataFrame,
                  schema: Dict[str, Field],
                  name: str) -> (pd.DataFrame, Dict[str, Field]):
    encoder = ce.BinaryEncoder(cols=[name])
    return encode(encoder,
                  df,
                  schema,
                  name,
                  0.0,
                  1.0,
                  INFIX_BINARY)


def sum_encode(df: pd.DataFrame,
               schema: Dict[str, Field],
               name: str) -> (pd.DataFrame, Dict[str, Field]):
    encoder = ce.SumEncoder(cols=[name])
    return encode(encoder,
                  df,
                  schema,
                  name,
                  -1.0,
                  1.0,
                  INFIX_SUM)


def backward_difference_encode(df: pd.DataFrame,
                               schema: Dict[str, Field],
                               name: str) -> (pd.DataFrame, Dict[str, Field]):
    encoder = ce.SumEncoder(cols=[name])
    return encode(encoder,
                  df,
                  schema,
                  name,
                  -1.0,
                  1.0,
                  INFIX_BACKWARD_DIFFERENCE)


def base_n_encode(df: pd.DataFrame,
                  schema: Dict[str, Field],
                  name: str,
                  base: int = 8) -> (pd.DataFrame, Dict[str, Field]):
    encoder = ce.BaseNEncoder(cols=[name], base=base)
    return encode(encoder,
                  df,
                  schema,
                  name,
                  0.0,
                  float(base) - 1.0,
                  INFIX_BASE_N)


def helmert_contrast_encode(df: pd.DataFrame,
                            schema: Dict[str, Field],
                            name: str) -> (pd.DataFrame, Dict[str, Field]):
    encoder = ce.HelmertEncoder(cols=[name])
    return encode(encoder,
                  df,
                  schema,
                  name,
                  -1.0,
                  None,
                  INFIX_HELMERT)


def polynomial_encode(df: pd.DataFrame,
                      schema: Dict[str, Field],
                      name: str) -> (pd.DataFrame, Dict[str, Field]):
    encoder = ce.PolynomialEncoder(cols=[name])
    return encode(encoder,
                  df,
                  schema,
                  name,
                  -1.0,
                  None,
                  INFIX_POLYNOMIAL)


def encode(encoder,
           df: pd.DataFrame,
           schema: Dict[str, Field],
           name: str,
           minimum: float,
           maximum: Optional[float],
           infix) -> (pd.DataFrame, Dict[str, Field]):
    df_encoded = encoder.fit_transform(df[name])
    df_encoded = df_encoded.drop(columns=[INTERCEPT_COLUMN], errors='ignore')
    df_encoded = update_column_names(df_encoded, name, infix)
    schema = update_schema(df_encoded, schema, minimum, maximum)
    df = df.join(df_encoded)
    return df, schema


def update_column_names(df_encoded,
                        name,
                        infix) -> pd.DataFrame:
    df_encoded = df_encoded.rename(columns=lambda s: s.replace(f"col_", f"{name}_", 1) if s.startswith('col_') else s)
    df_encoded = df_encoded.rename(columns=lambda s: s.replace(f"{name}_", f"{name}{infix}", 1))
    return df_encoded


def update_schema(df_encoded,
                  schema,
                  minimum,
                  maximum) -> Dict[str, Field]:
    schema = dict(schema)
    for name in df_encoded.columns:
        schema.update({name: Numeric(minimum, maximum if maximum else df_encoded[name].max())})
    return schema
