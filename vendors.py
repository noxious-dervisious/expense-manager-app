import flet as ft
from constants import *
import logging
from sql_utils import SQLiteUtils

class Vendor(SQLiteUtils):
    def __init__(self,page:ft.Page):
        super().__init__()
        self.page = page
        self.logger = logging.getLogger(__name__)
        self.create_vendors_table()
        
    def __add_vendor(self, e):
        if self.name.controls[0].value == "":
            self.name.controls[0].error_text = "Name is a must"
            self.name.update()
            return
        if self.category.controls[0].value is None:
            self.category.controls[0].error_text = "Please specify a category"
            self.category.update()
            return
        name = self.name.controls[0].value
        category = self.category.controls[0].value
        self.insert_vendor(name, category)
        self.vendors = self.fetch_vendors()
        self.page.close(self.new_vendor_dialogue_box)

    def __remove_vendor(self, e):
        if self.name.controls[0].value is None:
            self.name.controls[0].error_text = "Name is a must"
            self.name.update()
            return
        name = self.name.controls[0].value
        self.delete_vendor_from_db(name)
        self.vendors = self.fetch_vendors()
        self.page.close(self.delete_vendor_dialogue_box)

    def view_vendor(self):
        self.vendors = self.fetch_vendors()
        rows = []
        for vendor in self.vendors:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(vendor["name"])),
                        ft.DataCell(ft.Text(vendor["category"])),
                    ]
                )
            )
        self.category_table_content = ft.DataTable(
            expand=True,
            columns=[
                ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Category", weight=ft.FontWeight.BOLD)),
            ],
            rows=rows,
            bgcolor=ft.Colors.BLUE_50
        )
        return self.category_table_content

    def add_vendor(self):
        # You may want to fetch categories from your categories table here
        self.categories = self.fetch_categories()
        self.name = ft.Row(
            [
                ft.TextField(
                    label="Vendor Name",
                    expand=True
                )
            ]
        )
        self.category = ft.Row(
            [
                ft.Dropdown(
                    label="Categories",
                    expand=True,
                    options=[ft.DropdownOption(key=dt.capitalize()) for dt in self.categories]
                )
            ]
        )
        self.new_vendor_dialogue_box = ft.AlertDialog(
            title="Add new vendor",
            content=ft.Container(
                ft.Column(
                    tight=True,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        self.name,
                        self.category,
                        ft.Row(
                            controls=[
                                ft.OutlinedButton(
                                    icon=ft.Icons.SEND,
                                    text="Save",
                                    icon_color=ft.Colors.GREEN_400,
                                    on_click=self.__add_vendor
                                ),
                                ft.OutlinedButton(
                                    icon=ft.Icons.CANCEL_OUTLINED,
                                    text="Cancel",
                                    icon_color=ft.Colors.RED_400,
                                    on_click=lambda e: self.page.close(self.new_vendor_dialogue_box)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        )
                    ]
                )
            )
        )
        return self.new_vendor_dialogue_box

    def delete_vendor(self):
        self.vendors = self.fetch_vendors()
        self.name = ft.Row(
            [
                ft.Dropdown(
                    label="Vendor",
                    expand=True,
                    options=[ft.DropdownOption(key=dt["name"]) for dt in self.vendors]
                )
            ]
        )
        self.delete_vendor_dialogue_box = ft.AlertDialog(
            title="Delete vendor",
            content=ft.Container(
                ft.Column(
                    tight=True,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        self.name,
                        ft.Row(
                            controls=[
                                ft.OutlinedButton(
                                    icon=ft.Icons.SEND,
                                    text="Save",
                                    icon_color=ft.Colors.GREEN_400,
                                    on_click=self.__remove_vendor
                                ),
                                ft.OutlinedButton(
                                    icon=ft.Icons.CANCEL_OUTLINED,
                                    text="Cancel",
                                    icon_color=ft.Colors.RED_400,
                                    on_click=lambda e: self.page.close(self.delete_vendor_dialogue_box)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        )
                    ]
                )
            )
        )
        return self.delete_vendor_dialogue_box