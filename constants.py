import flet as ft
import os

FLET_APP_STORAGE_DATA = os.getenv("FLET_APP_STORAGE_DATA")
FLET_APP_CONSOLE = os.getenv("FLET_APP_CONSOLE","console.log")
TRANSACTIONS_FILE_NAME = os.path.join(FLET_APP_STORAGE_DATA, "transactions.csv")
RECURRING_FILE_NAME = os.path.join(FLET_APP_STORAGE_DATA, "recurring_payments.csv")
PROFILE_FILE_NAME = os.path.join(FLET_APP_STORAGE_DATA, "profiles.yaml")
COLUMN_NAME_TYPE = "type"
COLUMN_NAME_VALUE = "value"
ACTIVE_TRACK_COLOR = ft.Colors.GREEN_ACCENT_400
INACTIVE_TRACK_COLOR = ft.Colors.GREY_200

APP_DATABASE_PATH = os.path.join(FLET_APP_STORAGE_DATA, "expense_manager_app.db")

PAYMENT_METHODS = [
    "Debit Card",
    "Credit Card",
    "Savings Account",
    "UPI"
]

PAYMENT_METHODS_ICON = [
    ft.Icons.QR_CODE_SCANNER_SHARP,
    ft.Icons.PAYMENT_OUTLINED,
    ft.Icons.ACCOUNT_BALANCE_OUTLINED,
    ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED
]

TRANSACTION_FIELD_NAMES = [
    {"name":"date","to_show":True},
    {"name":"vendor","to_show":True},
    {"name":"category","to_show":True},
    {"name":"price","to_show":True},
    {"name":"bank","to_show":True},
    {"name":"mode","to_show":True},
    {"name":"cashback","to_show":True},
    {"name":"recurring","to_show":True},
    {"name":"frequency","to_show":True},
    {"name":"debt","to_show":False},
    {"name":"person","to_show":False},
    {"name":"id","to_show":False},
    {"name":"kind","to_show":False},
    {"name":"bank_id","to_show":False}
]

PAYMENT_METHODS_SEGMENT = {
    "UPI" : ft.Segment(
        value="UPI",
        label=ft.Icon(ft.Icons.QR_CODE_SCANNER_SHARP,color=ft.Colors.BLUE_ACCENT),
        disabled=False,
    ),
    "Credit Card" : ft.Segment(
        value="Credit Card",
        icon=ft.Icon(ft.Icons.PAYMENT_OUTLINED,color=ft.Colors.BLUE_ACCENT),
        disabled=False,
    ),
    "Savings Account" : ft.Segment(
        value="Savings Account",
        icon=ft.Icon(ft.Icons.ACCOUNT_BALANCE_OUTLINED,color=ft.Colors.BLUE_ACCENT),
        disabled=False,
    ),
    "Debit Card" : ft.Segment(
        value="Debit Card",
        icon=ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,color=ft.Colors.BLUE_ACCENT),
        disabled=False,
    ),
}