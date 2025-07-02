import flet as ft
from constants import *
from payment_methods import PaymentMethods
from categories import Categories
from vendors import Vendor
import datetime
import logging
from sql_utils import SQLiteUtils

class Settings(SQLiteUtils):
    def __init__(self,page:ft.Page):

        super().__init__()
        self.page = page
        self.logger = logging.getLogger(__name__)
        self.payment = PaymentMethods(page)
        self.categories = Categories(page)
        self.vendor = Vendor(page)
        self.excluded_views = [
            "Debt",
            "Person",
            "Cashback",
            "Recurring",
            "kind"
        ]
    
    def __adjust_savings_and_investments(self,data):
        if data["category"] in ["Investment","Invest"]:
            try:
                investment = self.fetch_investment(name=data["vendor"])[0]
                updated_price = investment.get("invested_value",0) + data["price"]
                self.update_investment(name=data["vendor"],invested_value=updated_price)
            except:
                investment = {}
                updated_price = investment.get("invested_value",0) + data["price"]
                self.insert_investment(name=data["vendor"],invested_value=updated_price)
        
        if data['kind'] != 'x':
            self.update_payment_method(
                payment_method_id= data["bank_id"],
                balance = self.query_payment_methods(id=data["bank_id"])[0]["balance"] + data["price"],
            )
        else:
            self.update_payment_method(
                payment_method_id= data["bank_id"],
                balance = self.query_payment_methods(id=data["bank_id"])[0]["balance"] + data["price"],
            )
            self.update_payment_method(
                payment_method_id= self.generate_id(data["vendor"],data["mode"]),
                balance = self.query_payment_methods(id=self.generate_id(data["vendor"],data["mode"]))[0]["balance"] - data["price"],
            )

    def _get_recurring_payments(self):
        recurring = self.fetch_recurring()
        if recurring != []:
            self.recurring_payments = ft.Row(
                controls = [
                    ft.DataTable(
                        columns = [
                            ft.DataColumn(ft.Text(dt.capitalize())) for dt in recurring[0].keys() if dt not in self.excluded_views 
                        ],
                        rows = [
                            ft.DataRow([
                                ft.DataCell(ft.Text(v)) if k != "Date" else ft.DataCell(ft.Text(v.strftime("%Y-%m-%d"))) for k,v in trnx.items() if k not in self.excluded_views
                            ],
                            color = {
                                ft.ControlState.DEFAULT: ft.Colors.RED_100 if trnx["kind"] == "-" else ft.Colors.GREEN_100
                            }
                        ) for trnx in recurring
                        ],
                        expand=True,
                        bgcolor=ft.Colors.BLUE_50,
                    ),
                ],
                expand=True,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            )
        else:
            self.recurring_payments = ft.Row(
                controls = [
                    ft.DataTable(
                        columns = [
                            ft.DataColumn(ft.Text(dt["name"].capitalize())) for dt in TRANSACTION_FIELD_NAMES if dt["name"] not in self.excluded_views and dt["to_show"] is True
                        ],
                        expand=True,
                        bgcolor=ft.Colors.BLUE_50,
                    ),
                ],
                expand=True,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            )
        return self.recurring_payments

    def __adjust_recurring_payments(self):
        recurring = self.fetch_recurring()
        today = datetime.datetime.now().date()
        for idx,trnx in enumerate(recurring):
            date = datetime.datetime.strptime(trnx["date"],"%Y-%m-%d").date()
            check = False
            if trnx["frequency"] == "Daily" and (today-date) >= datetime.timedelta(days=1):
                self.logger.info("Triggered daily")
                trnx["date"] = today
                check = True
            elif trnx["frequency"] == "Weekly" and (today-date) >= datetime.timedelta(weeks=1):
                self.logger.info("Triggered weekly")
                trnx["date"] = today
                check = True
            elif trnx["frequency"] == "Monthly" and (today-date) >= datetime.timedelta(weeks=4):
                self.logger.info("Triggered monthly")
                trnx["date"] = today
                check = True
            elif trnx["frequency"] == "Yearly" and (today-date) >= datetime.timedelta(days=365):
                self.logger.info("Triggered yearly")
                trnx["date"] = today
                check = True
            if check:
                tmp = trnx.copy()
                tmp["id"] = self.generate_uuid()
                self.__adjust_savings_and_investments(tmp)
                self.insert_transaction(tmp)
                self.update_recurring(trnx)
    
    def adjust_recurring_payments(self):
        self.__adjust_recurring_payments()
    
    def navigation_bar(self):
        return ft.AppBar(
            leading_width=40,
            title=ft.Text("Manage app"),
            center_title=False,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            leading = ft.IconButton(
                    ft.Icons.HOME,
                    on_click= lambda e: self.page.go('/')
                ),
            actions=[
                ft.IconButton(
                    icon=ft.Icons.QUESTION_ANSWER_OUTLINED,
                    on_click= lambda e: self.page.open(
                        ft.AlertDialog(
                            content=ft.Text(open(FLET_APP_CONSOLE).read()),
                            scrollable=True,
                        )
                    )
                ),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    on_click= lambda e: self.landing_page()
                )
            ]
        )
    
    def __save_profile_info(self):
        profile = {} if self.fetch_profile() == [] else self.fetch_profile()[0]
        if profile == {}:
            profile["user_id"] = self.generate_uuid()
            profile["name"] = self.name.value
            profile["salary_day"] = int(self.salary_text.value)
            self.insert_profile(profile["name"], profile["salary_day"], profile["user_id"])
        else:
            profile["name"] = self.name.value
            profile["salary_day"] = int(self.salary_text.value)
            self.update_profile(profile["user_id"], name = profile["name"], salary_day = profile["salary_day"])
        self.salary_text.disabled = True
        self.salary_text.update()
        
    def landing_page(self):

        def enable_salary_edit():
            self.salary_text.disabled = False
            self.salary_text.update()
        
        self.page.views.clear()
        self.page.theme_mode = ft.ThemeMode.LIGHT
        profile = {} if self.fetch_profile() == [] else self.fetch_profile()[0]
        
        self.salary_text = ft.TextField(
            label="Salary Day",
            prefix_icon=ft.Icons.CALENDAR_MONTH,
            keyboard_type=ft.KeyboardType.NUMBER,
            value = profile.get("salary_day",""),
            disabled= True if profile.get("salary_day","") != "" else False
        )
        self.name = ft.TextField(
            label="Name",
            value = profile.get("name",""),
            disabled= True if profile.get("name","") != "" else False
        )
        self.page.views.append(
            ft.View(
                "/settings",
                appbar=self.navigation_bar(),
                controls=[
                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            scroll=ft.ScrollMode.AUTO,
                            expand=True,
                            controls=[
                                ft.Column(
                                    [
                                        self.name,
                                        self.salary_text,
                                        ft.Row(
                                            [
                                                ft.ElevatedButton(
                                                    icon=ft.Icons.SAVE,
                                                    text="Save",
                                                    on_click= lambda e: self.__save_profile_info()           
                                                ),
                                                ft.ElevatedButton(
                                                    icon=ft.Icons.EDIT,
                                                    text="Edit",
                                                    on_click= lambda e: enable_salary_edit()         
                                                )
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        )
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),
                                ft.ExpansionPanelList(
                                    expand_icon_color=ft.Colors.BLUE_900,
                                    spacing = 10,
                                    elevation=8,
                                    divider_color=ft.Colors.AMBER,
                                    expand=True,
                                    controls=[
                                        ft.ExpansionPanel(
                                            header=ft.Container(
                                                content=ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            "Payment Methods",
                                                            size=20,
                                                            weight=ft.FontWeight.BOLD,
                                                        ),
                                                        ft.PopupMenuButton(
                                                            items=[
                                                                ft.PopupMenuItem(
                                                                    icon=ft.Icons.ADD,
                                                                    text="New payment method",
                                                                    on_click=lambda e: self.page.open(self.payment.new_payment_method())
                                                                ),
                                                                ft.PopupMenuItem(
                                                                    icon=ft.Icons.REMOVE,
                                                                    text="Delete payment method",
                                                                    on_click=lambda e: self.page.open(self.payment.delete_payment_method())
                                                                )
                                                            ]
                                                        )
                                                    ],
                                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                                ),
                                                padding=ft.padding.all(10)
                                            ),
                                            bgcolor=ft.Colors.BLUE_200,
                                            expanded=False,
                                            can_tap_header=True,
                                            content=ft.Container(
                                                content=ft.Column(
                                                    controls=[
                                                        self.payment.payment_method_table()
                                                    ],
                                                ),
                                                padding=ft.padding.all(10)
                                            )
                                        ),
                                        ft.ExpansionPanel( 
                                            header=ft.Container(
                                                content=ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            "Categories",
                                                            size=20,
                                                            weight=ft.FontWeight.BOLD,
                                                        ),
                                                        ft.PopupMenuButton(
                                                            items=[
                                                                ft.PopupMenuItem(
                                                                    icon=ft.Icons.ADD,
                                                                    text="New categories",
                                                                    on_click=lambda e: self.page.open(self.categories.add_new_categories())
                                                                ),
                                                                ft.PopupMenuItem(
                                                                    icon=ft.Icons.REMOVE,
                                                                    text="Remove Categories",
                                                                    on_click=lambda e: self.page.open(self.categories.delete_categories())
                                                                )
                                                            ]
                                                        )
                                                    ],
                                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                                ),
                                                padding=ft.padding.all(10)
                                            ),
                                            bgcolor=ft.Colors.BLUE_200,
                                            expanded=False,
                                            can_tap_header=True,
                                            content=ft.Container(
                                                content=ft.Column(
                                                    controls=[
                                                        self.categories.categories_table()
                                                    ],
                                                ),
                                                padding=ft.padding.all(10)
                                            )
                                        ),
                                        ft.ExpansionPanel( 
                                            header=ft.Container(
                                                content=ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            "Vendors",
                                                            size=20,
                                                            weight=ft.FontWeight.BOLD,
                                                        ),
                                                        ft.PopupMenuButton(
                                                            items=[
                                                                ft.PopupMenuItem(
                                                                    icon=ft.Icons.ADD,
                                                                    text="Add new vendor",
                                                                    on_click=lambda e: self.page.open(self.vendor.add_vendor())
                                                                ),
                                                                ft.PopupMenuItem(
                                                                    icon=ft.Icons.REMOVE,
                                                                    text="Remove vendor",
                                                                    on_click=lambda e: self.page.open(self.vendor.delete_vendor())
                                                                )
                                                            ]
                                                        )
                                                    ],
                                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                                ),
                                                padding=ft.padding.all(10)
                                            ),
                                            bgcolor=ft.Colors.BLUE_200,
                                            expanded=False,
                                            can_tap_header=True,
                                            content=ft.Container(
                                                content=ft.Column(
                                                    controls=[
                                                        self.vendor.view_vendor()
                                                    ],
                                                ),
                                                padding=ft.padding.all(10)
                                            )
                                        ),
                                        ft.ExpansionPanel(
                                            header=ft.Container(
                                                content=ft.Row(
                                                    controls=[
                                                        ft.Text(
                                                            "Recurring Payments",
                                                            size=20,
                                                            weight=ft.FontWeight.BOLD,
                                                        ),
                                                        ft.IconButton(
                                                            icon=ft.Icons.ROTATE_LEFT,
                                                            icon_color=ft.Colors.BLACK87,
                                                            # text = "Adjust Recurring Payments",
                                                            on_click= lambda e : self.__adjust_recurring_payments()
                                                        )
                                                    ],
                                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                                ),
                                                padding=ft.padding.all(10)
                                            ),
                                            bgcolor=ft.Colors.BLUE_200,
                                            expanded=False,
                                            can_tap_header=True,
                                            content=ft.Container(
                                                content=ft.Column(
                                                    controls=[
                                                        self._get_recurring_payments()
                                                    ],
                                                    expand=True,
                                                    tight=True,
                                                    scroll=ft.ScrollMode.AUTO,
                                                ),
                                                padding=ft.padding.all(10),
                                                expand = True,
                                            )
                                        ),
                                    
                                    ]
                                )
                            ]
                        )
                    )
                ]
            )
        )

        self.page.update()
