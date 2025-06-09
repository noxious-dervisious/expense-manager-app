import flet as ft
from constants import *
import logging
import datetime
from transactions import Transactions
from sql_utils import SQLiteUtils

class Overview(SQLiteUtils):
    def __init__(self,page:ft.Page):
        super().__init__()
        self.page = page
        self.transaction_classs = Transactions(self.page)
        self.logger = logging.getLogger(__name__)

    def __calculate_total_consumed(self):

        spent = 0
        earned = 0

        start,end = self.load_start_end_date()
        transactions = self.fetch_transactions()
        for transaction in transactions:
            price = transaction["price"]
            if start <= datetime.datetime.strptime(transaction["date"],"%Y-%m-%d").date() <= end and transaction["kind"] == '-':
                spent += price
            elif start <= datetime.datetime.strptime(transaction["date"],"%Y-%m-%d").date() <= end and transaction["kind"] == '+':
                earned += price
            else:
                continue
        return (spent,earned)

    def view_table(self):

        payment_methods = self.get_payment_methods()

        value = self.__calculate_total_consumed()
        self.total_spent = ft.Text(
                    value = abs(value[0]),
                    weight= ft.FontWeight.BOLD,
                    size= min(self.page.width*0.2,50),
                    expand=True,
                    color=ft.Colors.RED,
                )
        self.total_earned = ft.Text(
                    value = abs(value[1]),
                    weight= ft.FontWeight.BOLD,
                    size= min(self.page.width*0.2,50),
                    expand=True,
                    color=ft.Colors.GREEN,
                )
        self.left = ft.Text(
                    value = abs(value[1]) - abs(value[0]),
                    weight= ft.FontWeight.BOLD,
                    size= min(self.page.width*0.2,50),
                    expand=True,
                    color="#522DB6",
                )
        self.total_left_box = ft.Container(ft.Column(
                    [
                        self.left,
                        ft.Text("Total Remaining",color="#522DB6",weight=ft.FontWeight.BOLD)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True
                ),
                border=ft.border.all(2, "#522DB6"),
                border_radius=10,
                padding=10,
                alignment=ft.alignment.center,
                bgcolor="#B8A5FC"
            )
        self.total_spend_box = ft.Container(ft.Column(
                    [
                        self.total_spent,
                        ft.Text("Total Spend",color="#DC2626",weight=ft.FontWeight.BOLD)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True
                ),
                border=ft.border.all(2, ft.Colors.RED_900),
                border_radius=10,
                padding=10,
                alignment=ft.alignment.center,
                bgcolor="#FCA5A5"
            )
        
        self.total_earned_box = ft.Container(ft.Column(
                    [
                        self.total_earned,
                        ft.Text("Total Earned",color="#16A34A",weight=ft.FontWeight.BOLD)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True
                ),
                border=ft.border.all(2, ft.Colors.GREEN_900),
                border_radius=10,
                padding=10,
                alignment=ft.alignment.center,
                bgcolor="#C9EED6",
            )
        
        self.bank_balance = ft.Column(
            [
                ft.Text(
                    "Account Statement",
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_ACCENT,
                    size=25
                ),
                ft.DataTable(
                    columns = [
                        ft.DataColumn(label=ft.Text("Bank Name",color="#1E293B")),
                        ft.DataColumn(label=ft.Text("Category",color="#1E293B")),
                        ft.DataColumn(label=ft.Text("Balance",color="#1E293B"))
                    ],
                    rows = [
                        ft.DataRow(
                            [
                                ft.DataCell(ft.Text(payment["bank"],color="#1E293B")),
                                ft.DataCell(ft.Text(payment["mode"],color="#1E293B")),
                                ft.DataCell(ft.Text(payment["balance"],color="#1E293B")),
                            ]
                        ) for payment in payment_methods if payment["parent"] is None
                    ],
                    bgcolor="#E0F2FE",
                    border=ft.border.all(width=2,color=ft.Colors.GREY_400)
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            tight=True,
            scroll=ft.ScrollMode.HIDDEN,
        )
        return ft.Column([
                        self.total_left_box,
                        self.total_spend_box,
                        self.total_earned_box,
                        self.bank_balance,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO
                )