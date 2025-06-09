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
        spent_value = abs(sum([spent[dt] for dt in limit.keys() if dt != "total" and limit[dt] != 0]))
        limit_value = sum([v for k,v in limit.items() if k != "total"])
        self.total_progress_tab = [ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                value = limit_value-spent_value,
                                weight= ft.FontWeight.BOLD,
                                size= min(self.page.width*0.1,50),
                                expand=True,
                                color="#000000",
                            ),
                            ft.Text(
                                value = "of",
                                weight= ft.FontWeight.BOLD,
                                size= min(self.page.width*0.2,25),
                                expand=True,
                                color="#6E6D6D44",
                                text_align=ft.TextAlign.END
                            ),
                            ft.Text(
                                value = limit_value,
                                weight= ft.FontWeight.BOLD,
                                size= min(self.page.width*0.1,50),
                                expand=True,
                                color="#000000",
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        scroll=ft.ScrollMode.HIDDEN
                    ),
                    ft.Text(
                        "Total Left",color="#000000",weight=ft.FontWeight.BOLD
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.HIDDEN
            ),
            border=ft.border.all(2, "#060B0C"),
            border_radius=10,
            padding=10,
            alignment=ft.alignment.center,
            bgcolor="#FFFFFF"
        )]
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
        self.header.extend(self.total_progress_tab)
        self.header.extend(self.category_progress_bar)

        self.body = ft.Column(
                    [
                        ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text("Name",weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Value",weight=ft.FontWeight.BOLD))
                            ],
                            rows=[
                                ft.DataRow(
                                    cells=[
                                        ft.DataCell(
                                            ft.Text(
                                                investment["name"],
                                                # text_align=ft.TextAlign.CENTER,
                                            )
                                        ),
                                        ft.DataCell(
                                            ft.Text(
                                                f"{abs(investment['invested_value'])}",
                                                # text_align=ft.TextAlign.CENTER,
                                            )
                                        )
                                    ]
                                ) for investment in investments
                            ],
                            expand=True,
                            bgcolor=ft.Colors.AMBER_50,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    # expand=True,
                    # tight=True,
                )

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
            bgcolor=ft.Colors.AMBER_50,
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
                            ft.Text("Investment Overview",weight=ft.FontWeight.BOLD,size=20),
                            ft.Text("Track your investments and their progress",size=15),
                            self.body
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
                            ft.Text("Debt Overview",weight=ft.FontWeight.BOLD,size=20),
                            ft.Text("Track your debts here",size=15),
                            self.debt_container
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
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO
        )