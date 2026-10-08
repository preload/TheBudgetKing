import re
from random import randint

import pandas as pd
import pyconify

from core.constants import STOP_WORDS
from processing.set_formats_validate_schemas import set_trx_formats


def make_clean_trx_merchant(dataframe: pd.DataFrame) -> pd.DataFrame:
    stop_words_list = sorted(STOP_WORDS, key=len, reverse=True)
    stop_words_regex = rf"\b({'|'.join(stop_words_list)})\b"

    mask = dataframe['clean_merchant'].isna()
    if not mask.any(): return dataframe

    dataframe.loc[mask, 'clean_merchant'] = (
        dataframe.loc[mask, 'merchant']
        .str.lower()
        .str.replace(stop_words_regex, '', flags=re.IGNORECASE, regex=True)
        .str.replace(r'[^\w\s]+', ' ', regex=True)
        .str.replace(r'\s\w*\dw*\b', ' ', regex=True)
        .str.replace(r'\s+', ' ', regex=True)
        .str.replace(r'^\s+|\s+$', '', regex=True)
    )

    return dataframe


def assume_trx_categories(dataframe: pd.DataFrame) -> pd.DataFrame:
    merchant_modes = dataframe.groupby('clean_merchant')['category'].agg(
        lambda x: x.mode().iloc[0] if not x.mode().empty else pd.NA
    )
    dataframe['category'] = dataframe['category'].fillna(dataframe['clean_merchant'].map(merchant_modes))

    return dataframe


def make_trx_icon(dataframe: pd.DataFrame) -> pd.DataFrame:
    def resolve_icon(clean_merchant: str) -> str:
        check = pyconify.search(clean_merchant).get('icons')
        if check:
            icon = pyconify.svg(check[0]).decode('utf-8')
        else:
            icon = 'Not Found'
        return icon

    mask = dataframe['icon'].isna()  # | dataframe['icon'].isin(['Not Found', ''])
    print(f"[_make_trx_icon] {mask.sum()} of {len(dataframe)} rows need icon lookup")
    if not mask.any(): return dataframe

    dataframe.loc[mask, 'icon'] = dataframe.loc[mask, 'clean_merchant'].apply(resolve_icon)
    return dataframe


def _make_trx_authcodes(dataframe: pd.DataFrame) -> pd.DataFrame:
    mask = dataframe['authcode'].isna()
    if not mask.any(): return dataframe

    random_nrs = [randint(10000000, 99999999) for _ in range(len(dataframe[mask]))]
    missing_indices = dataframe[mask].index
    dataframe.loc[mask, 'authcode'] = [f'GEN{nr}{index}' for nr, index in zip(random_nrs, missing_indices)]
    return dataframe


def apply_trx_pipeline(dataframe: pd.DataFrame) -> pd.DataFrame:
    return (
        dataframe
        .pipe(set_trx_formats)
        .pipe(assume_trx_categories)
        .pipe(make_clean_trx_merchant)
        .pipe(_make_trx_authcodes)
        .pipe(make_trx_icon)
    )
