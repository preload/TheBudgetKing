import flet as ft

from core.colors import *

DIRTY_TRX_COLUMNS = [
    'date',
    'authcode',
    'trx_type',
    'merchant',
    'dirty_amount',
    'amount',
    'notes',
    'category',
    'import_timestamp',
    'source',
    'clean_merchant',
    'duplicate_status',
    'icon'
]

CLEANED_TRX_COLUMNS = [
    'date',
    'authcode',
    'trx_type',
    'merchant',
    'amount',
    'notes',
    'category',
    'import_timestamp',
    'source',
    'clean_merchant',
    'duplicate_status',
    'icon'
]

CURRENCIES = [
    "AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN",
    "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BOV",
    "BRL", "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHE", "CHF",
    "CHW", "CLF", "CLP", "CNY", "COP", "COU", "CRC", "CUC", "CUP", "CVE",
    "CZK", "DJF", "DKK", "DOP", "DZD", "EGP", "ERN", "ETB", "EUR", "FJD",
    "FKP", "GBP", "GEL", "GHS", "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD",
    "HNL", "HRK", "HTG", "HUF", "IDR", "ILS", "IMP", "INR", "IQD", "IRR",
    "ISK", "JMD", "JOD", "JPY", "KES", "KGS", "KHR", "KMF", "KPW", "KRW",
    "KWD", "KYD", "KZT", "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD",
    "MDL", "MGA", "MKD", "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK",
    "MXN", "MXV", "MYR", "MZN", "NAD", "NGN", "NIO", "NOK", "NPR", "NZD",
    "OMR", "PAB", "PEN", "PGK", "PHP", "PKR", "PLN", "PYG", "QAR", "RON",
    "RSD", "RUB", "RWF", "SAR", "SBD", "SCR", "SDG", "SEK", "SGD", "SHP",
    "SLL", "SOS", "SRD", "SSP", "STN", "SVC", "SYP", "SZL", "THB", "TJS",
    "TMT", "TND", "TOP", "TRY", "TTD", "TWD", "TZS", "UAH", "UGX", "USD",
    "USN", "UYI", "UYU", "UYW", "UZS", "VES", "VND", "VUV", "WST", "XAF",
    "XCD", "XDR", "XOF", "XPF", "YER", "ZAR", "ZMW", "ZWL"
]

LOAN_COLUMNS = [
    'principal',
    'currency',
    'interest',
    'term',
    'payment_frequency',
    'amortization_type',
    'first_payment_date',
    'disbursement_date',
    'yearly_day_count_convention',
    'payment_timing',
    'recurring_mandatory_fees',
    'rounding_rules',
]

