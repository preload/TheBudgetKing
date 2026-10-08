import asyncio

import flet as ft

from core.colors import *
from core.constants import GLOBAL_THEME, SELECTED_TEXT_BUTTON_STYLE, TEXT_BUTTON_STYLE
from csm import CentralStateManager
from tabs.ImportViewFromFile import ImportView
from tabs.ImportViewManual import ImportViewManual
from tabs.TrxViewOverviewTab import TrxViewOverviewTab


def placeholder_budget_chart() -> ft.Container:
    return ft.Container(
        height=300,
        padding=20,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            vertical_alignment=ft.CrossAxisAlignment.END,  # Aligns bars to the bottom
            controls=[
                # Income Bar
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                    controls=[
                        ft.Text("4500", color="#111111", weight=ft.FontWeight.BOLD),
                        ft.Container(width=40, height=200, bgcolor="#00ed64", border_radius=4),
                        ft.Text("Income", color="#111111"),
                    ]
                ),
                # Expenses Bar
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                    controls=[
                        ft.Text("3200", color="#111111", weight=ft.FontWeight.BOLD),
                        ft.Container(width=40, height=140, bgcolor="#ff4d4d", border_radius=4),
                        ft.Text("Expenses", color="#111111"),
                    ]
                ),
                # Remaining Bar
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                    controls=[
                        ft.Text("1300", color="#111111", weight=ft.FontWeight.BOLD),
                        ft.Container(width=40, height=60, bgcolor="#3b82f6", border_radius=4),
                        ft.Text("Remaining", color="#111111"),
                    ]
                ),
            ]
        )
    )


# def trx_view_duplicates_tab(page: ft.Page) -> ft.Container:
#     container = ft.Container(
#         padding=2,
#         border=ft.Border.all(width=2, color="#02b85a"),
#         border_radius=10,
#         expand=False,
#     )
#
#     def highlight_trx_row(e):
#         e.control.selected = not e.control.selected
#         e.control.update()
#
#     def trx_duplicate_table() -> ftd.DataTable2:
#         # TODO: Check if generator is already created, if not create it
#         # Logic below is broken
#         # if not hasattr(page, 'duplicate_generator') or page.duplicate_generator is None:
#         page.duplicate_generator = page.csm.get_duplicate_trx_data()
#         trx_group = next(page.duplicate_generator, None)
#
#         return ftd.DataTable2(
#             heading_row_height=30,
#             expand=False,
#             column_spacing=0,
#             data_row_checkbox_theme=CHECKBOX_THEME,
#             heading_checkbox_theme=CHECKBOX_THEME,
#             show_checkbox_column=True,
#             empty=ft.Text("No duplicates found!", size=12),
#             sm_ratio=0.5,
#             lm_ratio=1.5,
#             heading_row_color='#EAEAEA',
#             columns=[
#                 ftd.DataColumn2(label='Date', size=ftd.DataColumnSize.S),
#                 ftd.DataColumn2(label='Type', size=ftd.DataColumnSize.S),
#                 ftd.DataColumn2(label='Merchant', size=ftd.DataColumnSize.M),
#                 ftd.DataColumn2(label='Amount', size=ftd.DataColumnSize.S),
#                 ftd.DataColumn2(label='Notes', size=ftd.DataColumnSize.S),
#                 ftd.DataColumn2(label='Category', size=ftd.DataColumnSize.S),
#             ],
#             rows=[ftd.DataRow2(
#                 specific_row_height=30,
#                 visible=True,
#                 on_select_change=highlight_trx_row,
#                 cells=[
#                     ft.DataCell(content=cell_text(row.date.strftime("%Y-%m-%d"))),
#                     ft.DataCell(content=cell_text(row.trx_type)),
#                     ft.DataCell(content=cell_text(row.merchant)),
#                     ft.DataCell(content=cell_text(row.amount)),
#                     ft.DataCell(content=cell_text(row.notes)),
#                     ft.DataCell(content=cell_text(row.category)),
#                 ]
#             ) for row in trx_group.itertuples()],
#         )
#
#     def manage_duplicate_buttons() -> ft.Row:
#         return ft.Row(
#             alignment=ft.MainAxisAlignment.CENTER,
#             expand=False,
#             controls=[
#                 ft.Button(content='Retain All and Mark as Unique', bgcolor='#02b85a', color='#ffffff'),
#                 ft.Button(content='Retain Selected and Remove Others', bgcolor='#02b85a', color='#ffffff'),
#                 ft.Button(content='Delete All', bgcolor='#02b85a', color='#ffffff'),
#             ]
#         )
#
#     container.content = ft.Column(
#         [
#             trx_duplicate_table(),
#             manage_duplicate_buttons(),
#         ]
#     )
#
#     return container


