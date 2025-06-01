import logging

import flet as ft
from constants import *
from sql_utils import SQLiteUtils

class Budget(SQLiteUtils):
    def __init__(self,page):
        super().__init__()
        self.page = page
        self.logger = logging.getLogger(__name__)

    def __total_spend_value(self,check=True):
        self.total = int(self.calculate_container.content.controls[0].value)
        self.spend = 0
        self.left = 0
        for line_item in self.budget_container.content.controls:
            self.spend += int(line_item.controls[1].value)
        self.left = self.total - self.spend
        self.calculate_container.content.controls[1].value = self.spend
        self.calculate_container.content.controls[2].value = self.left
        if check:
            self.calculate_container.update()
    
    def __remove_row(self,e):
        self.budget_container.content.controls.remove(self.rows[e.control.data])
        dropdown_value = self.rows[e.control.data].controls[0].value
        if dropdown_value is not None and dropdown_value != "":
            self.exclusion_list.remove(dropdown_value)
        self.budget_container.update()

    def __add_new_row(self):
        categories = self.fetch_categories()
        return ft.Row(
            [
                ft.Dropdown(
                    options = [ft.DropdownOption(key=cat) for cat in categories if cat not in self.exclusion_list],
                    label="Category",
                    on_change= lambda e: self.exclusion_list.append(e.control.value)
                ),
                ft.TextField(
                    label = "Spend Limit",
                    input_filter=ft.NumbersOnlyInputFilter(),
                    on_change= lambda e: self.__total_spend_value(),
                    keyboard_type=ft.KeyboardType.NUMBER
                ),
                ft.IconButton(
                    icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                    icon_color=ft.Colors.RED,
                    data=self.counter,
                    on_click = lambda e: self.__remove_row(e)
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            tight=True,
            scroll=ft.ScrollMode.AUTO
        )
    
    def __save_budget_details(self):
        self.budegting_tool = []    
        for idx,budget in enumerate(self.budget_container.content.controls):
            if budget.controls[0].value is None or budget.controls[0].value == "":
                self.budget_container.content.controls[idx].controls[0].error_text = "Please select a category"
            elif budget.controls[1].value is None or budget.controls[1].value == "":
                self.budget_container.content.controls[idx].controls[0].error_text = "Please specify a spend limit"
            else:
                data = {
                    "category" : budget.controls[0].value,
                    "spend_limit" : int(budget.controls[1].value)
                }
                self.insert_budgeting_tool(data["category"], data["spend_limit"])      

        total_spend_limit = int(self.calculate_container.content.controls[0].value) if self.calculate_container.content.controls[0].value != "" and self.calculate_container.content.controls[0].value is not None else 0
        if self.fetch_budgeting_tool(category="total") != []:
            self.update_budgeting_tool("total", spend_limit = total_spend_limit)
        else:
            self.insert_budgeting_tool("total", spend_limit = total_spend_limit)
        self.budget_container.update()
        
    def __add_existing_budget_info(self):
        budegting_tool = self.fetch_budgeting_tool()
        categories = self.fetch_categories()
        for line_items in budegting_tool:
            if line_items["category"] != "total":
                self.rows.append(
                    ft.Row(
                            [
                                ft.Dropdown(
                                    options = [ft.DropdownOption(key=cat) for cat in categories if cat not in self.exclusion_list],
                                    label="Category",
                                    on_change= lambda e: self.exclusion_list.append(e.control.value),
                                    value = line_items["category"]
                                ),
                                ft.TextField(
                                    label = "Spend Limit",
                                    input_filter=ft.NumbersOnlyInputFilter(),
                                    value = line_items["spend_limit"],
                                    keyboard_type=ft.KeyboardType.NUMBER
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                                    icon_color=ft.Colors.RED,
                                    data=self.counter,
                                    on_click = lambda e: self.__remove_row(e),
                                    # disabled=True
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            expand=True,
                            tight=True,
                            scroll=ft.ScrollMode.AUTO
                    )
                )
                self.counter += 1
                self.budget_container.content.controls.append(
                    self.rows[-1]
                )
                self.exclusion_list.append(line_items["category"])
        self.__total_spend_value(check=False)

    def __add_total_value_to_tracker(self):
        self.update_budgeting_tool("total", spend_limit = int(self.calculate_container.content.controls[0].value) if self.calculate_container.content.controls[0].value != "" and self.calculate_container.content.controls[0].value is not None else 0)
        self.__total_spend_value()
        
    def view_budget_table(self):
        def add_new_row():
            self.rows.append(self.__add_new_row())
            self.budget_container.content.controls.append(
                self.rows[-1]
            )
            self.counter += 1
            self.budget_table.update()
        
        self.counter = 0
        self.rows = []
        self.exclusion_list = []
        self.budget_container = ft.Container(
            content = ft.Column(),
        )
        categories = self.fetch_categories()
        budegting_tool = self.fetch_budgeting_tool()
        self.calculate_container = ft.Container(
            content = ft.Column(
                [
                    ft.TextField(
                        label="Total",
                        border_color=ft.Colors.BLUE_ACCENT,
                        value=sum([0] + [ items["spend_limit"] for items in budegting_tool if items["category"] == "total"]),
                        on_change=lambda e: self.__add_total_value_to_tracker(),
                        text_align=ft.TextAlign.CENTER,
                        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD,color=ft.Colors.BLUE_900,size=25),
                        content_padding=ft.padding.only(top=20, bottom=10),
                    ),
                    ft.TextField(
                        label="Spent",
                        border_color=ft.Colors.RED_900,
                        read_only=True,
                        text_align=ft.TextAlign.CENTER,
                        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD,color=ft.Colors.RED_900,size=25),
                        content_padding=ft.padding.only(top=20, bottom=10),
                    ),
                    ft.TextField(
                        label="Left",
                        border_color=ft.Colors.GREEN_900,
                        read_only=True,
                        text_align=ft.TextAlign.CENTER,
                        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD,color=ft.Colors.GREEN_900,size=25),
                        content_padding=ft.padding.only(top=20, bottom=10),
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
                scroll=ft.ScrollMode.AUTO
            ),
        )
        self.budget_table = ft.Column(
            [
                self.calculate_container,
                self.budget_container,
                ft.Row(
                    [
                        ft.ElevatedButton(
                            icon=ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED,
                            icon_color=ft.Colors.GREEN_900,
                            text="Add",
                            on_click= lambda e: add_new_row()
                        ),
                        ft.ElevatedButton(
                            icon=ft.Icons.CHECK_CIRCLE_OUTLINE_OUTLINED,
                            icon_color=ft.Colors.BLUE_ACCENT,
                            text="Save",
                            on_click= lambda e: self.__save_budget_details()
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    # expand=True,
                    tight=True,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            # expand=True,
            tight=True
        )
        self.__add_existing_budget_info()
        return self.budget_table