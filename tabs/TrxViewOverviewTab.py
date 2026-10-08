# region HEADER
import asyncio
import math
import time
from datetime import timedelta

import flet as ft
import flet.canvas as cv
import flet_datatable2 as ftd
import pandas as pd

from core.colors import *
from core.constants import BUTTON_STYLE, ICON_BUTTON_STYLE, TRX_TABLE_ROW_HEIGHT, TRX_TABLE_ICON_SIZE, TEXT_BUTTON_STYLE
from tabs.components.columns import column_label

COLUMN_HEADERS = ['date', 'merchant', 'amount', 'notes', 'category']
FIELD_DEFAULTS = dict(text_size=14, max_lines=2, border=ft.InputBorder.NONE, content_padding=0, expand=True,
                      text_align=ft.TextAlign.CENTER, read_only=True, mouse_cursor=ft.MouseCursor.CLICK,
                      enable_interactive_selection=False, )
TEXT_DEFAULTS = dict(size=14, max_lines=2, text_align=ft.TextAlign.CENTER, expand=True)
DROPDOWN_DEFAULTS = dict(bgcolor=SILVER, border_radius=4, text_size=14, content_padding=0, expand=True,
                         border=ft.InputBorder.NONE, )
PAGINATION_BAR_HEIGHT = 25


# endregion

