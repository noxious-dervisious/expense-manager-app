import flet as ft
from sql_utils import SQLiteUtils
from constants import *
import logging

class Categories(SQLiteUtils):
    def __init__(self,page:ft.Page):
        super().__init__()
        self.page = page
        self.logger = logging.getLogger(__name__)
        self.create_categories_table()

    def __add_categories(self, e):
        name = self.name.controls[0].value.capitalize()
        if not name:
            self.name.controls[0].error_text = "Name cannot be empty"
            self.name.update()
            return
        self.insert_category(name)
        self.categories = self.fetch_categories()
        self.page.update()
        self.page.close(self.new_categories_dialogue_box)

    def __remove_categories(self, e):
        name = self.name.controls[0].value
        if name not in self.categories:
            self.name.controls[0].error_text = "Please select a valid value"
            self.name.update()
            return
        self.delete_category(name)
        self.categories = self.fetch_categories()
        self.page.close(self.delete_categories_dialogue_box)
        self.page.update()

    def add_new_categories(self):
        self.name = ft.Row(
            [
                ft.TextField(
                    label="Name",
                    expand=True
                )
            ]
        )
        self.new_categories_dialogue_box = ft.AlertDialog(
            title="Add new categories",
            content=ft.Container(
                ft.Column(
                    tight=True,
                    controls=[
                        self.name,
                        ft.Row(
                            controls=[
                                ft.OutlinedButton(
                                    icon=ft.Icons.SEND,
                                    text="Save",
                                    icon_color=ft.Colors.GREEN_400,
                                    on_click=self.__add_categories
                                ),
                                ft.OutlinedButton(
                                    icon=ft.Icons.CANCEL_OUTLINED,
                                    text="Cancel",
                                    icon_color=ft.Colors.RED_400,
                                    on_click=lambda e: self.page.close(self.new_categories_dialogue_box)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        )
                    ]
                )
            )
        )
        return self.new_categories_dialogue_box

    def delete_categories(self):
        self.categories = self.fetch_categories()
        self.name = ft.Row(
            [
                ft.Dropdown(
                    label="Name",
                    expand=True,
                    options=[
                        ft.DropdownOption(key=dt) for dt in self.categories
                    ]
                )
            ]
        )
        self.delete_categories_dialogue_box = ft.AlertDialog(
            title="Delete categories",
            content=ft.Container(
                ft.Column(
                    tight=True,
                    controls=[
                        self.name,
                        ft.Row(
                            controls=[
                                ft.OutlinedButton(
                                    icon=ft.Icons.SEND,
                                    text="Save",
                                    icon_color=ft.Colors.GREEN_400,
                                    on_click=self.__remove_categories
                                ),
                                ft.OutlinedButton(
                                    icon=ft.Icons.CANCEL_OUTLINED,
                                    text="Cancel",
                                    icon_color=ft.Colors.RED_400,
                                    on_click=lambda e: self.page.close(self.delete_categories_dialogue_box)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        )
                    ]
                )
            )
        )
        return self.delete_categories_dialogue_box

    def categories_table(self):
        self.categories = self.fetch_categories()
        self.categories_table_content = ft.Card(
            content=ft.Container(
                height=300,
                content=ft.Column(
                    [
                        ft.ListTile(
                            ft.Text(
                                dt,
                                text_align=ft.TextAlign.CENTER,
                                weight=ft.FontWeight.BOLD
                            ),
                            title_alignment=ft.ListTileTitleAlignment.CENTER
                        ) for dt in self.categories
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO,
                    tight=True,
                    expand=True
                )
            )
        )
        return self.categories_table_content