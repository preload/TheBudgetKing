from enum import StrEnum

from pandas.api.types import CategoricalDtype


class CategorialEnum(StrEnum):
    @classmethod
    def dtype(cls) -> CategoricalDtype:
        return CategoricalDtype(categories=[c.value for c in cls], ordered=False)


class DuplicateStatus(CategorialEnum):
    UNIQUE = "UNIQUE"
    DUPLICATE = "DUPLICATE"
    NOT_REVIEWED = "NOT_REVIEWED"
    VERIFIED_UNIQUE = "VERIFIED_UNIQUE"


class SourceType(CategorialEnum):
    PDF = "PDF"
    CSV = "CSV"
    ClipBoard = "CP"
    MANUAL = "MANUAL"


class LoanPaymentFrequency(CategorialEnum):
    WEEKLY = "WEEKLY"
    BIWEEKLY = "BIWEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUALLY = "ANNUALLY"


class LoanAmortizationType(CategorialEnum):
    ANNUITY = "ANNUITY"
    LINEAR = "LINEAR"
    INTEREST_ONLY = "INTEREST-ONLY"
    BULLET_LOAN = "BULLET_LOAN"


class LoanPaymentTiming(CategorialEnum):
    ADVANCE = "ADVANCE"
    ARREARS = "ARREARS"


class LoanRoundingRules(CategorialEnum):
    ROUND_HALF_UP = "ROUND_HALF_UP"
    ROUND_HALF_DOWN = "ROUND_HALF_DOWN"
    ROUND_HALF_EVEN = "ROUND_HALF_EVEN"


class LoanYearlyDayCountConvention(CategorialEnum):
    EU = "360/360"
    OTHER = "365/365"
