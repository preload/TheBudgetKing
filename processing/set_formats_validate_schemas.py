from datetime import datetime

import pandas as pd

from core.constants import CLEANED_TRX_COLUMNS, LOAN_COLUMNS
from core.enums import DuplicateStatus, SourceType, LoanPaymentFrequency, LoanAmortizationType, \
    LoanYearlyDayCountConvention, LoanRoundingRules, LoanPaymentTiming


def set_trx_formats(dataframe: pd.DataFrame) -> pd.DataFrame:
    if 'dirty_amount' in dataframe.columns: dataframe.drop(columns=['dirty_amount'], inplace=True)
    if dataframe['amount'].dtype != 'float64':
        dataframe['amount'] = dataframe['amount'].str.replace(',', '.')
        dataframe['amount'] = dataframe['amount'].str.replace(r'[^\d.]+', '', regex=True)

    try:
        dataframe['date'] = pd.to_datetime(dataframe['date'], format='%d.%m.%Y')
    except ValueError:
        dataframe['date'] = pd.to_datetime(dataframe['date'], format='%Y-%m-%d')

    dataframe['import_timestamp'] = pd.to_datetime(datetime.now().isoformat(timespec='seconds'))
    return dataframe.astype(
        {
            'date': 'datetime64[us]',
            'authcode': 'string',
            'trx_type': 'string',
            'merchant': 'string',
            'amount': 'float64',
            'notes': 'string',
            'category': 'string',
            'import_timestamp': 'datetime64[us]',
            'source': SourceType.dtype(),
            'clean_merchant': 'string',
            'duplicate_status': DuplicateStatus.dtype(),
            'icon': 'string'
        }
    )


def validate_first_trx_row(dataframe: pd.DataFrame):
    def validator(df: pd.DataFrame) -> bool:
        try:
            df.loc[0, 'amount'] = df.loc[0, 'amount'].replace(',', '.')
            float(df.loc[0, 'amount'])
            df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')
            return True
        except ValueError:
            return False

    if not validator(dataframe):
        dataframe.drop(0, inplace=True)
        dataframe.reset_index(drop=True, inplace=True)
    if not validator(dataframe):
        raise ValueError("Invalid CSV format")


def validate_trx_schema(dataframe: pd.DataFrame) -> bool:
    if not all(col in dataframe.columns for col in CLEANED_TRX_COLUMNS): return False
    if not dataframe['date'].dtype == 'datetime64[us]': return False
    if not dataframe['authcode'].dtype == 'string': return False
    if not dataframe['trx_type'].dtype == 'string': return False
    if not dataframe['merchant'].dtype == 'string': return False
    if not dataframe['amount'].dtype == 'float64': return False
    if not dataframe['notes'].dtype == 'string': return False
    if not dataframe['category'].dtype == 'string': return False
    if not dataframe['import_timestamp'].dtype == 'datetime64[us]': return False
    if not dataframe['source'].dtype == 'category': return False
    if not dataframe['clean_merchant'].dtype == 'string': return False
    if not dataframe['duplicate_status'].dtype == 'category': return False
    if not dataframe['icon'].dtype == 'string': return False

    return True


def set_loan_formats(dataframe: pd.DataFrame) -> pd.DataFrame:
    return dataframe.astype(
        {
            'active': bool,
            'principal': float,
            'currency': str,
            'interest': float,
            'term': int,
            'payment_frequency': LoanPaymentFrequency.dtype(),
            'amortization_type': LoanAmortizationType.dtype(),
            'first_payment_date': 'datetime64[us]',
            'disbursement_date': 'datetime64[us]',
            'yearly_day_count_convention': LoanYearlyDayCountConvention.dtype(),
            'payment_timing': LoanPaymentTiming.dtype(),
            'recurring_mandatory_fees': float,
            'rounding_rules': LoanRoundingRules.dtype(),
        }
    )


def validate_loan_schema(dataframe: pd.DataFrame) -> bool:
    if not all(column in dataframe.columns for column in LOAN_COLUMNS):
        print("Columns not found: ", LOAN_COLUMNS - dataframe.columns, sep="")
        return False

    if not dataframe['principal'].dtype == float:
        print("Principal column is not float")
        return False

    if not dataframe['currency'].dtype == 'str':
        print("Currency column is not string")
        return False

    if not dataframe['interest'].dtype == float:
        print("Interest column is not float")
        return False

    if not dataframe['term'].dtype == int:
        print("Term column is not int")
        return False

    if not dataframe['payment_frequency'].astype(str).isin([freq for freq in LoanPaymentFrequency]).all():
        print("Payment frequency column is not in LoanPaymentFrequency enum")
        return False

    if not dataframe['amortization_type'].astype(str).isin([amort for amort in LoanAmortizationType]).all():
        print("Amortization type column is not in LoanAmortizationType enum")
        return False

    if not pd.api.types.is_datetime64_any_dtype(dataframe['first_payment_date']):
        print("First payment date column is not datetime64")
        return False

    if not pd.api.types.is_datetime64_any_dtype(dataframe['disbursement_date']):
        print("Disbursement date column is not datetime64")
        return False

    if not dataframe['yearly_day_count_convention'].astype(str).isin(
            [convention for convention in LoanYearlyDayCountConvention]).all():
        print("Yearly day count convention column is not in LoanYearlyDayCountConvention enum")
        return False

    if not dataframe['payment_timing'].astype(str).isin([timing for timing in LoanPaymentTiming]).all():
        print("Payment timing column is not in LoanPaymentTiming enum")
        return False

    if not dataframe['recurring_mandatory_fees'].dtype == float:
        print("Recurring mandatory fees column is not float")
        return False

    if not dataframe['rounding_rules'].astype(str).isin([rule for rule in LoanRoundingRules]).all():
        print("Rounding rules column is not in LoanRoundingRules enum")
        return False

    return True
