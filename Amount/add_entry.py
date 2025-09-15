from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
import sqlite3
from datetime import datetime


class AddEntryScreen(MDScreen):

    dialog = None

    def home_button(self):
        self.screen_manager.current = "home"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = MDApp.get_running_app()
        self.screen_manager = app.screen_manager
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_options = [
            {
                "viewclass": "OneLineListItem",
                "text": f"{day}",
                "height": dp(40),
                "on_release": lambda x = day: self.day_callback(x),
            } for day in days
        ]
        self.day_menu = MDDropdownMenu(
            items = day_options,
            position = "bottom",
            width_mult = 2,
            caller = self.ids.day,
        )
        transaction_menu = ["Cash", "Check", "GPay", "Paytm", "PhonePe"]
        transaction_type_options = [
            {
                "viewclass": "OneLineListItem",
                "text": f"{type}",
                "height": dp(40),
                "on_release": lambda x = type: self.transaction_type_callback(x),
            } for type in transaction_menu
        ]
        self.transaction_type_menu = MDDropdownMenu(
            items = transaction_type_options,
            position = "bottom",
            width_mult = 2,
            caller = self.ids.transaction_type,
        )

    def day_callback(self, text):
        self.ids.day.text = text
        self.show_options()
        self.day_menu.dismiss()

    def transaction_type_callback(self, text):
        self.ids.transaction_type.text = text
        self.show_options()
        self.transaction_type_menu.dismiss()

    def show_options(self):
        self.ids.top_app_bar.right_action_items = [
            ["close", lambda x: self.cancel_entry()],
            ["check", lambda x: self.submit_entry()]
        ]

    def cancel_entry(self):
        for i in self.ids.grid_layout.children:
            if i.text == "":
                return
        self.clear_fields()
        self.screen_manager.current = "home"

    def submit_entry(self):
        for i in self.ids.grid_layout.children[::-1]:
            if i.text == "":
                self.dialog = MDDialog(
                    title="Alert",
                    text=f"Please {i.helper_text} first",
                    buttons=[
                        MDFlatButton(
                            text = "DISMISS",
                            on_release = self.dismiss_dialog
                        )
                    ]
                )
                self.dialog.open()
                return
        person_name = self.ids.person_name.text
        branch_name = self.ids.branch_name.text
        day = self.ids.day.text
        transaction_date = self.ids.transaction_date.text
        amount = self.ids.amount.text
        transaction_type = self.ids.transaction_type.text
        received_by = self.ids.received_by.text

        if not all([person_name, branch_name, day, transaction_date, amount, transaction_type, received_by]):
            print("Please fill all fields")

        else:
            try:
                datetime.strptime(transaction_date, "%Y-%m-%d")
                amount = float(amount)
                self.add_entry(person_name, branch_name, day, transaction_date, amount, transaction_type, received_by)
            except ValueError:
                print("Invalid date or amount format.")

        self.clear_fields()

    def dismiss_dialog(self, instance):
        self.dialog.dismiss()

    def clear_fields(self):
        self.ids.person_name.text = ""
        self.ids.branch_name.text = ""
        self.ids.day.text = ""
        self.ids.transaction_date.text = ""
        self.ids.amount.text = ""
        self.ids.transaction_type.text = ""
        self.ids.received_by.text = ""

    def add_entry(self, person_name, branch_name, day, transaction_date, amount, transaction_type, received_by):
        self.conn = sqlite3.connect("account_details.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''INSERT INTO entries (person_name, branch_name, day, transaction_date, amount, transaction_type, received_by)
                               VALUES (?, ?, ?, ?, ?, ?, ?)''',
                            (person_name, branch_name, day, transaction_date, amount, transaction_type, received_by))
        self.conn.commit()
        self.conn.close()
        self.screen_manager.get_screen("home").load_entries()
        self.screen_manager.current = "home"

    def show_date_picker(self):
        dat = MDDatePicker(
            title = "Select Transaction Date",
            year = datetime.now().year,
            month = datetime.now().month,
            day = datetime.now().day,
            max_date = datetime.today()
        )
        dat.bind(
            on_save=self.on_date_selected,
            on_cancel=lambda instance, value: None
        )
        dat.open()

    def on_date_selected(self, instance, value, date_range):
        self.ids.transaction_date.text = value.strftime("%Y-%m-%d")