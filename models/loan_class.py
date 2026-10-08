from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

import numpy_financial as npf

from core.enums import LoanRoundingRules, LoanPaymentTiming, LoanPaymentFrequency, LoanAmortizationType, \
    LoanYearlyDayCountConvention
from core.constants import CURRENCIES

@dataclass
class LoanRecord:
    active: bool
    principal: float
    currency: str
    interest: float
    term: int
    payment_frequency: LoanPaymentFrequency
    amortization_type: LoanAmortizationType
    first_payment_date: date
    disbursement_date: date
    yearly_day_count_convention: LoanYearlyDayCountConvention
    payment_timing: LoanPaymentTiming
    recurring_mandatory_fees: float
    rounding_rules: LoanRoundingRules

    def __post_init__(self):
        if self.currency not in CURRENCIES:
            raise ValueError(f"Invalid currency: {self.currency}")
        if self.rounding_rules not in LoanRoundingRules:
            raise ValueError(f"Invalid rounding rules: {self.rounding_rules}")
        if self.payment_frequency not in LoanPaymentFrequency:
            raise ValueError(f"Invalid payment frequency: {self.payment_frequency}")
        if self.amortization_type not in LoanAmortizationType:
            raise ValueError(f"Invalid amortization type: {self.amortization_type}")
        if self.yearly_day_count_convention not in LoanYearlyDayCountConvention:
            raise ValueError(f"Invalid yearly day count convention: {self.yearly_day_count_convention}")
        if self.payment_timing not in LoanPaymentTiming:
            raise ValueError(f"Invalid payment timing: {self.payment_timing}")
        if self.term <= 0:
            raise ValueError("Term must be a positive integer")
        if self.principal <= 0:
            raise ValueError("Principal must be a positive number")
        if self.interest <= 0:
            raise ValueError("Interest must be a positive number")
        if self.recurring_mandatory_fees < 0:
            raise ValueError("Recurring mandatory fees must be a non-negative number")

    # calculate monthly payment amount of existing loan
    def calculate_monthly_payment_amount(self) -> Decimal:
        return (
            Decimal(
                npf.pmt(
                    rate=self.interest / 100 / 12,
                    nper=self.term,
                    pv=-self.principal,
                ))).quantize(Decimal('0.01'), rounding=self.rounding_rules)

    # calculate principal payment for specific month of existing loan
    def calculate_principal_payment_for_specific_month(self, month_number: int) -> Decimal:
        if not isinstance(month_number, int):
            raise TypeError("month_number must be an integer")
        if month_number < 1 or month_number > self.term:
            raise ValueError("month_number must be between 1 and term")
        return (
            Decimal(
                npf.ppmt(
                    rate=self.interest / 100 / 12,
                    per=month_number,
                    nper=self.term,
                    pv=-self.principal,
                ))).quantize(Decimal('0.01'), rounding=self.rounding_rules)

    # calculate interest payment for specific month of existing loan
    def calculate_interest_payment_for_specific_month(self, month_number: int) -> Decimal:
        if not isinstance(month_number, int):
            raise TypeError("month_number must be an integer")
        if month_number < 1 or month_number > self.term:
            raise ValueError("month_number must be between 1 and term")
        return (
            Decimal(
                npf.ipmt(
                    rate=self.interest / 100 / 12,
                    per=month_number,
                    nper=self.term,
                    pv=-self.principal,
                ).item())).quantize(Decimal('0.01'), rounding=self.rounding_rules)

    # calculate period of new loan
    @staticmethod
    def calculate_period_of_loan(principal, interest_percentage, monthly_payment,
                                 rounding: str = ROUND_HALF_UP) -> Decimal:
        if not isinstance(principal, (int, float)) or not isinstance(interest_percentage,
                                                                     (int, float)) or not isinstance(
            monthly_payment, (int, float)):
            raise TypeError("principal, interest_percentage, and monthly_payment must be integers or floats")
        if not isinstance(rounding, str):
            raise TypeError("rounding must be a string")
        if rounding not in [rule for rule in LoanRoundingRules]:
            raise ValueError(f"Invalid rounding value: {rounding}")
        if principal <= 0 or interest_percentage <= 0 or monthly_payment <= 0:
            raise ValueError("principal, interest_percentage, and monthly_payment must be positive integers")

        return (
            Decimal(
                npf.nper(
                    rate=interest_percentage / 100 / 12,
                    pv=-principal,
                    pmt=monthly_payment
                ).item()).quantize(Decimal('0.01'), rounding=rounding))

    # calculate interest of new loan
    @staticmethod
    def calculate_interest_of_loan(total_loan_term: int, monthly_payment: float, principal: float,
                                   rounding: str = ROUND_HALF_UP) -> Decimal:
        if not isinstance(total_loan_term, int) or not isinstance(monthly_payment, (int, float)) or not isinstance(
                principal, (int, float)):
            raise TypeError("total_loan_term, monthly_payment, and principal must be integers or floats")
        if not isinstance(rounding, str):
            raise TypeError("rounding must be a string")
        if rounding not in [rule for rule in LoanRoundingRules]:
            raise ValueError(f"Invalid rounding value: {rounding}")
        if total_loan_term <= 0 or monthly_payment <= 0 or principal <= 0:
            raise ValueError("total_loan_term, monthly_payment, and principal must be positive integers")

        return (
            Decimal(
                npf.rate(
                    nper=total_loan_term,
                    pmt=-monthly_payment,
                    pv=principal,
                    fv=0
                ) * 12 * 100).quantize(Decimal('0.01'), rounding=rounding))

    # calculate initial loan principal
    @staticmethod
    def calculate_loan_principal(interest_percentage: float, total_loan_term: int, monthly_payment: int,
                                 rounding: str = ROUND_HALF_UP) -> Decimal:
        if not isinstance(interest_percentage, (int, float)) or not isinstance(total_loan_term, int) or not isinstance(
                monthly_payment, int):
            raise TypeError("interest_percentage, total_loan_term, and monthly_payment must be integers or floats")
        if not isinstance(rounding, str):
            raise TypeError("rounding must be a string")
        if rounding not in [rule for rule in LoanRoundingRules]:
            raise ValueError(f"Invalid rounding value: {rounding}")
        if total_loan_term <= 0 or monthly_payment <= 0:
            raise ValueError("total_loan_term and monthly_payment must be positive integers")

        return (
            Decimal(
                npf.pv(
                    rate=interest_percentage / 100 / 12,
                    nper=total_loan_term,
                    fv=0,
                    pmt=-monthly_payment,
                )).quantize(Decimal('1'), rounding=rounding))