class TrxViewOverviewTab(ft.Container):
    # region INIT
    def __init__(self, page: ft.Page):
        super().__init__(
            padding=2,
            border=ft.Border.all(width=2, color=DARK_GREEN),
            border_radius=10,
            expand=True,
            alignment=ft.Alignment.CENTER,
            bgcolor=SILVER,
        )
        self._page = page

        # region PAGINATION VARS

        self.current_page_number = 1
        self.current_page_trx_data = None
        self.current_filtered_trx_data = None
        # endregion
        ############################################################################################################
        # region SORTING VARS

        self.current_sort_column_index = 0
        self.current_sort_ascending = False
        # endregion
        ############################################################################################################
        # region MAIN TABLE

        self.trx_table = ftd.DataTable2(
            heading_row_height=30,
            horizontal_margin=10,
            expand=True,
            column_spacing=0,
            sm_ratio=0.4,
            lm_ratio=1.5,
            bgcolor=WHITE,
            sort_arrow_icon_color=GREY,
            sort_ascending=True,
            heading_row_color=SILVER,
            columns=[ftd.DataColumn2(
                heading_row_alignment=ft.MainAxisAlignment.CENTER,
                label=column_label(column),
                on_sort=self._trx_table_sort_column
            ) for column in COLUMN_HEADERS],
        )
        # endregion
        ############################################################################################################
        # region UPDATE BOX VARS AND COMPONENTS

        self.date_picker = ft.DatePicker()
        self.trx_table_selected_rows = set()

        self.context_menu = ft.BottomSheet(
            content=ft.Container(
                padding=10,
                content=ft.SafeArea(
                    ft.Column(
                        tight=True,
                        controls=[
                            ft.ListTile(title=ft.Text("Edit"), on_click=self._context_menu_edit_row),
                            ft.ListTile(title=ft.Text("Delete"), on_click=self._context_menu_delete_row),
                        ]
                    )
                )
            )
        )
        self._page.overlay.append(self.context_menu)
        self.context_menu_send_update_button = ft.TextButton(
            "Update",
            style=TEXT_BUTTON_STYLE
        )
        self.update_box = ft.AlertDialog(
            title=ft.Text("Edit transaction", color=GREY),
            bgcolor=WHITE,
            open=False,
            modal=False,
            scrollable=True,
            actions=[
                self.context_menu_send_update_button,
                ft.TextButton("Cancel", style=TEXT_BUTTON_STYLE, on_click=self._page.pop_dialog),
            ],

        )

        # endregion
        ############################################################################################################
        # region FILTERING VARS AND COMPONENTS

        def clear_search(e):
            setattr(self.filter_textbox_string_search, 'value', '')
            self.filter_textbox_string_search.update()
            self._trx_table_filter_textbox_change(e)

        self.filter_textbox_string_search = ft.TextField(
            label='Search string',
            expand=True,
            value='',
            height=48,
            prefix_icon=ft.Icons.SEARCH,
            suffix_icon=ft.IconButton(
                ft.Icons.CLEAR,
                on_click=clear_search
            ),
            on_change=self._trx_table_filter_textbox_change,
            border_radius=4,
            content_padding=ft.Padding.symmetric(horizontal=10, vertical=8))

        self.filter_dropdown_string_search = ft.Dropdown(
            bgcolor=SILVER,
            border_radius=4,
            enable_filter=True,
            on_select=self._trx_table_filter_textbox_change,
            value='',
            editable=False,
            expand=True,
            label='Search by column',
            options=[ft.DropdownOption(key=value, text=value) for value in
                     ['All', 'Category', 'Merchant']],
        )

        self.filter_dropdown_amount_comparator = ft.Dropdown(
            bgcolor=SILVER,
            border_radius=4,
            expand=True,
            enable_filter=True,
            on_select=self._trx_table_filter_textbox_change,
            editable=False,
            label='Comparison operator',
            options=[ft.DropdownOption(key=value, text=value) for value in
                     ['Bigger Than', 'Smaller Than', 'Equals']],
        )

        self.filter_textbox_amount = ft.TextField(
            label='Amount',
            expand=True,
            height=48,
            on_change=self._trx_table_filter_textbox_change,
            border_radius=4,
            prefix_icon=ft.Icons.EURO,
            content_padding=ft.Padding.symmetric(horizontal=10, vertical=8)
        )

        self.filter_textbox_start_date = ft.TextField(
            label="Start Date",
            expand=True,
            height=48,
            on_change=self._trx_table_filter_textbox_change,
            prefix_icon=ft.IconButton(
                ft.Icons.CALENDAR_MONTH,
                on_click=self._start_date_open_datepicker,
            ),
            border_radius=4,
            content_padding=ft.Padding.symmetric(horizontal=10, vertical=8)
        )

        self.filter_textbox_end_date = ft.TextField(
            label="End Date",
            expand=True,
            height=48,
            prefix_icon=ft.IconButton(
                ft.Icons.CALENDAR_MONTH,
                on_click=self._end_dade_open_datepicker,
            ),
            on_change=self._trx_table_filter_textbox_change,
            border_radius=4,
            content_padding=ft.Padding.symmetric(horizontal=10, vertical=8)
        )

        self.visible_filter_rows = 0
        self.filter_container = self._trx_table_filter_box()
        self._start_date_datepicker = ft.DatePicker(on_change=self._set_filter_start_date)
        self._end_date_datepicker = ft.DatePicker(on_change=self._set_filter_end_date)

        # endregion
        ############################################################################################################
        # region RESIZING VARS AND COMPONENTS

        self.table_size_probe = cv.Canvas(
            left=0,
            right=0,
            top=0,
            bottom=0,
            on_resize=self._on_table_area_resize,
        )

        self.table_height = 400
        self.table_overhead = 0
        self._resize_debounce_task = None

        # endregion
        ############################################################################################################
        # region INTIAL REFRESH
        self._trx_table_refresh(execute_update=False)
        # endregion
        ############################################################################################################

    # endregion
    ################################################################################################################
    # region RESIZING

    def did_mount(self):
        self._page.on_resize = self._trx_view_overview_tab_resize

    def will_unmount(self):
        if self._page.on_resize == self._trx_view_overview_tab_resize: self._page.on_resize = None
        if self._resize_debounce_task: self._resize_debounce_task.cancel()

    def _trx_table_calculate_available_space(self) -> int:
        filter_row_height = 58
        additional_margin_of_error = 24
        total_overhead = self.table_overhead + self.visible_filter_rows * filter_row_height + additional_margin_of_error
        return max(1, int((self._page.height - total_overhead) // TRX_TABLE_ROW_HEIGHT))

    def _on_table_area_resize(self, e: ft.canvas.CanvasResizeEvent):
        print(f'[_on_table_area_resize] fired, height={e.height}')
        self.table_height = e.height
        self.table_overhead = self._page.height - e.height
        print('[_on_table_area_resize] self.table_overhead:', self.table_overhead)
        if self._resize_debounce_task: self._resize_debounce_task.cancel()
        self._resize_debounce_task = asyncio.create_task(self._trx_table_debounce_refresh())

    def _trx_view_overview_tab_resize(self, e: ft.ControlEvent) -> None:
        if self._resize_debounce_task: self._resize_debounce_task.cancel()
        self._resize_debounce_task = asyncio.create_task(self._trx_table_debounce_refresh())

    async def _trx_table_debounce_refresh(self) -> None:
        await asyncio.sleep(0.25)
        print(f'[debounce] probe reports height={self.table_height}')
        self._trx_table_refresh()

    # endregion
    ################################################################################################################
    # region FILTERING

    def _trx_table_filter_box(self) -> ft.Container:

        enable_filters_button = ft.TextButton(
            content='',
            height=25,
            expand=True,
            style=TEXT_BUTTON_STYLE,
            icon=ft.Icons.FILTER_LIST,
            icon_color=GREY,
        )

        row1: ft.Row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            visible=False,
            spacing=5,
            controls=[
                self.filter_textbox_string_search,
                self.filter_dropdown_string_search,
                bt1_add := ft.TextButton(
                    content='Add Filter',
                    icon=ft.Icons.ADD,
                    style=ft.ButtonStyle(
                        side=ft.BorderSide(width=1, color=ft.Colors.TRANSPARENT),
                        shape=ft.RoundedRectangleBorder(radius=4),
                        color=DARK_GREEN,
                    ),
                    height=48,
                ),
            ]
        )

        row2: ft.Row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
            visible=False,
            controls=[
                self.filter_dropdown_amount_comparator,
                self.filter_textbox_amount,
                bt2_remove := ft.IconButton(ft.Icons.DELETE, style=ICON_BUTTON_STYLE, height=48, width=48),
                bt2_add := ft.IconButton(ft.Icons.ADD, style=ICON_BUTTON_STYLE, height=48, width=48),
            ]
        )

        row3: ft.Row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
            visible=False,
            controls=[
                self.filter_textbox_start_date,
                self.filter_textbox_end_date,
                bt3_remove := ft.IconButton(ft.Icons.DELETE, style=ICON_BUTTON_STYLE, height=48, width=48),
                bt3_add := ft.IconButton(ft.Icons.ADD, style=ICON_BUTTON_STYLE, height=48, width=48, disabled=True),
            ]
        )

        def hide_filters(e: ft.ControlEvent):
            if row1.visible:
                setattr(row1, 'visible', False)
                setattr(self.filter_textbox_string_search, 'value', '')
                setattr(self.filter_dropdown_string_search, 'value', '')
                self.visible_filter_rows -= 1
                e.control.icon = ft.Icons.FILTER_LIST
            else:
                self.visible_filter_rows = 1
                row1.visible = True
                e.control.icon = ft.Icon(
                    ft.Icons.FILTER_LIST,
                    color=GREY,
                    rotate=ft.Rotate(angle=math.radians(180), alignment=ft.Alignment.CENTER)
                )
            if row2.visible:
                setattr(row2, 'visible', False)
                setattr(self.filter_dropdown_amount_comparator, 'value', '')
                setattr(self.filter_textbox_amount, 'value', '')
                self.visible_filter_rows -= 1
                e.control.icon = ft.Icons.FILTER_LIST
            if row3.visible:
                setattr(row3, 'visible', False)
                setattr(self.filter_textbox_start_date, 'value', '')
                setattr(self.filter_textbox_end_date, 'value', '')
                self.visible_filter_rows -= 1
                e.control.icon = ft.Icons.FILTER_LIST

            self._trx_table_refresh()

        def hide_row3(e: ft.ControlEvent):
            if row3.visible == True:
                setattr(row3, 'visible', False)
                setattr(self.filter_textbox_start_date, 'value', '')
                setattr(self.filter_textbox_end_date, 'value', '')
                self.visible_filter_rows -= 1
                self._trx_table_refresh()

        def hide_row2(e: ft.ControlEvent):
            if row2.visible == True:
                setattr(row2, 'visible', False)
                setattr(self.filter_dropdown_amount_comparator, 'value', '')
                setattr(self.filter_textbox_amount, 'value', '')
                self.visible_filter_rows -= 1
                self._trx_table_refresh()

        def show_row2(e: ft.ControlEvent):
            if row2.visible == False:
                setattr(row2, 'visible', True)
                self.visible_filter_rows += 1
                self._trx_table_refresh()

        def show_row3(e: ft.ControlEvent):
            if row3.visible == False:
                self.visible_filter_rows += 1
                setattr(row3, 'visible', True)
                self._trx_table_refresh()

        enable_filters_button.on_click = hide_filters
        bt1_add.on_click = show_row2
        bt2_add.on_click = show_row3
        bt2_remove.on_click = hide_row2
        bt3_remove.on_click = hide_row3

        return ft.Container(
            padding=2,
            border_radius=10,
            expand=False,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(controls=enable_filters_button),
                    row1,
                    row2,
                    row3,
                ]
            )
        )

    def _trx_table_filter_textbox_change(self, e: ft.ControlEvent) -> None:
        all_tbs = "".join([self.filter_textbox_string_search.value, self.filter_textbox_start_date.value,
                           self.filter_textbox_end_date.value, self.filter_textbox_amount.value])

        self._page.run_thread(self._trx_table_filter_apply, all_tbs)

    def _trx_table_filter_apply(self, captured_text: str) -> None:
        time.sleep(0.5)
        all_tbs = "".join([self.filter_textbox_string_search.value, self.filter_textbox_start_date.value,
                           self.filter_textbox_end_date.value, self.filter_textbox_amount.value])
        if all_tbs != captured_text:
            return

        self.current_page_number = 1
        self._trx_table_refresh()

    def _set_filter_start_date(self, e: ft.ControlEvent) -> None:
        seleted_date = e.control.value + timedelta(days=1)
        self.filter_textbox_start_date.value = seleted_date.strftime('%d-%b-%Y')
        self._trx_table_filter_textbox_change(e)
        self.filter_textbox_start_date.update()

    def _set_filter_end_date(self, e: ft.ControlEvent):
        selected_date = e.control.value + timedelta(days=1)
        self.filter_textbox_end_date.value = selected_date.strftime('%d-%b-%Y')
        self._trx_table_filter_textbox_change(e)
        self.filter_textbox_end_date.update()

    def _start_date_open_datepicker(self, e: ft.ControlEvent) -> None:
        self._page.show_dialog(self._start_date_datepicker)

    def _end_dade_open_datepicker(self, e: ft.ControlEvent) -> None:
        self._page.show_dialog(self._end_date_datepicker)

    # endregion
    ################################################################################################################
    # region SORTING
    def _trx_table_apply_sort(self) -> None:
        sorter_column_name = COLUMN_HEADERS[self.current_sort_column_index]
        self.current_filtered_trx_data.sort_values(by=sorter_column_name, ascending=self.current_sort_ascending,
                                                   inplace=True)

    def _trx_table_sort_column(self, e: ft.DataColumnSortEvent) -> None:
        self.current_sort_column_index = e.column_index
        self.current_sort_ascending = e.ascending
        self._trx_table_refresh(apply_filters=False)

    # endregion
    ################################################################################################################
    # region PAGINATION

    def _trx_table_increment_page(self, e: ft.ControlEvent) -> None:

        space = self._trx_table_calculate_available_space()
        max_pages = self._page.csm.get_nr_of_pages_trx_data(space, self.current_filtered_trx_data)

        if self.current_page_number != max_pages:
            self.current_page_number += 1
            self._trx_table_refresh()

    def _trx_table_last_page(self, e: ft.ControlEvent) -> None:

        space = self._trx_table_calculate_available_space()
        max_pages = self._page.csm.get_nr_of_pages_trx_data(space, self.current_filtered_trx_data)

        if self.current_page_number != max_pages:
            self.current_page_number = max_pages
            self._trx_table_refresh()

    def _trx_table_decrement_page(self, e: ft.ControlEvent) -> None:
        if self.current_page_number != 1:
            self.current_page_number -= 1
            self._trx_table_refresh()

    def _trx_table_first_page(self, e: ft.ControlEvent) -> None:
        if self.current_page_number != 1:
            self.current_page_number = 1
            self._trx_table_refresh()

    def _trx_table_pagination_bar(self) -> ft.Container:
        space = self._trx_table_calculate_available_space()
        max_pages = self._page.csm.get_nr_of_pages_trx_data(space, self.current_filtered_trx_data)
        if self.current_page_number > max_pages:
            self.current_page_number = max_pages
            self._trx_table_refresh()

        return ft.Container(
            height=PAGINATION_BAR_HEIGHT,
            padding=1,
            alignment=ft.Alignment.TOP_CENTER,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Button(content='<<', bgcolor=WHITE, height=20, on_click=self._trx_table_first_page,
                              style=BUTTON_STYLE),
                    ft.Button(content='<', bgcolor=WHITE, height=20, on_click=self._trx_table_decrement_page,
                              style=BUTTON_STYLE),
                    ft.Text(f"Page {self.current_page_number} of {max_pages}", size=13),
                    ft.Button(content='>', bgcolor=WHITE, height=20, on_click=self._trx_table_increment_page,
                              style=BUTTON_STYLE),
                    ft.Button(content='>>', bgcolor=WHITE, height=20, on_click=self._trx_table_last_page,
                              style=BUTTON_STYLE),
                ]
            )
        )

    # endregion
    ################################################################################################################
    # region UPDATING

    def _trx_table_change_category(self, e: ft.ControlEvent):
        e.control.data['dropdown'].visible = not e.control.data['dropdown'].visible
        e.control.data['text'].visible = not e.control.data['text'].visible
        e.control.data['discard_button'].visible = not e.control.data['discard_button'].visible
        category_selection_items = e.control.data

        if e.control is category_selection_items['dropdown']:
            self._page.csm.update_trx_field(
                authcode=category_selection_items['authcode'],
                column='category',
                value=category_selection_items['dropdown'].value,
            )
            category_selection_items['text'].value = category_selection_items['dropdown'].value

    def _handle_item_click(self, e: ft.ControlEvent):
        action = e.control.content
        print(action)

    def _open_context_menu(self, e: ft.ControlEvent):
        id = e.control.data
        self.context_menu.data = id
        self.context_menu.open = True

    def _context_menu_delete_row(self, e: ft.ControlEvent):
        self.context_menu.open = False
        self.context_menu.update()
        trx_id = self.context_menu.data
        print(f'[_context_menu_delete_row] trx_id: [{trx_id}]')
        self._page.csm.drop_row(trx_id)
        self._trx_table_refresh()
        self.context_menu.data = ''

    def _update_box_handler(self, authcode: str):

        trx = self._page.csm.get_trx_row(authcode).iloc[0]
        initial_date = getattr(trx, 'date')
        initial_trx_id = getattr(trx, 'authcode')
        initial_merchant = getattr(trx, 'merchant')
        initial_amount = float(getattr(trx, 'amount'))
        initial_notes = getattr(trx, 'notes')
        initial_category = getattr(trx, 'category')

        self.update_box.content = ft.SafeArea(
            ft.Column(
                tight=True,
                controls=[
                    ft.Text("Date"),
                    date_field := ft.TextField(
                        initial_date.strftime('%d-%b-%Y').strip(' 00:00:00'),
                        read_only=True,
                        enable_interactive_selection=False,
                        mouse_cursor=ft.MouseCursor.CLICK,
                        on_click=lambda _: self._page.show_dialog(self.date_picker),
                        prefix_icon=ft.IconButton(
                            ft.Icons.CALENDAR_MONTH,
                            on_click=lambda _: self._page.show_dialog(self.date_picker),
                        ),
                    ),
                    ft.Text("Transaction ID"),
                    ft.TextField(
                        initial_trx_id,
                        tooltip='Authcode/Transaction ID cannot be changed.',
                        read_only=True,
                        enable_interactive_selection=False,
                        mouse_cursor=ft.MouseCursor.CLICK,
                    ),

                    ft.Text("Merchant"),
                    merchant_field := ft.TextField(
                        initial_merchant if not pd.isna(initial_merchant) else '',
                    ),

                    ft.Text("Amount"),
                    amount_field := ft.TextField(
                        initial_amount,
                        prefix_icon=ft.Icons.EURO,
                        input_filter=ft.InputFilter(allow=True, regex_string=r"^\d*\.?\d{0,2}$"),
                    ),

                    ft.Text("Notes"),
                    notes_field := ft.TextField(
                        initial_notes if str(initial_notes) != '<NA>' else '',
                    ),

                    ft.Text("Category"),
                    category_field := ft.Dropdown(
                        bgcolor=SILVER,
                        border_radius=4,
                        enable_filter=True,
                        editable=True,
                        menu_height=400,
                        text_size=14,
                        expand=True,
                        value=initial_category,
                        options=[ft.DropdownOption(key=value, text=value) for value in
                                 self._page.csm.get_unique_categories()]
                    )
                ]
            )
        )

        def set_date(e: ft.ControlEvent):
            selected_date = e.control.value + timedelta(days=1)
            date_field.value = selected_date.strftime('%d-%b-%Y')

        self.date_picker.on_change = set_date

        async def submit_updates(e: ft.ControlEvent):
            # disallow empty fields
            if merchant_field.value.strip() == '':
                await merchant_field.focus()
                merchant_field.border_color = ft.Colors.RED
                return
            elif amount_field.value == '':
                await amount_field.focus()
                amount_field.border_color = ft.Colors.RED
                return
            # only update if the field has changed
            if initial_date.strftime('%d-%b-%Y') != date_field.value:
                self._page.csm.update_trx_field(
                    authcode=authcode,
                    column='date',
                    value=date_field.value,
                )
            if initial_merchant != merchant_field.value:
                self._page.csm.update_trx_field(
                    authcode=authcode,
                    column='merchant',
                    value=merchant_field.value,
                )
            if initial_amount != amount_field.value:
                self._page.csm.update_trx_field(
                    authcode=authcode,
                    column='amount',
                    value=amount_field.value,
                )
            if pd.isna(initial_notes) and notes_field.value != '':
                self._page.csm.update_trx_field(
                    authcode=authcode,
                    column='notes',
                    value=notes_field.value,
                )
            if initial_category != category_field.value:
                self._page.csm.update_trx_field(
                    authcode=authcode,
                    column='category',
                    value=category_field.value,
                )
            # close dialog
            self._page.pop_dialog()
            self._trx_table_refresh()

        date_field.on_submit = submit_updates
        merchant_field.on_submit = submit_updates
        amount_field.on_submit = submit_updates
        notes_field.on_submit = submit_updates

        self.context_menu_send_update_button.on_click = submit_updates

    def _context_menu_edit_row(self, e: ft.ControlEvent):
        self.context_menu.open = False
        self.context_menu.update()
        trx_id = self.context_menu.data
        self._update_box_handler(self.context_menu.data)
        self._page.show_dialog(self.update_box)

    # endregion
    ################################################################################################################
    # region TABLE

    def _highlight_trx_row(self, trx_id: str, e: ft.ControlEvent):
        if not e.control.selected:
            self.trx_table_selected_rows.add(trx_id)
        else:
            self.trx_table_selected_rows.discard(trx_id)
        e.control.selected = not e.control.selected

    def _trx_table_fill(self) -> None:

        rows = []
        unique_categories = self._page.csm.get_unique_categories()

        def make_data_cell(row, col):

            if pd.isna(getattr(row, col)):
                cell_value = ''
            elif col == 'date':
                cell_value = getattr(row, col).strftime('%d-%b-%Y').strip(' 00:00:00')
            elif col == 'amount':
                cell_value = f'€ {getattr(row, col):.2f}'
            else:
                cell_value = str(getattr(row, col))

            if col == 'merchant':
                return ft.DataCell(
                    content=ft.Row(
                        controls=[
                            ft.Image(src=getattr(row, 'icon'), width=TRX_TABLE_ICON_SIZE,
                                     height=TRX_TABLE_ICON_SIZE, color=GREY)
                            if row.icon.startswith('<svg') else ft.Icon(ft.Icons.STORE, color=GREY,
                                                                        size=TRX_TABLE_ICON_SIZE),
                            ft.Text(
                                **TEXT_DEFAULTS,
                                value=cell_value,
                            )
                        ]
                    )
                )
            elif col == 'category':
                return ft.DataCell(
                    ft.Container(
                        alignment=ft.Alignment.CENTER,
                        content=ft.Text(
                            **TEXT_DEFAULTS,
                            value=cell_value,
                        )
                    )
                )
            else:
                return ft.DataCell(
                    ft.Container(
                        alignment=ft.Alignment.CENTER,
                        content=ft.Text(
                            **TEXT_DEFAULTS,
                            value=cell_value,
                        )
                    )
                )

        for row in self.current_page_trx_data.itertuples():
            rows.append(
                ftd.DataRow2(
                    specific_row_height=TRX_TABLE_ROW_HEIGHT,
                    data=getattr(row, 'authcode'),
                    on_secondary_tap=self._open_context_menu,
                    on_double_tap=self._open_context_menu,
                    cells=[make_data_cell(row, col) for col in COLUMN_HEADERS]
                )
            )

        self.trx_table.rows = rows

    def _trx_table_refresh(self, execute_update: bool = True, apply_filters: bool = True) -> None:
        space = self._trx_table_calculate_available_space()

        filter_strings = self.filter_textbox_string_search.value if (self.filter_dropdown_string_search.value in
                                                                     ['', 'All', 'Merchant']) else ''
        filter_categories = self.filter_textbox_string_search.value if (self.filter_dropdown_string_search.value in
                                                                        ['Category']) else ''
        filter_date = self._page.csm.get_trx_data_date_mask(self.filter_textbox_start_date.value,
                                                            self.filter_textbox_end_date.value)
        filter_amount = self._page.csm.get_trx_data_amount_mask(
            self.filter_dropdown_amount_comparator.value if self.filter_dropdown_amount_comparator.value else '',
            float(self.filter_textbox_amount.value) if self.filter_textbox_amount.value else 0)

        if apply_filters:
            self.current_filtered_trx_data = self._page.csm.get_trx_data(
                search_term=filter_strings,
                category=filter_categories,
                date_mask=filter_date,
                amount_mask=filter_amount,
            )

        self._trx_table_apply_sort()

        self.current_page_trx_data = self._page.csm.get_paginated_trx_data(
            page_nr=self.current_page_number,
            page_size=space,
            data=self.current_filtered_trx_data,
        )

        self._trx_table_fill()
        self.trx_table.sort_column_index = self.current_sort_column_index
        self.trx_table.sort_ascending = self.current_sort_ascending

        if not self.content:
            self.content = ft.Column(
                expand=True,
                controls=[
                    self.filter_container,
                    ft.Stack(
                        expand=True,
                        controls=[
                            self.trx_table,
                            self.table_size_probe,
                        ]
                    ),
                    self._trx_table_pagination_bar(),
                ]
            )
        else:
            self.content.controls[1] = self.trx_table
            self.content.controls[2] = self._trx_table_pagination_bar()

        if execute_update: self.update()

    # endregion
    ################################################################################################################
