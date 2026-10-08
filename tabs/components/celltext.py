import flet as ft
import pandas as pd

def cell_text(value: str) -> ft.Text:
    if pd.isna(value): value = ''
    return ft.Text(value, overflow=ft.TextOverflow.ELLIPSIS, max_lines=2, size=14, expand=True)