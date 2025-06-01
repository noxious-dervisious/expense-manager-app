import flet as ft
from transactions import Transactions
from settings import Settings
from constants import *
import logging
from transactions import Transactions
from overview import Overview
from budget import Budget
from track import Track
from settings import Settings

logging.basicConfig(
    level=logging.INFO,  # or INFO, WARNING, ERROR as needed
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

def main(page: ft.Page):

    transactions = Transactions(page)
    overview = Overview(page)
    budget = Budget(page)
    tracker = Track(page)
    settings = Settings(page)
    # settings.create_tables()
    data_container = ft.Container(
        alignment=ft.alignment.center
    )
    
    view_overview_box = ft.Container(
                                    content=ft.Text("Overview",weight=ft.FontWeight.BOLD,color=ft.Colors.BLACK87),
                                    padding=20,
                                    bgcolor="#CBD5E1",
                                    border_radius = 50,
                                    on_click=lambda e: view_overview()
                                )
        
    view_transactions_box = ft.Container(
                                content=ft.Text("Transactions",weight=ft.FontWeight.BOLD,color=ft.Colors.BLACK87),
                                padding=20,
                                bgcolor="#CBD5E1",
                                border_radius = 50,
                                on_click=lambda e: view_transactions()
                            )
    view_status_box = ft.Container(
                                content=ft.Text("Track",weight=ft.FontWeight.BOLD,color=ft.Colors.BLACK87),
                                padding=20,
                                border_radius = 50,
                                bgcolor="#CBD5E1",
                                on_click=lambda e: view_status()
                            )
    view_budget_box =ft.Container(
                                content=ft.Text("Budget",weight=ft.FontWeight.BOLD,color=ft.Colors.BLACK87),
                                padding=20,
                                border_radius = 50,
                                bgcolor="#CBD5E1",
                                on_click=lambda e: view_budget(),
                            )
    def reset_all_view_boxes():
        view_budget_box.bgcolor = "#CBD5E1"
        view_overview_box.bgcolor = "#CBD5E1"
        view_transactions_box.bgcolor = "#CBD5E1"
        view_status_box.bgcolor = "#CBD5E1"
        
    def update_all_boxes():
        view_status_box.update()
        view_budget_box.update()
        view_transactions_box.update()
        view_overview_box.update()

    def view_transactions():
        data_container.content = transactions.view_transaction()
        reset_all_view_boxes()
        view_transactions_box.bgcolor = "#818CF8"
        update_all_boxes()
        data_container.update()
    
    def view_overview():
        data_container.content = overview.view_table()
        reset_all_view_boxes()
        view_overview_box.bgcolor = "#818CF8"
        update_all_boxes()
        data_container.update()
    
    def view_budget():
        data_container.content = budget.view_budget_table()
        reset_all_view_boxes()
        view_budget_box.bgcolor = "#818CF8"
        update_all_boxes()
        data_container.update()
    
    def view_status():
        data_container.content = tracker.view_progress_status()
        reset_all_view_boxes()
        view_status_box.bgcolor = "#818CF8"
        update_all_boxes()
        data_container.update()

    def home_page(page: ft.Page):
        page.theme_mode = ft.ThemeMode.LIGHT
        # page.bgcolor = "#1F1F1F"
        page.views.append(
             ft.View(
                    "/",
                    floating_action_button=ft.FloatingActionButton(
                        icon=ft.Icons.ADD,
                        bgcolor=ft.Colors.YELLOW_ACCENT,
                        on_click=lambda e: transactions.add_transaction(),
                        shape= ft.CircleBorder()
                    ),
                    controls=[
                        ft.AppBar(
                            title=ft.Text(
                                "Expense Manager".upper(),
                                color=ft.Colors.BLUE_900,
                                weight = ft.FontWeight.BOLD,
                            ),
                            actions = [
                                ft.Container(
                                    ft.OutlinedButton(
                                        icon=ft.Icons.SETTINGS,
                                        text="Settings",
                                        on_click=lambda e: page.go("/settings"),
                                        expand=True,
                                    ),
                                    padding=ft.padding.all(10)
                                )
                            ]
                        ),
                        ft.Row(
                            alignment =ft.MainAxisAlignment.CENTER,
                            vertical_alignment = ft.CrossAxisAlignment.CENTER,
                            controls = [
                                view_overview_box,
                                view_transactions_box,
                                view_status_box,
                                view_budget_box
                            ],
                            expand=True,
                            tight=True,
                            scroll=ft.ScrollMode.HIDDEN,
                        ),
                        data_container,
                    ],
                    scroll=ft.ScrollMode.AUTO,
                )
        )
    # Define the route change handler
    def route_change(route):
        page.views.clear()
        if page.route == "/":
            home_page(page)
        if page.route == "/settings":
            Settings(page).landing_page()
        page.update()

    page.on_route_change = route_change
    page.go(page.route)
    settings.adjust_recurring_payments()
    view_overview()
    
ft.app(target=main)
