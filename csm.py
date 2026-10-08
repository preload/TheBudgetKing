import os

import pandas as pd

from core.enums import DuplicateStatus
from ingestion.trx_init_scrape_import import initialize_trx_data, scrape_pdf, load_from_csv, load_from_clipboard
from processing.trx_clean_assume_icon_authcode import apply_trx_pipeline


class CentralStateManager:

    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_dir, 'data/main_trx_2.csv')
        self.file_path = csv_path
        self.trx_df = initialize_trx_data(self.file_path)
        self.import_df = None
        self.manual_df = None
        self._update_df_field_debounce_task = None

    def get_trx_data(self, search_term: str = "", category: str = "", date_mask: pd.Series = None,
                     amount_mask: pd.Series = None) -> pd.DataFrame:
        if date_mask is None: date_mask = pd.Series(True, index=self.trx_df.index)
        if amount_mask is None: amount_mask = pd.Series(True, index=self.trx_df.index)
        mask = pd.Series(True, index=self.trx_df.index)

        if category:
            mask &= self.trx_df['category'].str.contains(category, case=False, na=False)
        if search_term:
            search_term_mask = (
                    self.trx_df['merchant'].str.contains(search_term, case=False, na=False) |
                    self.trx_df['notes'].str.contains(search_term, case=False, na=False) |
                    self.trx_df['amount'].astype(str).str.contains(search_term, case=False, na=False)
            )
            mask &= search_term_mask

        mask &= date_mask
        mask &= amount_mask

        return self.trx_df[mask]

    def get_trx_data_date_mask(self, start_date: str, end_date: str) -> pd.Series:
        mask = pd.Series(True, index=self.trx_df.index)
        if start_date:
            mask &= self.trx_df['date'] >= pd.to_datetime(start_date)
        if end_date:
            mask &= self.trx_df['date'] <= pd.to_datetime(end_date)
        return mask

    def get_trx_data_amount_mask(self, comparator: str = "", amount: float = 0) -> pd.Series:
        mask = pd.Series(True, index=self.trx_df.index)
        if comparator == 'Bigger Than':
            mask &= self.trx_df['amount'] > amount
        if comparator == 'Smaller Than':
            mask &= self.trx_df['amount'] < amount
        if comparator == 'Equals':
            mask &= self.trx_df['amount'] == amount
        return mask

    def get_paginated_trx_data(self, page_nr: int, page_size: int, data: pd.DataFrame) -> pd.DataFrame:
        start_index = (page_nr - 1) * page_size
        end_index = start_index + page_size
        return data.iloc[start_index:end_index] if data is not None else pd.DataFrame()

    def get_nr_of_pages_trx_data(self, page_size: int, data: pd.DataFrame) -> int:
        return (len(data) // page_size) + (1 if len(data) % page_size != 0 else 0) if data is not None else 1

    def get_duplicate_trx_data(self):
        condition1 = self.trx_df['duplicate_status'] == DuplicateStatus.DUPLICATE
        condition2 = (self.trx_df.duplicated(subset=['date', 'clean_merchant', 'amount'], keep=False))
        groups = self.trx_df.loc[condition1 & condition2].groupby(
            ['date', 'clean_merchant', 'amount']).groups
        group_indices = [list(indices) for indices in groups.values() if len(indices) > 1]
        yield from (self.trx_df.loc[indices] for indices in group_indices)

    def get_unique_categories(self):
        self.trx_df['category'] = self.trx_df['category'].fillna('Not assigned')
        return [''] + sorted(self.trx_df['category'].unique().tolist())

    def get_unique_values(self, column: str):
        return [''] + sorted(self.trx_df[column].dropna().unique().tolist())

    def add_manual_df_row(self, row: pd.Series):
        if self.manual_df is None:
            self.manual_df = pd.DataFrame(columns=self.trx_df.columns)

        self.manual_df.loc[len(self.manual_df)] = row
        self.manual_df = apply_trx_pipeline(self.manual_df)

    def update_trx_field(self, authcode: str, column: str, value: str, dataframe: pd.DataFrame = None):
        using_default = dataframe is None
        if using_default: dataframe = self.trx_df
        mask = dataframe['authcode'] == authcode

        if column == 'amount': value = float(value) if value != '' else 0
        dataframe.loc[mask, column] = value if value != '' else pd.NA

        if column == 'merchant':
            if pd.notna(dataframe.loc[mask, 'clean_merchant'].squeeze()):
                dataframe.loc[mask, 'clean_merchant'] = pd.NA
                print('[update_trx_field] clean_merchant cleared')
            if pd.notna(dataframe.loc[mask, 'icon'].squeeze()):
                dataframe.loc[mask, 'icon'] = pd.NA
                print('[update_trx_field] icon cleared')
            dataframe = apply_trx_pipeline(dataframe)

        print('[update_trx_field]', dataframe.loc[mask, column])

        if using_default:
            self.trx_df = dataframe
        else:
            return dataframe

    def import_trx_data(self, file_path: str = None):
        if file_path.endswith('.csv'):
            self.import_df = load_from_csv(file_path)
        elif file_path.endswith('.pdf'):
            self.import_df = scrape_pdf(file_path)
        elif file_path in [None, '', ' ']:
            self.import_df = load_from_clipboard()

    def save_trx_data(self):
        self.trx_df.to_csv(self.file_path, index=False)

    def get_trx_row(self, authcode: str):
        return self.trx_df.loc[self.trx_df['authcode'] == authcode]

    def merge_trx_data(self, import_df: pd.DataFrame = None):
        if import_df is None: import_df = self.import_df
        self.trx_df = pd.concat([self.trx_df, import_df], ignore_index=True)

    def merge_subset_trx_data(self, subset: set):
        self.import_df = self.import_df.loc[self.import_df['authcode'].isin(subset)]
        self.merge_trx_data()

    def drop_row(self, authcode:str, dataframe: pd.DataFrame = None):
        if dataframe is None: dataframe = self.trx_df
        mask = dataframe['authcode'] == authcode

        dataframe = dataframe.drop(dataframe[mask].index)
        self.trx_df = dataframe