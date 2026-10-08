import flet as ft
import flet_datatable2 as ftd

from collections.abc import Callable
from typing import Any

def column_label(label: str) -> ft.Text:
    return ft.Text(
        label,
        size=12,
        max_lines=2,
        overflow=ft.TextOverflow.ELLIPSIS,
        text_align=ft.TextAlign.CENTER,
    )


def centered_column(label: str, sort_method=None) -> ftd.DataColumn2:
    if label == 'icon':
        return ftd.DataColumn2(
            heading_row_alignment=ft.MainAxisAlignment.CENTER,
            fixed_width=52,
            label=column_label(label),
            on_sort=sort_method
        )

    return ftd.DataColumn2(
        heading_row_alignment=ft.MainAxisAlignment.CENTER,
        label=column_label(label),
        on_sort=sort_method
    )
