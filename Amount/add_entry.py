from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
import sqlite3
from datetime import datetime, date
import re

class AddEntryScreen(MDScreen):

    def home_button(self):
        self.ids.top_app_bar.right_action_items = []
        self.clear_fields()
        for child in self.ids.md_list.children:
            child.error = False
            child.focus = False
        self.screen_manager.current = "home"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = MDApp.get_running_app()
        self.screen_manager = app.screen_manager
        self.dat = None
        transaction_type_menu = ["Debit", "Credit"]
        transaction_type_options = [
            {
                "viewclass": "OneLineListItem",
                "text": f"{type}",
                "height": dp(40),
                "on_release": lambda x = type: self.transaction_type_callback(x),
            } for type in transaction_type_menu
        ]
        self.transaction_type_menu = MDDropdownMenu(
            items = transaction_type_options,
            position = "bottom",
            #width_mult = 4,
            caller = self.ids.transaction_type,
        )
        self.transaction_type_menu.width = self.ids.transaction_type.width
        transaction_method_menu = ["Cash", "Check", "GPay", "Paytm", "PhonePe"]
        transaction_method_options = [
            {
                "viewclass": "OneLineListItem",
                "text": f"{method}",
                "height": dp(40),
                "on_release": lambda x = method: self.transaction_method_callback(x),
            } for method in transaction_method_menu
        ]
        self.transaction_method_menu = MDDropdownMenu(
            items = transaction_method_options,
            position = "bottom",
            #width_mult = 4,
            caller = self.ids.transaction_method,
        )
        self.transaction_method_menu.width = self.ids.transaction_method.width

    def name_filter(self, text, from_undo):
        return re.sub(r"[^A-Za-z \-']", '', text)
    
    def type_filter(self, text, from_undo):
        if text in ["Debit", "Credit"]:
            return text  # allow values
        else:
            return ''

    def transaction_type_callback(self, text):
        self.ids.transaction_type.text = text
        self.transaction_type_menu.dismiss()

    def method_filter(self, text, from_undo):
        if text in ["Cash", "Check", "GPay", "Paytm", "PhonePe"]:
            return text  # allow values
        else:
            return ''

    def transaction_method_callback(self, text):
        self.ids.transaction_method.text = text
        self.transaction_method_menu.dismiss()

    def toggle_opacity(self, obj):
        if not obj.text.strip():
            obj.error = True
        for i in self.ids.md_list.children:
            if i.text.strip() == "":
                for child in self.ids.top_app_bar.ids.right_actions.children:
                    if child.disabled == False:
                        child.disabled = True
                return
        for child in self.ids.top_app_bar.ids.right_actions.children:
            child.disabled = False

    def show_options(self):
        if self.ids.top_app_bar.right_action_items == []:
            self.ids.top_app_bar.right_action_items = [
                ["close", lambda x: self.cancel_entry()],
                ["check", lambda x: self.submit_entry()]
            ]
            Clock.schedule_once(self.set_button_opacity, 0)

    def set_button_opacity(self, *args):
        if self.ids.top_app_bar.ids.right_actions.children != []:
            for child in self.ids.top_app_bar.ids.right_actions.children:
                child.disabled = True
        
    def cancel_entry(self):
        '''for i in self.ids.md_list.children[::-1]:
            if i.text.strip() == "":
                return'''
        self.ids.top_app_bar.right_action_items = []
        self.clear_fields()
        for child in self.ids.md_list.children:
            child.error = False
        self.screen_manager.current = "home"

    def submit_entry(self):
        '''for i in self.ids.md_list.children[::-1]:
            if i.text.strip() == "":
                text=f"Please {i.helper_text} first"
                self.dialog_build(text)
                return'''
        person_name = self.ids.person_name.text.strip()
        branch_name = self.ids.branch_name.text.strip()
        transaction_date = self.ids.transaction_date.text.strip()
        amount = self.ids.amount.text.strip()
        transaction_type = self.ids.transaction_type.text.strip()
        transaction_method = self.ids.transaction_method.text.strip()
        received_by = self.ids.received_by.text.strip()

        self.add_entry(person_name, branch_name, transaction_date, amount, transaction_type, transaction_method, received_by)

    def clear_fields(self):
        for field in self.ids.md_list.children:
            field.text = ""
            field.error = False

    def add_entry(self, person_name, branch_name, transaction_date, amount, transaction_type, transaction_method, received_by):
        self.conn = sqlite3.connect("account_details.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''INSERT INTO entries (person_name, branch_name, transaction_date, amount, transaction_type, transaction_method, received_by)
                               VALUES (?, ?, ?, ?, ?, ?, ?)''',
                            (person_name, branch_name, transaction_date, amount, transaction_type, transaction_method, received_by))
        self.conn.commit()
        self.conn.close()
        self.ids.top_app_bar.right_action_items = []
        self.clear_fields()
        for child in self.ids.md_list.children:
            child.error = False
        
        home_screen = self.screen_manager.get_screen("home")
        tab_bar = home_screen.ids.tabs.get_current_tab().title
        if tab_bar == "All Entries":
            home_screen.load_entries()
        elif tab_bar == "Credit Entries":
            home_screen.load_credit_entries()
        elif tab_bar == "Debit Entries":
            home_screen.load_debit_entries()
        self.screen_manager.current = "home"

    def show_date_picker(self):
        if not self.dat:
            self.dat = MDDatePicker(
                title = "Select Transaction Date",
                year = datetime.now().year,
                month = datetime.now().month,
                day = datetime.now().day,
                max_date = date.today()
            )
            self.dat.bind(
                on_save=self.on_date_selected,
                on_cancel=lambda instance, value: None
            )
        self.dat.open()

    def on_date_selected(self, instance, value, date_range):
        selected_date = value
        today = datetime.today().date()
        if selected_date <= today:
            self.ids.transaction_date.text = value.strftime("%Y-%m-%d")
            self.ids.transaction_date.helper_text_mode = "on_focus"
            self.ids.transaction_date.hint_text= "Transaction Date"
            self.ids.transaction_date.helper_text= "Enter the transaction date"
        else:
            self.ids.transaction_date.helper_text_mode = "persistent"
            self.ids.transaction_date.text = ""
            self.ids.transaction_date.hint_text = "Invalid Transaction Date"
            self.ids.transaction_date.helper_text = "Selected Date can not exceed today's date."       