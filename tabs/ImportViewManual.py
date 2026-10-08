from datetime import datetime, timedelta

import flet as ft
import flet_datatable2 as ftd
import pandas as pd

from core.colors import *
from core.constants import TEXT_BUTTON_STYLE, TRX_TABLE_ROW_HEIGHT, CHECKBOX_THEME, TRX_TABLE_ICON_SIZE
from core.enums import DuplicateStatus, SourceType
from tabs.components.columns import centered_column

VISIBLE_TRX_COLUMNS = ['date', 'authcode', 'trx_type', 'icon', 'merchant', 'amount', 'notes', 'category']


class ImportViewManual(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(
            padding=2,
            border=ft.Border.all(width=2, color=DARK_GREEN),
            border_radius=10,
            expand=True,
            alignment=ft.Alignment.TOP_CENTER,
        )
        self._page = page

        self.trx_table = ftd.DataTable2(
            heading_row_height=30,
            horizontal_margin=10,
            data_row_checkbox_theme=CHECKBOX_THEME,
            heading_checkbox_theme=CHECKBOX_THEME,
            show_checkbox_column=True,
            column_spacing=2,
            sort_arrow_icon_color=GREY,
            sort_ascending=True,
            heading_row_color=SILVER,
            columns=[centered_column(column) for column in VISIBLE_TRX_COLUMNS],
        )

        self.add_row_button = ft.IconButton(
            ft.Icons.ADD,
            expand=True,
            on_click=lambda _: self._page.show_dialog(self.new_row_dialog),
        )

        self.new_row_date_field = ft.TextField(
            label='Date',
            prefix_icon=ft.IconButton(
                ft.Icons.CALENDAR_MONTH,
                on_click=lambda _: self._page.show_dialog(self.date_picker),
            ),
        )
        self.new_row_authcode_field = ft.TextField(label='Authcode', tooltip='Unique identifier for the transaction.\n'
                                                                             'Leave blank if unknown.\n'
                                                                             'A value will be auto-assigned')
        self.new_row_trx_type_field = ft.Dropdown(
            bgcolor=SILVER,
            border_radius=4,
            enable_filter=True,
            editable=True,
            text_size=14,
            expand=True,
            label='Type',
            options=[ft.DropdownOption(key=value, text=value) for value in
                     self._page.csm.get_unique_values('trx_type')]
        )

        self.new_row_merchant_field = ft.TextField(label='Merchant')

        self.new_row_amount_field = ft.TextField(label='Amount',
                                                 input_filter=ft.InputFilter(allow=True,
                                                                             regex_string=r"^\d*\.?\d{0,2}$"), )
        self.new_row_notes_field = ft.TextField(label='Notes')

        self.new_row_category_field = ft.Dropdown(
            bgcolor=SILVER,
            border_radius=4,
            enable_filter=True,
            editable=True,
            menu_height=450,
            text_size=14,
            expand=True,
            label='Category',
            options=[ft.DropdownOption(key=value, text=value) for value in
                     self._page.csm.get_unique_categories()]
        )

        self.new_row_dialog = ft.AlertDialog(
            title=ft.Text("New row", color=GREY),
            bgcolor=WHITE,
            open=False,
            modal=True,
            actions=[
                ft.TextButton("Add row", style=TEXT_BUTTON_STYLE, on_click=self._add_row_to_table),
                ft.TextButton("Cancel", style=TEXT_BUTTON_STYLE, on_click=self._clear_new_row_fields),
            ],
            content=ft.SafeArea(
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    height=400,
                    controls=[
                        ft.Row(controls=[self.new_row_date_field]),
                        ft.Row(controls=[self.new_row_authcode_field]),
                        ft.Row(controls=[self.new_row_trx_type_field]),
                        ft.Row(controls=[self.new_row_merchant_field]),
                        ft.Row(controls=[self.new_row_amount_field]),
                        ft.Row(controls=[self.new_row_notes_field]),
                        ft.Row(controls=[self.new_row_category_field]),
                    ]
                ),
            )
        )

        self.date_picker = ft.DatePicker(on_change=self._set_row_date)

        self._manual_import_view_refresh(execute_update=False)

    def _clear_new_row_fields(self):
        self._page.pop_dialog()
        self.new_row_date_field.value = ''
        self.new_row_authcode_field.value = ''
        self.new_row_trx_type_field.value = ''
        self.new_row_merchant_field.value = ''
        self.new_row_amount_field.value = ''
        self.new_row_notes_field.value = ''
        self.new_row_category_field.value = ''

    def _set_row_date(self, e: ft.ControlEvent):
        selected_date = e.control.value + timedelta(days=1)  # need timedelta due to timezone issue
        self.new_row_date_field.value = selected_date.strftime('%d-%b-%Y')

    def _add_row_to_table(self):
        self._page.pop_dialog()
        date = datetime.strptime(self.new_row_date_field.value, '%d-%b-%Y')
        authcode = self.new_row_authcode_field.value if self.new_row_authcode_field.value else None
        trx_type = self.new_row_trx_type_field.value
        merchant = self.new_row_merchant_field.value
        amount = float(self.new_row_amount_field.value)
        notes = self.new_row_notes_field.value
        category = self.new_row_category_field.value
        import_timestamp = datetime.now().isoformat(timespec='seconds')
        source = SourceType.MANUAL
        clean_merchant = None
        duplicate_status = DuplicateStatus.NOT_REVIEWED
        icon = None

        row = [date, authcode, trx_type, merchant, amount, notes, category, import_timestamp, source, clean_merchant,
               duplicate_status, icon]
        print(f'[_add_row_to_table] row: {row}')

        self._page.csm.add_manual_df_row(row)
        self._clear_new_row_fields()
        self._manual_import_view_refresh()

    def _import_table_fill(self) -> None:

        rows = []
        data = self._page.csm.manual_df
        if data is None:
            self.trx_table.rows = rows
            return
        else:
            data = self._page.csm.manual_df.itertuples()

        def make_data_cell(row, col):
            if pd.isna(getattr(row, col)):
                cell_text = ''
            elif col == 'date':
                cell_text = getattr(row, col).strftime('%d-%b-%Y')
            else:
                cell_text = str(getattr(row, col))

            if col == 'date':
                return ft.DataCell(
                    content=ft.TextField(
                        value=cell_text.strip(' 00:00:00'),
                        text_size=14,
                        max_lines=3,
                        data=(getattr(row, 'authcode'), col),
                        border=ft.InputBorder.NONE,
                        # on_click=self._open_date_picker,
                        content_padding=0,
                        # on_change=self._import_trx_table_on_field_change,
                        input_filter=ft.InputFilter(allow=True, regex_string=r"^\d{4}-\d{2}-\d{2}$"),
                        text_align=ft.TextAlign.CENTER,
                    )
                )
            elif col == 'authcode':
                return ft.DataCell(
                    content=ft.Text(
                        value=cell_text,
                        size=14,
                        max_lines=2,
                        expand=True,
                        text_align=ft.TextAlign.CENTER,
                    )
                )
            elif col == 'icon':
                return ft.DataCell(
                    content=ft.Container(
                        content=(
                            ft.Image(src=getattr(row, 'icon'), width=TRX_TABLE_ICON_SIZE,
                                     height=TRX_TABLE_ICON_SIZE, color=GREY)
                            if row.icon.startswith('<svg') else ft.Icon(ft.Icons.STORE, color=GREY,
                                                                        size=TRX_TABLE_ICON_SIZE)
                        ),
                        alignment=ft.Alignment.CENTER,
                        border_radius=4,
                    )
                )
            elif col == 'category':
                return ft.DataCell(
                    content=ft.Dropdown(
                        bgcolor=SILVER,
                        border_radius=4,
                        text_size=14,
                        data=(getattr(row, 'authcode'), col),
                        border=ft.InputBorder.NONE,
                        enable_filter=True,
                        content_padding=0,
                        editable=True,
                        value=getattr(row, 'category'),
                        # on_select=self._import_trx_table_on_field_change,
                        expand=True,
                        options=[ft.DropdownOption(key=value, text=value) for value in
                                 self._page.csm.get_unique_categories()],
                    )
                )
            elif col == 'amount':
                return ft.DataCell(
                    content=ft.TextField(
                        value=cell_text if cell_text != 'nan' else '',
                        text_size=14,
                        max_lines=3,
                        data=(getattr(row, 'authcode'), col),
                        # on_change=self._import_trx_table_on_field_change,
                        border=ft.InputBorder.NONE,
                        content_padding=0,
                        expand=True,
                        input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d{0,2}$"),
                        text_align=ft.TextAlign.CENTER,
                    )
                )
            else:
                return ft.DataCell(
                    content=ft.TextField(
                        value=cell_text if cell_text != 'nan' else '',
                        text_size=14,
                        max_lines=2,
                        expand=True,
                        data=(getattr(row, 'authcode'), col),
                        # on_change=self._import_trx_table_on_field_change,
                        border=ft.InputBorder.NONE,
                        content_padding=0,
                        text_align=ft.TextAlign.CENTER,
                    )
                )

        for row in data:
            rows.append(
                ftd.DataRow2(
                    specific_row_height=TRX_TABLE_ROW_HEIGHT,
                    cells=[make_data_cell(row, col) for col in VISIBLE_TRX_COLUMNS]
                )
            )

        self.trx_table.rows = rows

    def _manual_import_view_refresh(self, execute_update: bool = True):

        self._import_table_fill()

        self.content = ft.Column(
            [
                ft.Column(
                    [
                        self.trx_table,
                        ft.Row(controls=[self.add_row_button], alignment=ft.MainAxisAlignment.CENTER),
                    ],
                    expand=True,
                ),
                self._import_confirmation_controls_container(),
            ]
        )

        if execute_update: self.update()

    def _import_view_merge_data(self):
        self._page.csm.merge_trx_data(self._page.csm.manual_df)
        self._page.csm.manual_df = None
        self.trx_table.rows.clear()

    def _import_view_discard_imported_trxs(self):
        self._page.csm.manual_df = None
        self.trx_table.rows.clear()

    def _import_confirmation_controls_container(self) -> ft.Container:
        import_all_confirmation_button = ft.TextButton(
            content='Upload',
            style=TEXT_BUTTON_STYLE,
            icon=ft.Icons.ALL_OUT,
            on_click=self._import_view_merge_data,
        )

        import_discard_button = ft.TextButton(
            content='Discard',
            style=TEXT_BUTTON_STYLE,
            icon=ft.Icons.DELETE,
            on_click=self._import_view_discard_imported_trxs,
        )

        return ft.Container(
            padding=10,
            alignment=ft.Alignment.BOTTOM_CENTER,
            border_radius=10,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    import_all_confirmation_button,
                    import_discard_button,
                ]
            )
        )