def placeholder_home_overview_tab() -> ft.Container:
    return ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        border_radius=10,
        border=ft.Border.all(width=2, color="#02b85a"),
        bgcolor="#ffffff",
        padding=10,
        margin=10,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("Welcome back!", expand=True, size=40, weight=ft.FontWeight.BOLD, color="#111111"),
                ft.Text("Current month's income: 1700", expand=True, size=20, weight=ft.FontWeight.BOLD,
                        color="#111111"),
                ft.Text("Current month's expenses: 1200", expand=True, size=20, weight=ft.FontWeight.BOLD,
                        color="#111111"),
                ft.Text("Current month's balance: 500", expand=True, size=20, weight=ft.FontWeight.BOLD,
                        color="#111111"),
                ft.Text("Current month's budget: 1000", expand=True, size=20, weight=ft.FontWeight.BOLD,
                        color="#111111"),
                ft.Text("Current month's savings: 500", expand=True, size=20, weight=ft.FontWeight.BOLD,
                        color="#111111"),
                ft.Text("Current month's savings goal: 1000", expand=True, size=20, weight=ft.FontWeight.BOLD,
                        color="#111111"),
                ft.Text("Current month's savings progress: 50%", expand=True, size=20, weight=ft.FontWeight.BOLD,
                        color="#111111"),
                ft.Text("Current month's savings target: 1000", expand=True, size=20, weight=ft.FontWeight.BOLD,
                        color="#111111"),
                ft.Text("Current month's savings target progress: 50%", expand=True, size=20, weight=ft.FontWeight.BOLD,
                        color="#111111"),
                ft.Text("Current month's savings target goal: 1000", expand=True, size=20, weight=ft.FontWeight.BOLD,
                        color="#111111"),
                placeholder_budget_chart()
            ]
        )
    )


def create_navigation_bar(page: ft.Page, title: str) -> ft.NavigationBar:
    routes = ["/", "/import_view", "/budget_view", "/loan_view", "/trx_view"]
    titles = ["Home", "Import", "Budget", "Loans", "Transactions"]
    icons = [ft.Icons.HOME_OUTLINED, ft.Icons.IMPORT_EXPORT_OUTLINED,
             ft.Icons.MONEY_OUTLINED, ft.Icons.PERSON_OUTLINED, ft.Icons.SEARCH_OUTLINED]

    def on_change(e: ft.ControlEvent):
        asyncio.create_task(page.push_route(routes[e.control.selected_index]))

    return (
        ft.SafeArea(
            ft.NavigationBar(
                selected_index=titles.index(title) if title in titles else 0,
                on_change=on_change,
                bgcolor=WHITE,
                elevation=2,
                height=50,
                destinations=[
                    ft.NavigationBarDestination(icon=icon, label=label)
                    for icon, label in zip(icons, titles)
                ],
            ), visible=page.platform.is_mobile(),
        )
    )


def create_app_bar(page: ft.Page, title: str) -> ft.AppBar:
    return ft.AppBar(
        title=ft.Text(title, color=GREY, weight=ft.FontWeight.BOLD, size=20),
        bgcolor=SILVER,
        elevation=2,
        visible=page.platform.is_desktop(),
        automatically_imply_leading=False,
        actions_padding=10,
        actions=[
            ft.SafeArea(
                ft.Row(
                    spacing=5,
                    controls=[
                        ft.TextButton(content="Home",
                                      style=SELECTED_TEXT_BUTTON_STYLE if title == 'Home' else TEXT_BUTTON_STYLE,
                                      icon=ft.Icons.HOME_OUTLINED,
                                      on_click=lambda _: asyncio.create_task(page.push_route("/"))),
                        ft.TextButton(content="Import",
                                      style=SELECTED_TEXT_BUTTON_STYLE if title == 'Import' else TEXT_BUTTON_STYLE,
                                      icon=ft.Icons.IMPORT_EXPORT_OUTLINED,
                                      on_click=lambda _: asyncio.create_task(page.push_route("/import_view"))),
                        ft.TextButton(content="Budget",
                                      style=SELECTED_TEXT_BUTTON_STYLE if title == 'Budget' else TEXT_BUTTON_STYLE,
                                      icon=ft.Icons.MONEY_OUTLINED,
                                      on_click=lambda _: asyncio.create_task(page.push_route("/budget_view"))),
                        ft.TextButton(content="Loans",
                                      style=SELECTED_TEXT_BUTTON_STYLE if title == 'Loans' else TEXT_BUTTON_STYLE,
                                      icon=ft.Icons.PERSON_OUTLINED,
                                      on_click=lambda _: asyncio.create_task(page.push_route("/loan_view"))),
                        ft.TextButton(content="Transactions",
                                      style=SELECTED_TEXT_BUTTON_STYLE if title == 'Transactions' else TEXT_BUTTON_STYLE,
                                      icon=ft.Icons.SEARCH_OUTLINED,
                                      on_click=lambda _: asyncio.create_task(page.push_route("/trx_view"))),
                    ]
                )
            )
        ],
    )