STOP_WORDS = [
    # Corporate entities (Latin & Cyrillic)
    r'EOOD', r'OOD', r'EAD', r'AD', r'ET', r'KD', r'KDA', r'SD',
    r'ЕООД', r'ООД', r'ЕАД', r'АД', r'ЕТ', r'КД', r'КДА', r'СД',
    r'LTD', r'LLC', r'PLC', r'INC', r'CORP', r'GMBH', r'AG', r'BV', r'SA', r'SRL', r'SP Z O O',

    # Transaction / Terminal / Retail markers
    r'POS', r'VPOS', r'ATM', r'OTM', r'ПОС', r'ВПОС', r'БАНКОМАТ',
    r'STORE', r'SHOP', r'MARKET', r'SUPERMARKET', r'MINIMARKET', r'HYPERMARKET',
    r'MAGAZIN', r'МАГАЗИН', r'APTEKA', r'АПТЕКА', r'BENZINOSTANTSIYA', r'БЕНЗИНОСТАНЦИЯ',
    r'RESTAURANT', r'РЕСТОРАНТ', r'FAST FOOD', r'KAFE', r'CAFE', r'BAR',
    r'PAYPAL', r'STRIPE', r'ADYEN', r'SUMUP', r'EPAY', r'EASYPAY',
    r'GOOGLE', r'APPLE', r'BILL', r'INVOICE', r'ORDER', r'TRANS', r'TRANSFER',

    # ISO Country Codes (Frequent in transaction strings)
    r'BGR', r'BG', r'IRL', r'IE', r'SWE', r'SE', r'DEU', r'DE', r'USA', r'US',
    r'POL', r'PL', r'NLD', r'NL', r'CZE', r'CZ', r'GBR', r'UK', r'LUX', r'LU',
    r'FRA', r'FR', r'ESP', r'ES', r'ITA', r'IT', r'AUT', r'AT', r'ROU', r'RO',
    r'GRC', r'GR', r'CYP', r'CY', r'SRB', r'RS', r'MKD', r'MK', r'TUR', r'TR',

    # Country & Region Names
    r'BULGARIA', r'BALGARIYA', r'БЪЛГАРИЯ',

    # Bulgarian Major Cities & Towns (Latin + Cyrillic)
    r'SOFIA', r'SOFIYA', r'СОФИЯ',
    r'PLOVDIV', r'ПЛОВДИВ',
    r'VARNA', r'ВАРНА',
    r'BURGAS', r'BOURGAS', r'БУРГАС',
    r'RUSE', r'ROUSSE', r'РУСЕ',
    r'STARA ZAGORA', r'СТАРА ЗАГОРА',
    r'PLEVEN', r'ПЛЕВЕН',
    r'SLIVEN', r'СЛИВЕН',
    r'DOBRICH', r'ДОБРИЧ',
    r'SHUMEN', r'ШУМЕН',
    r'PERNIK', r'ПЕРНИК',
    r'HASKOVO', r'ХАСКОВО',
    r'YAMBOL', r'ЯМБОЛ',
    r'PAZARDZHIK', r'PAZARDJIK', r'ПАЗАРДЖИК',
    r'BLAGOEVGRAD', r'БЛАГОЕВГРАД',
    r'VELIKO TARNOVO', r'ВЕЛИКО ТЪРНОВО',
    r'GABROVO', r'ГАБРОВО',
    r'VRATSA', r'ВРАЦА',
    r'KARDZHALI', r'KARDJALI', r'КЪРДЖАЛИ',
    r'VIDIN', r'ВИДИН',
    r'ASENOVGRAD', r'АСЕНОВГРАД',
    r'KAZANLAK', r'КАЗАНЛЪК',
    r'KYUSTENDIL', r'КЮСТЕНДИЛ',
    r'MONTANA', r'МОНТАНА',
    r'DIMITROVGRAD', r'ДИМИТРОВГРАД',
    r'LOVECH', r'ЛОВЕЧ',
    r'SILISTRA', r'СИЛИСТРА',
    r'TARGOVISHTE', r'ТЪРГОВИЩЕ',
    r'RAZGRAD', r'РАЗГРАД',
    r'SMOLYAN', r'СМОЛЯН',
    r'PETRICH', r'ПЕТРИЧ',
    r'SAMOKOV', r'САМОКОВ',
    r'SANDANSKI', r'САНДАНСКИ',
    r'SVISTOV', r'SVISHTOV', r'СВИЩОВ',
    r'BOZHURISHTE', r'БОЖУРИЩЕ',
    r'BANKYA', r'БАНКЯ',
    r'SOZOPOL', r'СОЗОПОЛ',
    r'NESSEBAR', r'NESEBAR', r'НЕСЕБЪР',
    r'BANSKO', r'БАНСКО',
    r'BELOZEM', r'БЕЛОЗЕМ',

    # Sofia Neighborhoods (frequent in POS descriptions)
    r'MLADOST', r'МЛАДОСТ',
    r'LYULIN', r'LIULIN', r'ЛЮЛИН',
    r'NADEZHDA', r'НАДЕЖДА',
    r'LOZENETS', r'ЛОЗЕНЕЦ',
    r'CENTER', r'TSENTAR', r'ЦЕНТЪР',
    r'STUDENTSKI', r'СТУДЕНТСКИ',
    r'BOROVO', r'БОРОВО',
    r'DRUZHBA', r'DRUJBA', r'ДРУЖБА',
    r'TRAYAN', r'ТРАЯН',

    # Common European Tech/Payment Headquarters
    r'DUBLIN', r'STOCKHOLM', r'SEATTLE', r'WARSZAWA', r'AMSTERDAM',
    r'BRNO', r'LONDON', r'BERLIN', r'PARIS', r'FRANKFURT', r'VILNIUS'
]

