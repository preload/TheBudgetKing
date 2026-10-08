import re
from datetime import datetime

import pandas as pd
import pdfplumber

from core.constants import DIRTY_TRX_COLUMNS
from core.enums import DuplicateStatus, SourceType
from processing.trx_clean_assume_icon_authcode import apply_trx_pipeline
from processing.set_formats_validate_schemas import validate_first_trx_row


def initialize_trx_data(file_path) -> pd.DataFrame:
    try:
        trx_df = pd.read_csv(file_path)
    except FileNotFoundError:
        print("File not found.")

    return apply_trx_pipeline(trx_df)


def scrape_pdf(file_path: str) -> pd.DataFrame:
    batch_time = datetime.now().isoformat(timespec='seconds')

    # SCRAPE PDF
    with pdfplumber.open(file_path) as pdf:
        all_text = ''.join(text for page in pdf.pages if (text := page.extract_text()))

    raw_transactions = all_text.split('\n')

    ##CONSTRUCTING DATAFRAME
    pattern = re.compile(r'(\d{2}\.\d{2}\.\d{2}\s\d{2}:\d{2})(?::\d{2})?')
    transactions = []
    for i, line in enumerate(raw_transactions):
        match = pattern.search(line)
        if match:
            transactions.append({
                "date": match.group(1),
                "authcode": None,
                "trx_type": raw_transactions[i - 1] if i > 0 else "",
                "merchant": line[:match.start()].strip(),
                "amount": line[match.end():].strip(),
                "notes": None,
                "category": None,
                "import_timestamp": pd.to_datetime(batch_time),
                "source": SourceType.PDF,
                "clean_merchant": None,
                "duplicate_status": DuplicateStatus.NOT_REVIEWED,
                'icon': None
            })

    scraped_df = (
        pd.DataFrame.from_dict(transactions)
        .assign(date=lambda df: pd.to_datetime(df['date'], exact=True, format='%d.%m.%y %H:%M').dt.normalize())
        .loc[lambda df: df['trx_type'] != 'ВНОСКА']
    )

    return apply_trx_pipeline(scraped_df)


def load_from_clipboard() -> pd.DataFrame:
    df = pd.read_clipboard(header=None, names=DIRTY_TRX_COLUMNS)
    validate_first_trx_row(df)
    df['source'] = SourceType.ClipBoard
    df['import_timestamp'] = datetime.now().isoformat(timespec='seconds')
    return apply_trx_pipeline(df)


def load_from_csv(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, header=None, names=DIRTY_TRX_COLUMNS)
    validate_first_trx_row(df)
    df['source'] = SourceType.CSV
    df['import_timestamp'] = datetime.now().isoformat(timespec='seconds')
    return apply_trx_pipeline(df)
