import flet as ft
from constants import *
import logging
import datetime
from sql_utils import SQLiteUtils

class Track(SQLiteUtils):
    def __init__(self,page:ft.Page):
        super().__init__()
        self.page = page
        self.logger = logging.getLogger(__name__)
    
    def calculate_current_category(self):
        transactions = self.fetch_transactions()
        categories = self.fetch_categories()
        start,end = self.load_start_end_date()
        result = {cat:0 for cat in categories}
        for trnx in transactions:
            if start <= datetime.datetime.strptime(trnx["date"],"%Y-%m-%d").date() <= end:
                if trnx["category"] not in result:
                    result[trnx["category"]] = 0
                result[trnx["category"]] += trnx["price"]
        return result
    
    def calculate_spend_limit(self):
        budgeting_tool = self.fetch_budgeting_tool()
        categories = self.fetch_categories()
        result = {cat:0 for cat in categories}
        for spend in budgeting_tool:
            result[spend["category"]] = spend["spend_limit"]
        return result

    def view_progress_status(self):
        investments = self.fetch_investment()
        spent = self.calculate_current_category()
        limit = self.calculate_spend_limit()
        self.category_progress_bar = [ 
            ft.Column(
                controls=[
                    ft.ProgressBar(
                        value=abs(spent[dt])/limit[dt],
                        color = ft.Colors.RED,
                        bgcolor=ft.Colors.GREEN_300
                    ),
                    ft.Row(
                        [
                            ft.Text(dt,weight=ft.FontWeight.BOLD),
                            ft.Text(
                                f"{abs(spent[dt])}/{limit[dt]}",
                                weight=ft.FontWeight.BOLD
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    )
                ],
            ) for dt in limit.keys() if dt != "total" and limit[dt] != 0
        ]
        self.header = [ft.Text(
                "Spend Tracking",
                expand=True,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLACK,
                size=25,
            )]
        
        self.header.extend(self.category_progress_bar)

        self.body = [
            ft.Container(
                content = ft.Column(
                    [
                        ft.Text(
                            abs(investment["invested_value"]),
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLACK,
                            size=50,
                            # expand=True,
                        ),
                        ft.Text(
                            investment["name"],
                            # expand=True,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    # expand=True,
                    # tight=True,
                ),
                border= ft.border.all(2,color=ft.Colors.BLACK),
                padding=10,
                border_radius=10,
                bgcolor = ft.Colors.AMBER_50,
                # expand= True,
            ) for investment in investments
        ]

        debt = self.run_query(
            "SELECT person,sum(price) as amount FROM transactions WHERE person != '' GROUP BY person",
            fetch=True
        )
        self.debt_container = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Person",weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Amount",weight=ft.FontWeight.BOLD))
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(debt_item["person"])),
                        ft.DataCell(ft.Text(f"{abs(debt_item['amount'])}"))
                    ]
                ) for debt_item in debt
            ],
            expand=True,
        )
        return ft.Column(
            controls=[
                ft.Container(
                    content = ft.Column(
                        self.header,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        scroll=ft.ScrollMode.HIDDEN
                    ),
                    border= ft.border.all(2,color=ft.Colors.BLACK),
                    padding=10,
                    border_radius=10,
                    bgcolor=ft.Colors.AMBER_50,
                ),
                ft.Container(
                    content = ft.Column(
                        [
                            ft.Text("Investment Management",weight=ft.FontWeight.BOLD,size=20),
                            ft.Text("Track your investments and their progress",size=15),
                            ft.GridView(
                                self.body,
                                expand=1,
                                runs_count=2,
                                child_aspect_ratio=1.0,
                                spacing=5,
                                run_spacing=5,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    padding=10,
                    border_radius=5,
                    # bgcolor=ft.Colors.AMBER_50,
                    border= ft.border.all(2,color=ft.Colors.BLACK),
                    expand=True,
                ),
                ft.Container(
                    content = ft.Column(
                        [
                            ft.Text("Debt Management",weight=ft.FontWeight.BOLD,size=20),
                            ft.Text("Track your debts here",size=15),
                            self.debt_container
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    padding=10,
                    border_radius=5,
                    bgcolor=ft.Colors.AMBER_50,
                    border= ft.border.all(2,color=ft.Colors.BLACK),
                    expand=True,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO
        )