COLOR_SCHEME = ft.ColorScheme(
    primary=LIGHT_GREEN,  # main_green
    on_primary=GREY,  # blackish
    surface=WHITE,  # white
    on_surface=GREY,  # blackish
    outline=DARK_GREEN,  # darker_green
    primary_container=LIGHT_GREEN,  # main_green
    on_primary_container=GREY,  # blackish
    on_surface_variant=GREY,  # blackish

)

TEXT_THEME = ft.TextTheme(
    body_large=ft.TextStyle(color=GREY),
    body_medium=ft.TextStyle(color=GREY),
    body_small=ft.TextStyle(color=GREY),
    label_large=ft.TextStyle(color=GREY),
    title_medium=ft.TextStyle(color=GREY),
    title_large=ft.TextStyle(color=GREY),
)

TEXT_BUTTON_STYLE = ft.ButtonStyle(
    color=GREY,
    icon_color=DARK_GREEN,
    bgcolor=WHITE,
    side=ft.BorderSide(width=1, color=GREY),
    shape=ft.RoundedRectangleBorder(radius=4),
)

SELECTED_TEXT_BUTTON_STYLE = ft.ButtonStyle(
    color=GREY,
    bgcolor=MUTED_GREEN,
    icon_color=LIGHT_GREEN,
    side=ft.BorderSide(width=2, color=DARK_GREEN),
    shape=ft.RoundedRectangleBorder(radius=4),
)

CHECKBOX_THEME = ft.CheckboxTheme(
    fill_color={
        ft.ControlState.SELECTED: DARK_GREEN,
        ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
    },
    check_color={
        ft.ControlState.SELECTED: WHITE,
        ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
    },
    shape=ft.RoundedRectangleBorder(radius=4),
    border_side=ft.BorderSide(width=2, color=DARK_GREEN)
)

BUTTON_STYLE = ft.ButtonStyle(
    side=ft.BorderSide(width=1, color=GREY),
    shape=ft.RoundedRectangleBorder(radius=4),
    color=DARK_GREEN,
)

ICON_BUTTON_STYLE = ft.ButtonStyle(
    side=ft.BorderSide(width=1, color=GREY),
    shape=ft.RoundedRectangleBorder(radius=4),
    color=DARK_GREEN,
)

DATE_PICKER_THEME = ft.DatePickerTheme(
    bgcolor=WHITE,
)

NAVIGATION_BAR_THEME = ft.NavigationBarTheme(
    bgcolor=WHITE,
    elevation=4,
    indicator_color=DARK_GREEN,

)

TRX_TABLE_ROW_HEIGHT = 50
TRX_TABLE_ICON_SIZE = TRX_TABLE_ROW_HEIGHT - 4

GLOBAL_THEME = ft.Theme(
    color_scheme=COLOR_SCHEME,
    divider_theme=ft.DividerTheme(color=DARK_GREEN),
    text_theme=TEXT_THEME,
    checkbox_theme=CHECKBOX_THEME,
    data_table_theme=ft.DataTableTheme(heading_text_style=ft.TextStyle(color=GREY, weight=ft.FontWeight.BOLD)),
    date_picker_theme=DATE_PICKER_THEME,
    navigation_bar_theme=NAVIGATION_BAR_THEME,
)

