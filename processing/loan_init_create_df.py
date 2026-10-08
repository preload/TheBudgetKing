import pandas as pd

from models.loan_class import LoanRecord
from set_formats_validate_schemas import validate_loan_schema, set_loan_formats


def initialize_loans(file_path: str) -> list[LoanRecord]:
        df = pd.read_csv(file_path)
        return [LoanRecord(**row) for _, row in df.iterrows()]


def create_loan_df(loan_record: LoanRecord) -> pd.DataFrame:
    loan_data = {
        'active': [loan_record.active],
        'principal': [loan_record.principal],
        'currency': [loan_record.currency],
        'interest': [loan_record.interest],
        'term': [loan_record.term],
        'payment_frequency': [loan_record.payment_frequency],
        'amortization_type': [loan_record.amortization_type],
        'first_payment_date': [loan_record.first_payment_date],
        'disbursement_date': [loan_record.disbursement_date],
        'yearly_day_count_convention': [loan_record.yearly_day_count_convention],
        'payment_timing': [loan_record.payment_timing],
        'recurring_mandatory_fees': [loan_record.recurring_mandatory_fees],
        'rounding_rules': [loan_record.rounding_rules],
    }
    loan_data = pd.DataFrame(loan_data)
    loan_data = set_loan_formats(loan_data)
    if not validate_loan_schema(loan_data): raise ValueError("Schema validation failed")
    return loan_data

if __name__ == '__main__':
    loan = initialize_loans("../data/loans.csv")[0]
    df = create_loan_df(loan)
    print(df)
