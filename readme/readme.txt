### `main.py`
*   **placeholder_budget_chart**
*   **placeholder_home_overview_tab**
*   **create_navigation_bar**
*   **create_app_bar**
*   **create_tab_bar**
*   **main**
*   **main_view**
*   **import_view**
*   **budget_view**
*   **loan_view**
*   **trx_view**

### `csm.py`
*   **Class: CentralStateManager**
    *   __init__
    *   get_trx_data
    *   get_trx_data_date_mask
    *   get_trx_data_amount_mask
    *   get_paginated_trx_data
    *   get_nr_of_pages_trx_data
    *   get_duplicate_trx_data
    *   get_unique_categories
    *   get_unique_values
    *   add_manual_df_row
    *   update_trx_field
    *   import_trx_data
    *   save_trx_data
    *   get_trx_row
    *   merge_trx_data
    *   merge_subset_trx_data
    *   drop_row

### `core/enums.py`
*   **Class: CategorialEnum**
    *   dtype
*   **Class: DuplicateStatus**
*   **Class: SourceType**
*   **Class: LoanPaymentFrequency**
*   **Class: LoanAmortizationType**
*   **Class: LoanPaymentTiming**
*   **Class: LoanRoundingRules**
*   **Class: LoanYearlyDayCountConvention**

### `ingestion/trx_init_scrape_import.py`
*   **initialize_trx_data**
*   **scrape_pdf**
*   **load_from_clipboard**
*   **load_from_csv**

### `tabs/ImportViewManual.py`
*   **Class: ImportViewManual**
    *   __init__
    *   _clear_new_row_fields
    *   _set_row_date
    *   _add_row_to_table
    *   _import_table_fill
    *   _manual_import_view_refresh
    *   _import_view_merge_data
    *   _import_view_discard_imported_trxs
    *   _import_confirmation_controls_container

### `tabs/ImportViewFromFile.py`
*   **Class: ImportView**
    *   __init__
    *   _import_table_fill_button_event
    *   _import_confirmation_controls_container
    *   _import_source_container
    *   _trx_table_calculate_available_space
    *   _trx_table_increment_page
    *   _trx_table_last_page
    *   _trx_table_decrement_page
    *   _trx_table_first_page
    *   _trx_table_pagination_bar
    *   _set_row_date
    *   _open_date_picker
    *   _highlight_trx_row
    *   _trx_field_update
    *   _import_trx_table_on_field_change
    *   _trx_table_apply_sort
    *   _trx_table_sort_column
    *   _import_table_fill
    *   _import_view_refresh
    *   _import_view_merge_data
    *   _import_view_merge_data_subset
    *   _import_view_discard_imported_trxs

### `tabs/TrxViewOverviewTab.py`
*   **Class: TrxViewOverviewTab**
    *   __init__
    *   did_mount
    *   will_unmount
    *   _trx_table_calculate_available_space
    *   _on_table_area_resize
    *   _trx_view_overview_tab_resize
    *   _trx_table_filter_box
    *   _trx_table_filter_textbox_change
    *   _trx_table_filter_apply
    *   _set_filter_start_date
    *   _set_filter_end_date
    *   _start_date_open_datepicker
    *   _end_dade_open_datepicker
    *   _trx_table_apply_sort
    *   _trx_table_sort_column
    *   _trx_table_increment_page
    *   _trx_table_last_page
    *   _trx_table_decrement_page
    *   _trx_table_first_page
    *   _trx_table_pagination_bar
    *   _trx_table_change_category
    *   _handle_item_click
    *   _open_context_menu
    *   _context_menu_delete_row
    *   _update_box_handler
    *   _context_menu_edit_row
    *   _highlight_trx_row
    *   _trx_table_fill
    *   _trx_table_refresh

### `tabs/components/columns.py`
*   **column_label**
*   **centered_column**

### `tabs/components/celltext.py`
*   **cell_text**

### `models/loan_class.py`
*   **Class: LoanRecord**
    *   __post_init__
    *   calculate_monthly_payment_amount
    *   calculate_principal_payment_for_specific_month
    *   calculate_interest_payment_for_specific_month
    *   calculate_period_of_loan
    *   calculate_interest_of_loan
    *   calculate_loan_principal

### `processing/trx_clean_assume_icon_authcode.py`
*   **make_clean_trx_merchant**
*   **assume_trx_categories**
*   **make_trx_icon**
*   **_make_trx_authcodes**
*   **apply_trx_pipeline**

### `processing/loan_init_create_df.py`
*   **initialize_loans**
*   **create_loan_df**

### `processing/trx_merge_duplicates.py`
*   **merge_transactions**
*   **_mark_duplicates**

### `processing/set_formats_validate_schemas.py`
*   **set_trx_formats**
*   **validate_first_trx_row**
*   **validate_trx_schema**
*   **set_loan_formats**
*   **validate_loan_schema**

