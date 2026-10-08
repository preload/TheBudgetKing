import pandas as pd

from core.enums import DuplicateStatus
from processing.trx_clean_assume_icon_authcode import assume_trx_categories
from processing.set_formats_validate_schemas import set_trx_formats, validate_trx_schema


def merge_transactions(primary_df: pd.DataFrame, new_data: pd.DataFrame) -> pd.DataFrame:
    # FIX SCRAPED DATAFRAME
    new_data['duplicate_status'] = DuplicateStatus.NOT_REVIEWED
    clean_new_data = (
        new_data
        .pipe(set_trx_formats)
    )

    primary_df = pd.concat([primary_df, clean_new_data], ignore_index=True, sort=False)
    primary_df = assume_trx_categories(primary_df)
    primary_df = _mark_duplicates(primary_df, clean_new_data)

    # VALIDATE SCHEMA
    if not validate_trx_schema(primary_df): raise ValueError("Schema validation failed")

    # RETURN VALIDATED DF
    return primary_df


def _mark_duplicates(primary_df: pd.DataFrame, new_data: pd.DataFrame) -> pd.DataFrame:
    condition1 = (primary_df.duplicated(subset=['date', 'clean_merchant', 'amount'], keep=False))
    condition2 = (primary_df.duplicate_status.isin([DuplicateStatus.UNIQUE, DuplicateStatus.NOT_REVIEWED]))
    condition3 = (primary_df.date >= pd.to_datetime(new_data['date'].min()))

    groups = primary_df.loc[condition1 & condition2 & condition3].groupby(['date', 'clean_merchant', 'amount']).groups
    group_indices = [list(indices) for indices in groups.values() if len(indices) > 1]

    for indices in group_indices: primary_df.loc[indices, 'duplicate_status'] = DuplicateStatus.DUPLICATE

    # MARK ALL OTHER TRANSACTIONS AS UNIQUE
    primary_df.loc[
        primary_df.duplicate_status.isin([DuplicateStatus.NOT_REVIEWED]), 'duplicate_status'] = DuplicateStatus.UNIQUE

    return primary_df
