# region HEADER
import asyncio
from datetime import datetime, timedelta

import flet as ft
import flet_datatable2 as ftd
import pandas as pd

from core.colors import *
from core.constants import ICON_BUTTON_STYLE, TRX_TABLE_ROW_HEIGHT, CHECKBOX_THEME, \
    TEXT_BUTTON_STYLE, TRX_TABLE_ICON_SIZE, BUTTON_STYLE
from tabs.components.celltext import cell_text
from tabs.components.columns import column_label

IMPORT_SOURCE_OPTIONS = ['PDF', 'CSV', 'Clipboard']
VISIBLE_TRX_COLUMNS = ['date', 'authcode', 'trx_type', 'icon', 'merchant', 'amount', 'notes', 'category']

FIELD_DEFAULTS = dict(text_size=14, max_lines=2, border=ft.InputBorder.NONE, content_padding=0, expand=True,
                      text_align=ft.TextAlign.CENTER, )
DROPDOWN_DEFAULTS = dict(bgcolor=SILVER, border_radius=4, text_size=14, content_padding=0, expand=True,
                         border=ft.InputBorder.NONE, )
# endregion

class ImportView(ft.Container):
    # region INIT
    def __init__(self, page: ft.Page):
        super().__init__(
            padding=2,
            border=ft.Border.all(width=2, color=DARK_GREEN),
            border_radius=10,
            expand=True,
            alignment=ft.Alignment.TOP_CENTER,
        )
        self._page = page

        # region UPDATE DATA
        self.date_picker = ft.DatePicker(on_change=self._set_row_date)
        self.trx_table_selected_rows: set = set()
        # endregion
        ############################################################################################################
        # region DEBOUNCE
        self._update_field_debounce_task = None
        # endregion
        ############################################################################################################
        # regionPAGINATION VARS
        self.current_page_number = 1
        self.current_page_trx_data = None
        # endregion
        ############################################################################################################
        # region SORTING VARS
        self.current_sort_column_index = 0
        self.current_sort_ascending = True
        # endregion
        ############################################################################################################
        # region MAIN TABLE
        self.trx_table = ftd.DataTable2(
            heading_row_height=30,
            horizontal_margin=10,
            data_row_checkbox_theme=CHECKBOX_THEME,
            heading_checkbox_theme=CHECKBOX_THEME,
            show_checkbox_column=True,
            expand=True,
            column_spacing=2,
            sort_arrow_icon_color=GREY,
            sort_ascending=True,
            heading_row_color=SILVER,
            columns=[ftd.DataColumn2(
                heading_row_alignment=ft.MainAxisAlignment.CENTER,
                label=column_label(column),
                on_sort=self._trx_table_sort_column
            ) for column in VISIBLE_TRX_COLUMNS],
        )
        # endregion
        ############################################################################################################
        # region MPORT VARS/ELEMENTS
        self.import_source_visible = True

        self.import_source_file_selector_button = ft.IconButton(
            ft.Icons.ATTACH_FILE,
            style=ICON_BUTTON_STYLE,
            height=48, width=48,
            visible=True,
            on_click=self._browse_to_file
        )

        self.import_source_textbox = ft.TextField(
            value='',
            label='File path:',
            expand=True,
            border_radius=4,
            content_padding=ft.Padding.symmetric(horizontal=10, vertical=8)
        )
        # endregion
        ############################################################################################################
        # region NITIAL REFRESH
        self._import_view_refresh(execute_update=False)

        # endregion
        ############################################################################################################
    # endregion
    ################################################################################################################
    # region IMPORT

    async def _browse_to_file(self, e: ft.ControlEvent):
        temp_val = await ft.FilePicker().pick_files(allow_multiple=False)
        if temp_val: self.import_source_textbox.value = temp_val[0].path

    def _import_table_fill_button_event(self, e: ft.ControlEvent) -> None:
        self.import_source_visible = not self.import_source_visible
        self._page.csm.import_trx_data(self.import_source_textbox.value)
        self._import_table_fill()
        self._import_view_refresh()

    def _import_confirmation_controls_container(self) -> ft.Container:
        import_all_confirmation_button = ft.TextButton(
            content='Upload all',
            style=TEXT_BUTTON_STYLE,
            expand=True,
            icon=ft.Icons.ALL_OUT,
            on_click=self._import_view_merge_data,
        )
        import_selected_confirmation_button = ft.TextButton(
            content='Upload selected',
            style=TEXT_BUTTON_STYLE,
            expand=True,
            icon=ft.Icons.DATA_OBJECT,
            on_click=self._import_view_merge_data_subset,
        )
        import_discard_button = ft.TextButton(
            content='Discard all',
            expand=True,
            style=TEXT_BUTTON_STYLE,
            icon=ft.Icons.DELETE,
            on_click=self._import_view_discard_imported_trxs,
        )

        return ft.Container(
            padding=2,
            alignment=ft.Alignment.BOTTOM_CENTER,
            border_radius=10,
            visible=not self.import_source_visible,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=3,
                controls=[
                    import_all_confirmation_button,
                    import_selected_confirmation_button,
                    import_discard_button,
                ]
            )
        )

    def _import_source_container(self) -> ft.Container:

        import_source_confirmation_button = ft.IconButton(
            ft.Icons.DOWNLOAD,
            style=ICON_BUTTON_STYLE,
            height=48, width=48,
            visible=True,
            on_click=self._import_table_fill_button_event
        )

        return ft.Container(
            padding=2,
            alignment=ft.Alignment.TOP_CENTER,
            visible=self.import_source_visible,
            border_radius=10,
            content=ft.Row(
                spacing=3,
                controls=[
                    self.import_source_textbox,
                    self.import_source_file_selector_button,
                    import_source_confirmation_button,
                ]
            )

        )
    # endregion
    ################################################################################################################
    # region PAGINATION

    def _trx_table_calculate_available_space(self) -> int:
        app_bar = 64
        tabs_height = 25
        page_padding = 20
        filter_box_height = 0
        table_header_height = 30
        data_row_height = TRX_TABLE_ROW_HEIGHT
        container_border = 4
        pagination_bar_height = 20
        last_row = TRX_TABLE_ROW_HEIGHT  # needs to be removed to prevent clipping on my resolution, otherwise generally not necessary
        total_overhead = sum(
            [app_bar, container_border, tabs_height, page_padding, table_header_height, pagination_bar_height,
             filter_box_height, last_row])

        return max(1, int((self._page.height - total_overhead) // data_row_height))

    def _trx_table_increment_page(self, e: ft.ControlEvent) -> None:

        space = self._trx_table_calculate_available_space()
        max_pages = self._page.csm.get_nr_of_pages_trx_data(space, self._page.csm.import_df)

        if self.current_page_number != max_pages:
            self.current_page_number += 1
            self._import_view_refresh()

    def _trx_table_last_page(self, e: ft.ControlEvent) -> None:

        space = self._trx_table_calculate_available_space()
        max_pages = self._page.csm.get_nr_of_pages_trx_data(space, self._page.csm.import_df)

        if self.current_page_number != max_pages:
            self.current_page_number = max_pages
            self._import_view_refresh()

    def _trx_table_decrement_page(self, e: ft.ControlEvent) -> None:
        if self.current_page_number != 1:
            self.current_page_number -= 1
            self._import_view_refresh()

    def _trx_table_first_page(self, e: ft.ControlEvent) -> None:
        if self.current_page_number != 1:
            self.current_page_number = 1
            self._import_view_refresh()

    def _trx_table_pagination_bar(self) -> ft.Container:
        space = self._trx_table_calculate_available_space()
        max_pages = self._page.csm.get_nr_of_pages_trx_data(space, self._page.csm.import_df)

        if self._page.csm.import_df is not None:
            if self.current_page_number > max_pages:
                self.current_page_number = max_pages
                self._import_view_refresh()

        return ft.Container(
            height=20,
            padding=1,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Button(content='<<', bgcolor=WHITE, on_click=self._trx_table_first_page,
                              style=BUTTON_STYLE),
                    ft.Button(content='<', bgcolor=WHITE, on_click=self._trx_table_decrement_page,
                              style=BUTTON_STYLE),
                    ft.Text(f"Page {self.current_page_number} of {max_pages}", size=13),
                    ft.Button(content='>', bgcolor=WHITE, on_click=self._trx_table_increment_page,
                              style=BUTTON_STYLE),
                    ft.Button(content='>>', bgcolor=WHITE, on_click=self._trx_table_last_page,
                              style=BUTTON_STYLE),
                ]
            )
        )
    # endregion
    ################################################################################################################
    # region DATA UPDATES AND MANIPULATION

    def _set_row_date(self, e: ft.ControlEvent):
        selected_date = e.control.value + timedelta(days=1)  # need timedelta due to timezone issue
        self.date_picker.data.value = selected_date.strftime('%d-%b-%Y')
        self.date_picker.data.update()

    def _open_date_picker(self, e: ft.ControlEvent):
        self.date_picker.data = e.control
        self.date_picker.current_date = datetime.strptime(e.control.value, '%d-%b-%Y')
        self._page.show_dialog(self.date_picker)

    def _highlight_trx_row(self, trx_id: str, e: ft.ControlEvent):
        if not e.control.selected:
            self.trx_table_selected_rows.add(trx_id)
        else:
            self.trx_table_selected_rows.discard(trx_id)
        e.control.selected = not e.control.selected

    async def _field_update_debounce_refresher(self, e: ft.ControlEvent) -> None:
        await asyncio.sleep(0.4)
        self._import_trx_table_on_field_change(e)

    def _trx_field_update(self, e: ft.ControlEvent) -> None:
        if self._update_field_debounce_task: self._update_field_debounce_task.cancel()
        self._update_field_debounce_task = asyncio.create_task(self._field_update_debounce_refresher(e))

    def _import_trx_table_on_field_change(self, e: ft.ControlEvent):
        dataframe = self._page.csm.import_df
        new_val = e.control.value
        authcode, column = e.control.data

        self._page.csm.import_df = self._page.csm.update_trx_field(
            authcode=authcode,
            column=column,
            value=new_val,
            dataframe=dataframe,
        )
        if column == 'merchant': self._import_view_refresh()
    # endregion
    ################################################################################################################
    # region SORTING

    def _trx_table_apply_sort(self) -> None:
        sorter_column_name = VISIBLE_TRX_COLUMNS[self.current_sort_column_index]
        self._page.csm.import_df.sort_values(by=sorter_column_name, ascending=self.current_sort_ascending,
                                             inplace=True, kind='mergesort')

    def _trx_table_sort_column(self, e: ft.DataColumnSortEvent) -> None:
        self.current_sort_column_index = e.column_index
        print(f'[_trx_table_sort_column] called for column {VISIBLE_TRX_COLUMNS[self.current_sort_column_index]}')
        self.current_sort_ascending = e.ascending
        self._import_view_refresh()
    # endregion
    ################################################################################################################
    # region MAIN TABLE

    def _import_table_fill(self) -> None:
        rows = []

        space = self._trx_table_calculate_available_space()
        unique_categories = self._page.csm.get_unique_categories()

        self.current_page_trx_data = self._page.csm.get_paginated_trx_data(
            page_nr=self.current_page_number,
            page_size=space,
            data=self._page.csm.import_df,
        )

        def make_data_cell(row, col):

            if pd.isna(getattr(row, col)):
                cell_value = ''
            elif col == 'date':
                cell_value = getattr(row, col).strftime('%d-%b-%Y').strip(' 00:00:00')
            elif col == 'amount':
                cell_value = f'{getattr(row, col):.2f}'
            else:
                cell_value = str(getattr(row, col))

            if col == 'date':
                return ft.DataCell(
                    content=ft.TextField(
                        **FIELD_DEFAULTS,
                        value=cell_value,
                        data=(getattr(row, 'authcode'), col),
                        on_click=self._open_date_picker,
                        read_only=True,
                        mouse_cursor=ft.MouseCursor.CLICK,
                        on_change=self._trx_field_update,
                    )
                )
            elif col == 'authcode':
                return ft.DataCell(
                    cell_text(cell_value)
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
                    content=ft.SafeArea(
                        ft.Dropdown(
                            **DROPDOWN_DEFAULTS,
                            data=(getattr(row, 'authcode'), col),
                            value='Other',
                            on_select=self._trx_field_update,
                            options=[ft.DropdownOption(key=value, text=value) for value in unique_categories],
                        )
                    )
                )
            elif col == 'amount':
                return ft.DataCell(
                    content=ft.TextField(
                        **FIELD_DEFAULTS,
                        value=cell_value,
                        data=(getattr(row, 'authcode'), col),
                        on_change=self._trx_field_update,
                        input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d{0,2}$"),
                    )
                )
            else:
                return ft.DataCell(
                    content=ft.TextField(
                        **FIELD_DEFAULTS,
                        value=cell_value if cell_value != 'nan' else '',
                        data=(getattr(row, 'authcode'), col),
                        on_change=self._trx_field_update,
                    )
                )

        for row in self.current_page_trx_data.itertuples():
            rows.append(
                ftd.DataRow2(
                    specific_row_height=TRX_TABLE_ROW_HEIGHT,
                    on_select_change=lambda e, trx_id=getattr(row, 'authcode'): self._highlight_trx_row(trx_id, e),
                    cells=[make_data_cell(row, col) for col in VISIBLE_TRX_COLUMNS]
                )
            )

        self.trx_table.rows = rows

    def _import_view_refresh(self, execute_update: bool = True):

        self.trx_table.sort_column_index = self.current_sort_column_index
        self.trx_table.sort_ascending = self.current_sort_ascending

        if self._page.csm.import_df is not None:
            self._trx_table_apply_sort()

        self._import_table_fill()

        self.content = ft.Column(
            [
                self._import_source_container(),
                self._import_confirmation_controls_container(),
                self.trx_table,
                self._trx_table_pagination_bar(),

            ]
        )

        if execute_update: self.update()
    # endregion
    ################################################################################################################
    # region FINALIZE DATA

    def _import_view_merge_data(self):
        self._page.csm.merge_trx_data()

    def _import_view_merge_data_subset(self):
        self._page.csm.merge_subset_trx_data(self.trx_table_selected_rows)

    def _import_view_discard_imported_trxs(self):
        self._page.csm.import_df = None
        self.import_source_visible = True
        self.trx_table.rows.clear()
        self._import_view_refresh()
    # endregion
    ################################################################################################################