def create_tab_bar(page: ft.Page, title: str) -> ft.Tabs:
    tab_bar_items = {
        'Home': {
            'labels': ['Overview', 'Settings'],
            'tabs': [ft.Container(), ft.Container()],
        },
        'Import': {
            'labels': ['From file', 'Manual'],
            'tabs': [ImportView(page), ImportViewManual(page)],
        },
        'Budget': {
            'labels': ['Overview', 'Edit', 'Stats'],
            'tabs': [ft.Container(), ft.Container(), ft.Container()],
        },
        'Loans': {
            'labels': ['Overview', 'New', 'Calculator'],
            'tabs': [ft.Container(), ft.Container(), ft.Container()],
        },
        'Transactions': {
            'labels': ['Overview', 'Duplicates', 'Export'],
            'tabs': [TrxViewOverviewTab(page), ft.Container(), ft.Container()],
        }
    }

    def get_tabs(title: str) -> list[ft.Tab]:
        return [ft.Tab(label=lbl, height=25) for lbl in tab_bar_items[title]['labels']]

    tabs = get_tabs(title)

    return ft.Tabs(
        length=len(tabs),
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                ft.Container(
                    bgcolor=WHITE,
                    content=ft.TabBar(
                        label_color="#111111",
                        scrollable=False,
                        tab_alignment=ft.TabAlignment.FILL,
                        tabs=tabs,
                    )
                ),
                ft.TabBarView(
                    expand=True,
                    controls=tab_bar_items[title]['tabs'],
                ),
            ],
        ),
    )


def main(page: ft.Page):
    page.csm = CentralStateManager()
    page.window.prevent_close = True
    page.theme_mode = ft.ThemeMode.LIGHT
    os = page.platform

    def wipe_import_data_on_page_change():
        page.csm.import_df = None
        page.csm.manual_df = None

    def route_change():
        page.views.clear()
        page.views.append(main_view(page))
        if page.route == "/import_view":
            wipe_import_data_on_page_change()
            page.views.append(import_view(page))
        if page.route == "/budget_view":
            page.views.append(budget_view(page))
        if page.route == "/loan_view":
            page.views.append(loan_view(page))
        if page.route == "/trx_view":
            wipe_import_data_on_page_change()
            page.views.append(trx_view(page))

        page.update()

    async def window_events(e):
        event_name = e.type.name
        if event_name == 'CLOSE':
            page.csm.save_trx_data()
            await page.window.destroy()

    page.window.on_event = window_events

    async def view_pop(e):
        if e.view is not None:
            page.views.remove(e.view)
        else:
            page.views.pop()
        top_view = page.views[-1]
        await page.push_route(top_view.route)

    page.theme = GLOBAL_THEME
    page.on_route_change = route_change
    page.on_pop_view = view_pop
    route_change()


def main_view(page: ft.Page) -> ft.View:
    title = 'Home'
    return ft.View(
        bgcolor="#ffffff",
        route="/",
        appbar=create_app_bar(page, title),
        navigation_bar=create_navigation_bar(page, title),
        controls=[
            ft.SafeArea(
                placeholder_home_overview_tab(),
                expand=True,
            )
        ]
    )


def import_view(page: ft.Page) -> ft.View:
    title = 'Import'
    return ft.View(
        bgcolor="#ffffff",
        route="/import_view",
        appbar=create_app_bar(page, title),
        navigation_bar=create_navigation_bar(page, title),
        controls=[
            ft.SafeArea(
                create_tab_bar(page, title),
                expand=True,
            )
        ],
    )


def budget_view(page: ft.Page) -> ft.View:
    title = 'Budget'
    return ft.View(
        bgcolor="#ffffff",
        route="/budget_view",
        appbar=create_app_bar(page, title),
        navigation_bar=create_navigation_bar(page, title),
        controls=[
            ft.SafeArea(
                create_tab_bar(page, title),
                expand=True,
            )
        ],
    )


def loan_view(page: ft.Page) -> ft.View:
    title = 'Loans'
    return ft.View(
        bgcolor="#ffffff",
        route="/loan_view",
        appbar=create_app_bar(page, title),
        navigation_bar=create_navigation_bar(page, title),
        controls=[
            ft.SafeArea(
                create_tab_bar(page, title),
                expand=True,
            )
        ],
    )


def trx_view(page: ft.Page) -> ft.View:
    title = 'Transactions'
    return ft.View(
        bgcolor="#ffffff",
        padding=5,
        route="/trx_view",
        appbar=create_app_bar(page, title),
        navigation_bar=create_navigation_bar(page, title),
        controls=[
            ft.SafeArea(
                create_tab_bar(page, title),
                expand=True,
            )
        ],
    )


if __name__ == "__main__":
    ft.run(main)
