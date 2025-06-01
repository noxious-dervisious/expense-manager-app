import flet as ft
from datetime import datetime
from constants import *
import logging
from sql_utils import SQLiteUtils

class PaymentMethods(SQLiteUtils):
    def __init__(self,page:ft.Page):
        super().__init__()
        self.page = page
        self.logger = logging.getLogger(__name__)
        
    def list_available_methods(self,e):
        payment_methods = self.query_payment_methods(bank=e.control.value)
        print(payment_methods)
        self.type.controls[0].options.extend([ft.DropdownOption(key=dt["mode"]) for dt in payment_methods])
        self.type.update()

    def payment_method_table(self):
        payment_methods = self.get_payment_methods()
        rows = []
        for payment_method in payment_methods:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(payment_method["bank"])),
                        ft.DataCell(ft.Text(payment_method["mode"])),
                        ft.DataCell(ft.Text(payment_method["cashback"])),
                        ft.DataCell(ft.Text(payment_method["due_date"])), 
                    ]
                )
            )
        self.payment_method_table_content = ft.Row(
            [
                ft.DataTable(
                    expand=True,
                    columns = [
                        ft.DataColumn(ft.Text("Bank",weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Method",weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Cashback",weight=ft.FontWeight.BOLD),numeric=True),
                        ft.DataColumn(ft.Text("Due Date",weight=ft.FontWeight.BOLD)),
                    ],
                    rows=rows,
                    bgcolor=ft.Colors.BLUE_50
                )
            ],
            expand=True,
            tight=True,
            scroll=ft.ScrollMode.AUTO
        )
        return self.payment_method_table_content
    
    def __add_payment_method(self,e):
        payment_methods = self.get_payment_methods()
        check = False
        for payment_method in payment_methods:
            if payment_method["bank"] == self.name.controls[0].value and  payment_method["mode"] == self.type.controls[0].value:
                self.logger.error("Payment method matching your specification(s) already exists!!!")
                self.page.close(self.new_payment_dialogue_box)
                return
        if self.name.controls[0].value.upper() == "" or self.name.controls[0].value.upper() is None:
            self.name.controls[0].error_text = "Bank name is missing"
            check = True
        else:
            self.name.controls[0].error_text = ""
        if self.type.controls[0].value is None or self.type.controls[0].value == "":
            self.type.controls[0].error_text = "Method is missing"
            check = True
        else:
            self.type.controls[0].error_text = ""
        if self.type.controls[0].value == "Credit Card" and self.billing_data_for_credit_card.value == "" or self.billing_data_for_credit_card.value is None:
            self.billing_data_for_credit_card.error_text = "Missing billing date"
            check = True
        else:
            self.billing_data_for_credit_card.error_text = ""
        self.name.controls[0].update()
        self.type.controls[0].update()
        self.billing_data_for_credit_card.update()
        if check:
            return 
        payment_method = {
            "bank" : self.name.controls[0].value.upper(),
            "mode" : self.type.controls[0].value,
            "cashback" : 0 if self.percentage.controls[0].value == "" else int(self.percentage.controls[0].value),
            "due_date" : datetime.strptime(self.billing_data_for_credit_card.value,"%d/%m/%Y").day if self.billing_data_for_credit_card.value != "" else "",
            "balance" : 0 if self.balance.controls[0].value == "" else int(self.balance.controls[0].value),
            "acc_number" : self.account_number.controls[0].value,
            "parent" : self.associated_account.controls[0].value,
        }
        self.insert_payment_method(payment_method)
        self.logger.info(f"Successfully added Bank : {self.name.controls[0].value} Method : {self.type.controls[0].value}")
        self.payment_method_table_content.update()
        self.page.close(self.new_payment_dialogue_box)
        
    def __remove_payment_method(self,e):
        self.delete_payment_method_from_table(self.generate_id(self.name.controls[0].value,self.type.controls[0].value))
        self.logger.info(f"Removed Bank : {self.name.controls[0].value} Method : {self.type.controls[0].value}")
        self.payment_method_table_content.update()
        self.page.close(self.delete_payment_dialogue_box)
        
    def new_payment_method(self):
        def set_date(e):
            self.billing_data_for_credit_card.value = self.date_picker.value.strftime("%d/%m/%Y")
            self.billing_data_for_credit_card.update()

        def need_billing_date(e):
            if e.data == "Credit Card":
                self.billing_data_for_credit_card.disabled = False
            else:
                self.billing_data_for_credit_card.disabled = True
            if e.data == "Credit Card" or e.data == "Savings Account":
                self.balance.controls[0].disabled = False
            else:
                self.balance.controls[0].disabled = True
            if e.data == "Savings Account":
                self.account_number.controls[0].disabled = False
            else:
                self.account_number.controls[0].disabled = True
            if e.data == "UPI" or e.data == "Debit Card":
                self.associated_account.controls[0].disabled = False
                self.associated_account.controls[0].options = [ft.DropdownOption(text=f"{dt["bank"]}(***{dt["acc_number"]})",key=dt["id"]) for dt in self.query_payment_methods(mode = "Savings Account")]
            else:
                self.associated_account.controls[0].disabled = True
            self.billing_data_for_credit_card.update()
            self.balance.update()
            self.account_number.update()
            self.associated_account.update()
        
        self.name = ft.Row(
                            [
                                ft.TextField(
                                    label="Bank",
                                    expand=True
                                )
                            ]
                        )
        self.type = ft.Row(
                            [
                                ft.Dropdown(
                                    label="Method",
                                    expand=True,
                                    options =[ft.DropdownOption(key=dt) for dt in PAYMENT_METHODS],
                                    on_change=need_billing_date
                                )
                            ]
                        )
        self.percentage = ft.Row(
                                [
                                    ft.TextField(
                                        label="Percentage",
                                        expand=True,
                                        suffix_icon=ft.Icons.PERCENT,
                                        keyboard_type=ft.KeyboardType.NUMBER,
                                    )
                                ],
                        )
        self.billing_data_for_credit_card = ft.TextField(
            label="Billing date",
            suffix_icon = ft.IconButton(
                icon=ft.Icons.CALENDAR_MONTH,
                on_click= lambda e : self.page.open(self.date_picker)
            ),
            disabled= True
        )

        self.date_picker =  ft.DatePicker(
            on_change = set_date
        )

        self.balance = ft.Row(
                            [
                                ft.TextField(
                                    label="Current Balance",
                                    expand=True,
                                    suffix_icon=ft.Icons.CURRENCY_RUPEE_OUTLINED,
                                    disabled= True,
                                    keyboard_type=ft.KeyboardType.NUMBER,
                                )
                            ],
                        )

        self.account_number = ft.Row(
                            [
                                ft.TextField(
                                    label="Account Number - 4 digits",
                                    input_filter=ft.NumbersOnlyInputFilter(),
                                    keyboard_type=ft.KeyboardType.NUMBER,
                                    expand=True,
                                    suffix_icon=ft.Icons.ONETWOTHREE_SHARP,
                                    disabled= True,
                                )
                            ],
                        )
        
        self.associated_account = ft.Row(
                            [
                                ft.Dropdown(
                                    label="Associated Account",
                                    expand=True,
                                )
                            ]
                        )
        
        self.new_payment_dialogue_box = ft.AlertDialog(
            title = "Add new payment methods",
            content = ft.Container(
                ft.Column(
                    tight=True,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    controls= [
                        self.name,
                        self.type,
                        self.account_number,
                        self.balance,
                        self.percentage,
                        self.billing_data_for_credit_card,
                        self.associated_account,
                        ft.Row(
                            controls=[
                                ft.OutlinedButton(
                                    icon = ft.Icons.SEND,
                                    text="Save",
                                    icon_color=ft.Colors.GREEN_400,
                                    on_click= self.__add_payment_method
                                ),
                                ft.OutlinedButton(
                                    icon = ft.Icons.CANCEL_OUTLINED,
                                    text="Cancel",
                                    icon_color=ft.Colors.RED_400,
                                    on_click=lambda e: self.page.close(self.new_payment_dialogue_box)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        )
                    ]
                )
            )
        )
        return self.new_payment_dialogue_box
    
    def delete_payment_method(self):
        payment_methods = set()
        for payment_method in self.get_payment_methods():
            payment_methods.add(payment_method["bank"])
        self.name = ft.Row(
                            [
                                ft.Dropdown(
                                    label="Bank",
                                    expand=True,
                                    options = [ft.DropdownOption(key=payment_method) for payment_method in payment_methods],
                                    on_change=self.list_available_methods
                                )
                            ]
                        )
        self.type = ft.Row(
                            [
                                ft.Dropdown(
                                    label="Method",
                                    expand=True,
                                )
                            ]
                        )
        self.delete_payment_dialogue_box = ft.AlertDialog(
            title = "Delete payment methods",
            content = ft.Container(
                ft.Column(
                    tight=True,
                    controls= [
                        self.name,
                        self.type,
                        ft.Row(
                            controls=[
                                ft.OutlinedButton(
                                    icon = ft.Icons.SEND,
                                    text="Save",
                                    icon_color=ft.Colors.GREEN_400,
                                    on_click= self.__remove_payment_method
                                ),
                                ft.OutlinedButton(
                                    icon = ft.Icons.CANCEL_OUTLINED,
                                    text="Cancel",
                                    icon_color=ft.Colors.RED_400,
                                    on_click=lambda e: self.page.close(self.delete_payment_dialogue_box)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        )
                    ]
                )
            )
        )
        return self.delete_payment_dialogue_box
    
    