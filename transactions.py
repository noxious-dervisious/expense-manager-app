import flet as ft
from constants import *
import logging
import datetime
from sql_utils import SQLiteUtils

class Transactions(SQLiteUtils):
    def __init__(self,page:ft.Page):
        super().__init__()
        self.page = page
        self.logger = logging.getLogger(__name__)
        self.transactions_table =None
        self.exclude_list = [ col["name"] for col in TRANSACTION_FIELD_NAMES if not col["to_show"] ]
        self.include_list = [ col["name"] for col in TRANSACTION_FIELD_NAMES if col["to_show"] ]
        self.category_dropdown = ft.Dropdown(
            options=[ft.DropdownOption("All")] + [
                ft.DropdownOption(dt) for dt in self.fetch_categories()
            ],
            expand=True,
            label="Categories",
            on_change= lambda e: self.view_transaction(external=True),
        )

    def public_transactions_file(self):
        return self.fetch_transactions()
    
    def __delete_entry(self,idx,data):
        
        if data["category"] in ["Investment","Invest"]:
            investment = self.fetch_investment(name=data["vendor"])[0]
            updated_price = investment.get("invested_value",0) - data["price"]
            self.update_investment(name=data["vendor"],invested_value=updated_price)
            
        if data["recurring"]:
            self.delete_recurring(data["id"])

        if data["kind"] != 'x':
            payment_id = self.query_payment_methods(id=data["bank_id"])[0]["parent"] if self.query_payment_methods(id=data["bank_id"])[0]["parent"] is not None else data["bank_id"]            
            self.update_payment_method(
                payment_method_id= payment_id,
                balance = self.query_payment_methods(id=payment_id)[0]["balance"] - data["price"],
            )
        else:
            payment_id = self.query_payment_methods(id=data["bank_id"])[0]["parent"] if self.query_payment_methods(id=data["bank_id"])[0]["parent"] is not None else data["bank_id"]
            payment_id_1 = self.query_payment_methods(id=self.generate_id(data["vendor"],data["mode"]))[0]["parent"] if self.query_payment_methods(id=self.generate_id(data["vendor"],data["mode"]))[0]["parent"] is not None else self.generate_id(data["vendor"],data["mode"])
            self.update_payment_method(
                payment_method_id= payment_id,
                balance = self.query_payment_methods(id=payment_id)[0]["balance"] - data["price"],
            )
            self.update_payment_method(
                payment_method_id= payment_id_1,
                balance = self.query_payment_methods(id=payment_id_1)[0]["balance"] + data["price"],
            )

        self.delete_transaction(idx)
        self.page.views[-1].controls[-2].content=self.view_transaction()
        self.page.update()
    
    def __edit_entry(self,idx,data):
        error = False
        def price(value):
            if list(self.transaction_type.selected)[0] != '+':
                return 0 - int(value)
            return int(value)
        if self.vendor.controls[0].value is None:
            self.vendor.controls[0].error_text = "Vendor is missing"
            error = True
        else:
            self.vendor.controls[0].error_text = ""
        if self.payment_method.controls[0].value is None:
            self.payment_method.controls[0].error_text = "Payment method is missing"
            error = True
        else:
            self.payment_method.controls[0].error_text = ""
        if self.price.controls[0].value == "":
            self.price.controls[0].error_text = "Price is missing"
            error = True
        else:
            self.price.controls[0].error_text = ""
        
        if error:
            self.payment_method.update()
            self.price.update()
            self.vendor.update()
            self.logger.error("Missed a few values!!!!")
            return  
        category = self.fetch_vendors(name = self.vendor.controls[0].value)          
        data = {
                "date" : data["date"],
                "vendor" : self.vendor.controls[0].value,
                "category" : category[0]["category"] if len(category) > 0 else "Uncategorized",
                "price" : price(self.price.controls[0].value),
                "bank" : self.payment_method.controls[0].value,
                "mode" : list(self.payment_type.controls[0].selected)[0],
                "recurring" : self.periodic.controls[0].value,
                "frequency" : self.frequency.value,
                "debt" : self.debt.controls[0].value,
                "person" : self.debt_taker_name.value.capitalize(),
                "id" : data["id"],
                "kind" : list(self.transaction_type.selected)[0],
            }
        data["bank_id"] = self.generate_id(data["bank"],data["mode"])
        data["cashback"] = abs(self.query_payment_methods(id=data["bank_id"])[0]["cashback"] * data["price"])/100 if data["kind"] == "-" else 0
        old_price = self.fetch_transactions(id=data["id"])[0]["price"]
        self.update_transaction(data)

        if data["category"] in ["Investment","Invest"]:
            try:
                investment = self.fetch_investment(name=data["vendor"])[0]
                updated_price = investment.get("invested_value",0) + data["price"] - old_price
                self.update_investment(name=data["vendor"],invested_value=updated_price)
            except:
                investment = {}
                updated_price = investment.get("invested_value",0) + data["price"] - old_price
                self.insert_investment(name=data["vendor"],invested_value=updated_price)
            
        if self.fetch_recurring(id=data["id"]) != [] and data["recurring"]:
            self.update_recurring(data)
        elif data["recurring"]:
            self.insert_recurring(data)
        elif self.fetch_recurring(id=data["id"]) != [] and not data["recurring"]:
            self.delete_recurring(data["id"])

        if data["kind"] != 'x':
            payment_id = self.query_payment_methods(id=data["bank_id"])[0]["parent"] if self.query_payment_methods(id=data["bank_id"])[0]["parent"] is not None else data["bank_id"]
            self.update_payment_method(
                payment_method_id= payment_id,
                balance = self.query_payment_methods(id=payment_id)[0]["balance"] + data["price"] - old_price,
            )
        else:
            payment_id = self.query_payment_methods(id=data["bank_id"])[0]["parent"] if self.query_payment_methods(id=data["bank_id"])[0]["parent"] is not None else data["bank_id"]
            payment_id_1 = self.query_payment_methods(id=self.generate_id(data["vendor"],data["mode"]))[0]["parent"] if self.query_payment_methods(id=self.generate_id(data["vendor"],data["mode"]))[0]["parent"] is not None else self.generate_id(data["vendor"],data["mode"])
            self.update_payment_method(
                payment_method_id= payment_id,
                balance = self.query_payment_methods(id=payment_id)[0]["balance"] + data["price"] - old_price,
            )
            self.update_payment_method(
                payment_method_id= self.query_payment_methods(id=payment_id_1),
                balance = self.query_payment_methods(id=payment_id_1)[0]["balance"] - data["price"] + old_price,
            )
        
        self.page.close(self.edit_transaction_dialogue_box)
        self.page.views[-1].controls[-2].content = self.view_transaction()
        self.page.update()

    def  __open_edit_dialogue_box(self,idx,data):
        def debt(e):
            if self.debt.controls[0].value == True:
                self.debt.controls[1].disabled = False
            else:
                self.debt.controls[1].disabled = True
                self.debt_taker_name.value = ""
            self.edit_transaction_dialogue_box.update()

        def periodic(e):
            if self.periodic.controls[0].value == True:
                self.periodic.controls[1].disabled = False
            else:
                self.periodic.controls[1].disabled = True
                self.periodic.controls[1].value = ""
            self.edit_transaction_dialogue_box.update()

        self.debt_taker_name = ft.TextField(
            label="Paid to",
            expand=True,
            disabled=True,
        )

        self.debt = ft.Row([
                ft.Switch(label="Debt", value=bool(data["debt"]),on_change=debt),
                self.debt_taker_name
            ])

        self.transaction_type = ft.SegmentedButton(
                        selected={data["kind"]},
                        allow_multiple_selection=False,
                        show_selected_icon=True,
                        segments=[
                            ft.Segment(
                                value="-",
                                icon=ft.Icon(ft.Icons.REMOVE,color=ft.Colors.RED),
                            ),
                            ft.Segment(
                                value="x",
                                icon=ft.Icon(ft.Icons.SWAP_HORIZ,color=ft.Colors.BLACK),
                            ),
                            ft.Segment(
                                value="+",
                                icon=ft.Icon(ft.Icons.ADD,color=ft.Colors.GREEN),
                            ),
                        ],
                        disabled=True,
                    )
        self.vendor = ft.Row(
                            [
                                ft.Dropdown(
                                    value=data["vendor"],
                                    label="Vendor" if data["kind"] != 'x' else "To",
                                    expand=True,
                                    enable_search = True,
                                    enable_filter = True,
                                    focused_border_color = ft.Colors.RED,
                                    options = [ft.DropdownOption(key=dt["name"]) for dt in self.fetch_vendors()] if data["kind"] != "x" else [ft.DropdownOption(dt) for dt in set(payment["bank"] for payment in self.get_payment_methods())]
                                )
                            ]
                        )
        self.payment_method = ft.Row(
                        controls=[
                            ft.Dropdown(
                                label="Payment Method" if data["kind"] != 'x' else "From",
                                value=data["bank"],
                                expand=True,
                                enable_search=True,
                                enable_filter=True,
                                focused_border_color=ft.Colors.RED,
                                options=[ft.DropdownOption(dt) for dt in set(payment["bank"] for payment in self.get_payment_methods())],
                            ),
                        ],
                        vertical_alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10
                    )
        self.payment_type = ft.Row(
                                controls=[
                                    ft.SegmentedButton(
                                        selected={data["mode"]},
                                        allow_multiple_selection=False,
                                        show_selected_icon=True,
                                        expand = True,
                                        # direction=ft.Axis(value="vertical"),
                                        segments=[PAYMENT_METHODS_SEGMENT[payment["mode"]] for payment in self.query_payment_methods(id=data["bank_id"])],
                                    )
                                ],
                                vertical_alignment=ft.MainAxisAlignment.CENTER,
                                spacing=10
                            )
        self.price = ft.Row(
                            [
                                ft.TextField(
                                    label="Price",
                                    value=abs(data["price"]),
                                    expand=True,
                                    keyboard_type=ft.KeyboardType.NUMBER
                                )
                            ]
                        )
        self.frequency = ft.Dropdown(
                                label="Recurring Period",
                                expand=True,
                                options=[
                                    ft.DropdownOption(key="Yearly"),
                                    ft.DropdownOption(key="Monthly"),
                                    ft.DropdownOption(key="Weekly"),
                                    ft.DropdownOption(key="Daily"),
                                    
                                ],
                                value = data["frequency"] if data["frequency"] != "" else None,
                                disabled = False if data["frequency"] != "" and data["frequency"] is not None else True 
                            )
        
        self.periodic = ft.Row([
                ft.Switch(value=bool(data["recurring"]),on_change=periodic),
                self.frequency
            ])
        self.edit_transaction_dialogue_box = ft.AlertDialog(
            title = ft.Text(
                "Edit Transaction",
                color=ft.Colors.BLUE_ACCENT,
                weight=ft.FontWeight.BOLD
            ),
            content = ft.Container(
                expand=True,
                content = ft.Column(
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                    controls= [
                        self.transaction_type,
                        self.payment_type,
                        self.vendor,
                        self.payment_method,
                        self.price,
                        self.periodic,
                        self.debt,
                        ft.Row(
                            controls=[
                                ft.OutlinedButton(
                                    icon = ft.Icons.SEND,
                                    text="Save",
                                    icon_color=ft.Colors.GREEN_400,
                                    on_click= lambda e,idx=idx,data=data: self.__edit_entry(idx,data)
                                ),
                                ft.OutlinedButton(
                                    icon = ft.Icons.CANCEL_OUTLINED,
                                    text="Cancel",
                                    icon_color=ft.Colors.RED_400,
                                    on_click=lambda e: self.page.close(self.edit_transaction_dialogue_box)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                    ]
                )
            )
        )
        self.page.open(self.edit_transaction_dialogue_box) 

    def ___view_transactions(self):

        def determin_color(dt):
            if dt["kind"] == 'x':
                return ft.Colors.BLUE_100
            elif dt["kind"] == '+':
                return ft.Colors.GREEN_100
            else:
                return ft.Colors.RED_100
        if self.category_dropdown.value is None or self.category_dropdown.value == "All":
            # transactions = self.fetch_transactions()
            transactions = self.run_query("""
                SELECT * FROM transactions WHERE date BETWEEN ? AND ? ORDER BY date DESC
            """, (self.start, self.end), fetch=True)
        else:
            transactions = self.fetch_transactions(category=self.category_dropdown.value)
        if transactions == []:
            column_name = [col["name"] for col in TRANSACTION_FIELD_NAMES if col not in self.exclude_list and col["to_show"]]
        else:
            column_name = [col for col in transactions[0].keys() if col not in self.exclude_list]
        return ft.DataTable(
            border=ft.border.all(1,ft.Colors.BLACK),
            columns=[ft.DataColumn(ft.Text(""))] + [
                ft.DataColumn(ft.Text(col.capitalize())) for col in column_name
            ] + [ft.DataColumn(ft.Text(""))]*2,
            rows=[
                ft.DataRow(
                    color= determin_color(dt),
                    cells = [
                            ft.DataCell(ft.Text(idx+1))
                        ] + 
                        [ 
                            ft.DataCell(
                                ft.Text(
                                    value = entry if type(entry) != int else abs(entry),
                                    weight = ft.FontWeight.BOLD if key == "Price" else ft.FontWeight.NORMAL,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ) for key,entry in dt.items() if key in self.include_list
                        ] + 
                        [
                            ft.DataCell(
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_DOCUMENT,
                                    on_click=lambda e,idx=dt["id"],data=dt : self.__open_edit_dialogue_box(idx,data)
                                )
                            ),
                            ft.DataCell(
                                ft.IconButton(
                                    icon=ft.Icons.HIGHLIGHT_REMOVE_OUTLINED,
                                    on_click=lambda e,i=dt["id"],data=dt : self.__delete_entry(i,data),
                                    data=idx,
                                ),
                            )
                        ]
                ) for idx,dt in enumerate(transactions) if self.start <= datetime.datetime.strptime(dt["date"],'%Y-%m-%d').date() <= self.end
            ],
            expand=True,
            heading_row_color = ft.Colors.GREY_50,
        )
        # return self.transactions_table
    
    def __save_transaction(self,e):
        error = False
        def price(value):
            if list(self.transaction_type.selected)[0] != '+':
                return 0 - int(value)
            return int(value)
        
        if self.vendor.controls[0].value is None:
            self.vendor.controls[0].error_text = "vendor is missing"
            error = True
        else:
            self.vendor.controls[0].error_text = ""
        if self.payment_method.controls[0].value is None:
            self.payment_method.controls[0].error_text = "payment method is missing"
            error = True
        else:
            self.payment_method.controls[0].error_text = ""
        if self.price.controls[0].value == "":
            self.price.controls[0].error_text = "price is missing"
            error = True
        else:
            self.price.controls[0].error_text = ""
        
        if self.periodic.controls[0].value == True and (self.frequency.value is None or self.frequency.value == ""):
            self.frequency.error_text = "frequency is missing"
            error = True
        else:
            self.frequency.error_text = ""
        
        if self.debt.controls[0].value == True and (self.debt_taker_name.value is None or self.debt_taker_name.value == ""):
            self.debt_taker_name.error_text = "person is missing"
            error = True
        else:
            self.debt_taker_name.error_text = ""

        if error:
            self.payment_method.update()
            self.price.update()
            self.vendor.update()
            self.frequency.update()
            self.debt_taker_name.update()
            self.logger.error("Missed a few values!!!!")
            return
        category = self.fetch_vendors(name = self.vendor.controls[0].value)
        data = {
                "date" : datetime.datetime.now().strftime("%Y-%m-%d"),
                "vendor" : self.vendor.controls[0].value,
                "category" : category[0]["category"] if len(category) > 0 else "Uncategorized",
                "price" : price(self.price.controls[0].value),
                "bank" : self.payment_method.controls[0].value,
                "mode" : list(self.payment_type.controls[0].selected)[0],
                "recurring" : self.periodic.controls[0].value,
                "frequency" : self.frequency.value,
                "debt" : self.debt.controls[0].value,
                "person" : self.debt_taker_name.value.capitalize(),
                "id" : self.generate_uuid(),
                "kind" : list(self.transaction_type.selected)[0],
            }
        data["bank_id"] = self.generate_id(data["bank"],data["mode"])
        data["cashback"] = abs(self.query_payment_methods(id=data["bank_id"])[0]["cashback"] * data["price"])/100 if data["kind"] == "-" else 0
        self.insert_transaction(data)

        if data["recurring"]:
            self.insert_recurring(data)
        
        if data["category"] in ["Investment","Invest"]:
            try:
                investment = self.fetch_investment(name=data["vendor"])[0]
                updated_price = investment.get("invested_value",0) + data["price"]
                self.update_investment(name=data["vendor"],invested_value=updated_price)
            except:
                investment = {}
                updated_price = investment.get("invested_value",0) + data["price"]
                self.insert_investment(name=data["vendor"],invested_value=updated_price)
        
        if list(self.transaction_type.selected)[0] != 'x':
            payment_id = self.query_payment_methods(id=data["bank_id"])[0]["parent"] if self.query_payment_methods(id=data["bank_id"])[0]["parent"] is not None else data["bank_id"]
            self.update_payment_method(
                payment_method_id= payment_id,
                balance = self.query_payment_methods(id=payment_id)[0]["balance"] + data["price"],
            )
        else:
            payment_id = self.query_payment_methods(id=data["bank_id"])[0]["parent"] if self.query_payment_methods(id=data["bank_id"])[0]["parent"] is not None else data["bank_id"]
            payment_id_1 = self.query_payment_methods(id=self.generate_id(data["vendor"],data["mode"]))[0]["parent"] if self.query_payment_methods(id=self.generate_id(data["vendor"],data["mode"]))[0]["parent"] is not None else self.generate_id(data["vendor"],data["mode"])
            self.update_payment_method(
                payment_method_id= payment_id ,
                balance = self.query_payment_methods(id=payment_id)[0]["balance"] + data["price"],
            )
            self.update_payment_method(
                payment_method_id= payment_id_1,
                balance = self.query_payment_methods(id=payment_id_1)[0]["balance"] - data["price"],
            )
        self.page.close(self.record_transaction_dialogue_box)
        self.page.views[-1].controls[-2].content = self.view_transaction()
        self.page.update()

    
    def add_transaction(self):
        def periodic(e):
            if self.periodic.controls[0].value == True:
                self.periodic.controls[1].disabled = False
            else:
                self.periodic.controls[1].disabled = True
                self.periodic.controls[1].value = ""
            self.record_transaction_dialogue_box.update()
        
        def debt(e):
            if self.debt.controls[0].value == True:
                self.debt.controls[1].disabled = False
            else:
                self.debt.controls[1].disabled = True
                self.debt_taker_name.value = ""
            self.record_transaction_dialogue_box.update()

        def modes(e):
            self.payment_type.controls[0].segments = [PAYMENT_METHODS_SEGMENT[payment["mode"]] for payment in self.query_payment_methods(bank=e.data)]
            self.payment_type.controls[0].disabled = False
            self.payment_type.update()

        def transfer(e):
            if list(self.transaction_type.selected)[0] == 'x':
                self.vendor.controls[0].options = [ft.DropdownOption(dt) for dt in set(payment["bank"] for payment in self.get_payment_methods())]
                self.vendor.controls[0].label = "To"
                self.payment_method.controls[0].label = "From"
                self.payment_type.controls[0].segments = [
                    ft.Segment(
                        value="Savings Account",
                        icon=ft.Icon(ft.Icons.ACCOUNT_BALANCE_OUTLINED,color=ft.Colors.BLUE_ACCENT),
                        disabled=True,
                    )
                ]
                self.payment_type.controls[0].selected = {"Savings Account"}
            else:
                self.vendor.controls[0].options = [ft.DropdownOption(key=dt["name"]) for dt in self.fetch_vendors()]
                self.vendor.controls[0].label = "Vendor"
                self.payment_method.controls[0].label = "Payment Method"
                self.payment_type.controls[0].segments = list(PAYMENT_METHODS_SEGMENT.values())
            
            self.vendor.update()
            self.payment_method.update()
            self.payment_type.update()
            self.record_transaction_dialogue_box.update()
        
        def remove_payment_methods(e):
            if self.transaction_type.selected == {'x'}:
                self.payment_method.controls[0].options = [ft.DropdownOption(dt) for dt in set(payment["bank"] for payment in self.get_payment_methods()) if dt != e.control.value]
                self.payment_method.update()
            else:
                self.payment_method.controls[0].options = [ft.DropdownOption(dt) for dt in set(payment["bank"] for payment in self.get_payment_methods())]
                self.payment_method.update()

        self.frequency = ft.Dropdown(
                        label="Recurring Period",
                        expand=True,
                        options=[
                            ft.DropdownOption(key="Yearly"),
                            ft.DropdownOption(key="Monthly"),
                            ft.DropdownOption(key="Weekly"),
                            ft.DropdownOption(key="Daily"),
                            
                        ],
                        disabled=True,
                    )

        self.debt_taker_name = ft.TextField(
            label="Paid to",
            expand=True,
            disabled=True,
        )

        self.periodic = ft.Row([
                ft.Switch(value=False,on_change=periodic),
                self.frequency
        ])
        
        self.debt = ft.Row([
                ft.Switch(label="Debt", value=False,on_change=debt),
                self.debt_taker_name
            ])

        self.transaction_type = ft.SegmentedButton(
                        selected={"-"},
                        allow_multiple_selection=False,
                        show_selected_icon=True,
                        segments=[
                            ft.Segment(
                                value="-",
                                icon=ft.Icon(ft.Icons.REMOVE,color=ft.Colors.RED),
                            ),
                            ft.Segment(
                                value="x",
                                icon=ft.Icon(ft.Icons.SWAP_HORIZ,color=ft.Colors.BLACK),
                            ),
                            ft.Segment(
                                value="+",
                                icon=ft.Icon(ft.Icons.ADD,color=ft.Colors.GREEN),
                            ),
                        ],
                        on_change=transfer,
                    )
        self.vendor = ft.Row(
                            [
                                ft.Dropdown(
                                    label="Vendor",
                                    expand=True,
                                    enable_search = True,
                                    enable_filter = True,
                                    focused_border_color = ft.Colors.RED,
                                    options = [ft.DropdownOption(key=dt["name"]) for dt in self.fetch_vendors()],
                                    on_change=remove_payment_methods
                                )
                            ]
                        )
        self.payment_method = ft.Row(
                        controls=[
                            ft.Dropdown(
                                label="Payment Method",
                                expand=True,
                                enable_search=True,
                                enable_filter=True,
                                focused_border_color=ft.Colors.RED,
                                options=[ft.DropdownOption(dt) for dt in set(payment["bank"] for payment in self.get_payment_methods())],
                                on_change=modes
                            ),
                        ],
                        vertical_alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10
                    )
        self.payment_type = ft.Row(
                                controls=[
                                    ft.SegmentedButton(
                                        selected={"Credit Card"},
                                        allow_multiple_selection=False,
                                        show_selected_icon=True,
                                        expand = True,
                                        # direction=ft.Axis(value="vertical"),
                                        segments= list(PAYMENT_METHODS_SEGMENT.values()),
                                        disabled=True
                                    )
                                ],
                                vertical_alignment=ft.MainAxisAlignment.CENTER,
                                spacing=10
                            )
        self.price = ft.Row(
                            [
                                ft.TextField(
                                    label="Price",
                                    expand=True,
                                    keyboard_type=ft.KeyboardType.NUMBER
                                )
                            ]
        )

        self.record_transaction_dialogue_box = ft.AlertDialog(
            title = ft.Text(
                "New Transaction",
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.LIGHT_BLUE_700
            ),
            content = ft.Container(
                expand=True,
                content = ft.Column(
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                    controls= [
                        self.transaction_type,
                        self.vendor,
                        self.payment_method,
                        self.payment_type,
                        self.price,
                        self.periodic,
                        self.debt,
                        ft.Row(
                            controls=[
                                ft.OutlinedButton(
                                    icon = ft.Icons.SEND,
                                    text="Save",
                                    icon_color=ft.Colors.GREEN_400,
                                    on_click= self.__save_transaction
                                ),
                                ft.OutlinedButton(
                                    icon = ft.Icons.CANCEL_OUTLINED,
                                    text="Cancel",
                                    icon_color=ft.Colors.RED_400,
                                    on_click=lambda e: self.page.close(self.record_transaction_dialogue_box)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ),
            alignment=ft.alignment.center,
        )
        self.page.open(self.record_transaction_dialogue_box)
    

    def view_transaction(self,external = False):
        def change_start_end_time(delta:int):
            self.start = datetime.datetime(
                day=self.start.day,
                month=self.start.month+delta,
                year=self.start.year
            ).date()
            self.end = datetime.datetime(
                day=self.end.day,
                month=self.end.month+delta,
                year=self.end.year
            ).date()
            self.view_transaction(external=True)
        if external == False:
            self.start,self.end = self.load_start_end_date()
        self.transactions_table = ft.Container(ft.Row(
                alignment =ft.MainAxisAlignment.CENTER,
                vertical_alignment = ft.CrossAxisAlignment.CENTER,
                controls = [
                    ft.Container(
                        expand=True,
                        content = ft.Column(
                            tight=True,
                            scroll=ft.ScrollMode.HIDDEN,
                            controls= [
                                ft.Row(
                                    [
                                        ft.IconButton(
                                            icon =ft.Icons.ARROW_BACK_SHARP,  
                                            on_click=lambda e: change_start_end_time(-1)
                                        ),
                                        ft.Text(
                                            value=f"{self.start}",
                                            text_align=ft.TextAlign.CENTER,
                                            weight=ft.FontWeight.BOLD,
                                            size=20,
                                        ),
                                        ft.Icon(ft.Icons.ARROW_FORWARD_SHARP),
                                        ft.Text(
                                            value=f"{self.end}",
                                            text_align=ft.TextAlign.CENTER,
                                            weight=ft.FontWeight.BOLD,
                                            size=20,
                                        ),
                                        ft.IconButton(
                                            icon =ft.Icons.ARROW_FORWARD_SHARP,
                                            on_click=lambda e: change_start_end_time(1)
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    expand = True,
                                    tight = True
                                ),
                                self.category_dropdown,
                                ft.Row([self.___view_transactions()],scroll=ft.ScrollMode.HIDDEN)
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                    )
                ],
            ))
        if external == True:
            self.page.views[-1].controls[-2].content = self.transactions_table
            self.page.update()
        return self.transactions_table
    
        