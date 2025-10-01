from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
'''from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton'''
from datetime import datetime, date
import sqlite3
import re


class EditEntryScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = MDApp.get_running_app()
        self.screen_manager = app.screen_manager
        self.dat = None
        #self.error_dialog = None
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
            width_mult = 2,
            caller = self.ids.transaction_type,
        )
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
            width_mult = 2,
            caller = self.ids.transaction_method,
        )

    def name_filter(self, text, from_undo):
        return re.sub(r"[^A-Za-z \-']", '', text)

    def type_filter(self, text, from_undo):
        if text in ["Debit", "Credit"]:
            return text  # allow character
        else:
            return ''

    def transaction_type_callback(self, text):
        self.ids.transaction_type.text = text
        self.transaction_type_menu.dismiss()

    def method_filter(self, text, from_undo):
        if text in ["Cash", "Check", "GPay", "Paytm", "PhonePe"]:
            return text  # allow character
        else:
            return ''

    def transaction_method_callback(self, text):
        self.ids.transaction_method.text = text
        self.transaction_method_menu.dismiss()

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

    def clear_fields(self):
        for field in self.ids.md_list.children:
            field.text = ""

    def view_entry_button(self, instance):
        self.screen_manager.current = "view_entry"

    def toggle_opacity(self):
        row = self.screen_manager.get_screen("home").row
        self.row_item = [str(i) for i in row]
        count = 0
        for field in self.ids.md_list.children:
            if field.text.strip() in self.row_item:
                count += 1
        if count == len(self.row_item)-1: #row also includes id
            for child in self.ids.top_app_bar.ids.right_actions.children:
                if child.disabled == False: #child.opacity == 1:
                    #child.opacity = 0.5
                    child.disabled = True
        else:
            for child in self.ids.top_app_bar.ids.right_actions.children:
                #child.opacity = 1
                child.disabled = False

    def show_options(self):
        #def show_options(self, instance):
        if self.ids.top_app_bar.right_action_items == []:
            self.ids.top_app_bar.left_action_items = [
                ["home", lambda x: self.home_button()]
            ]
            '''self.ids.top_app_bar.right_action_items = [
                ["close", lambda x: self.cancel(instance)],
                ["check", lambda x: self.edit(instance)],
            ]'''
            self.ids.top_app_bar.right_action_items = [
                ["close", lambda x: self.cancel_entry()],
                ["check", lambda x: self.edit_entry()],
            ]
            Clock.schedule_once(self.set_button_opacity, 0)

    def set_button_opacity(self, *args):
        if self.ids.top_app_bar.ids.right_actions.children != []:
            for child in self.ids.top_app_bar.ids.right_actions.children:
                #child.opacity = 0.5
                child.disabled = True

    def home_button(self):
        self.ids.top_app_bar.left_action_items = [
            ["arrow-left", lambda x: self.view_entry_button(x)]
        ]
        self.ids.top_app_bar.right_action_items = []
        self.clear_fields()
        self.screen_manager.get_screen('view_entry').ids.top_app_bar.title = ""
        self.screen_manager.current = "home"

    '''def dialog_build(self, text):
        if not self.error_dialog:
            self.error_dialog = MDDialog(
                    title="Alert",
                    text=text,
                    buttons=[
                        MDFlatButton(
                            text = "DISMISS",
                            on_release = self.dismiss_dialog
                        )
                    ]
                )
            self.error_dialog.open()'''
    
    '''def dismiss_dialog(self, instance):
        self.dialog_error.dismiss()'''

    def edit_entry(self):
        #def edit(self, instance):
        '''row = self.screen_manager.get_screen("home").row
        self.row_item = [str(i) for i in row]
        if instance.text.strip() not in self.row_item:'''
        self.entry_id = self.screen_manager.get_screen("home").entry_id
        person_name = self.ids.person_name.text.strip()
        branch_name = self.ids.branch_name.text.strip()
        transaction_date = self.ids.transaction_date.text.strip()
        amount = self.ids.amount.text.strip()
        transaction_type = self.ids.transaction_type.text.strip()
        transaction_method = self.ids.transaction_method.text.strip()
        received_by = self.ids.received_by.text.strip()
        self.update_entry(self.entry_id, person_name, branch_name, transaction_date, amount, transaction_type, transaction_method, received_by)
        '''if person_name.isalpha():
            if branch_name.isalpha():
                try:
                    datetime.strptime(transaction_date, "%Y-%m-%d")
                    if re.match(r"^-?\d+(\.\d+)?$", amount):
                        if transaction_type in ['Debit', 'Credit']:
                            if transaction_method in ["Cash", "Check", "GPay", "Paytm", "PhonePe"]:
                                if received_by.isalpha():
                                    self.update_entry(self.entry_id, person_name, branch_name, transaction_date, amount, transaction_type, transaction_method, received_by)
                                else:
                                    text=f"Invalid Receiver's name, must not includes numbers and special characters."
                                    self.dialog_build(text)
                            else:
                                text=f"Invalid Transaction Method, must be choosen from the given option."
                                self.dialog_build(text)
                        else:
                            text=f"Invalid Transaction type, must be choosen from the given option."
                            self.dialog_build(text)
                    else:
                        text=f"Invalid Amount, must just includes numbers."
                        self.dialog_build(text)
                except ValueError:
                    text=f"Invalid Date format."
                    self.dialog_build(text)
            else:
                text=f"Invalid Branch Name, must not includes numbers and special characters."
        else:
            text=f"Invalid Person Name, must not includes numbers and special characters."
            self.dialog_build(text)'''

    def update_entry(self, entry_id, person_name, branch_name, transaction_date, amount, transaction_type, transaction_method, received_by):
        try:
            self.conn = sqlite3.connect("account_details.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute('''UPDATE entries SET person_name = ?, 
                                branch_name = ?, 
                                transaction_date = ?, 
                                amount = ?, 
                                transaction_type = ?,
                                transaction_method = ?,
                                received_by = ?
                                WHERE id = ?''',
                                (person_name, branch_name, transaction_date, amount, transaction_type, transaction_method, received_by, entry_id))
            self.conn.commit()
            self.conn.close()
            self.ids.top_app_bar.left_action_items = [
                ["arrow-left", lambda x: self.view_entry_button(x)]
            ]
            self.ids.top_app_bar.right_action_items = []
            self.clear_fields()

            home_screen = self.screen_manager.get_screen("home")
            tab_bar = home_screen.ids.tabs.get_current_tab().title
            if tab_bar == "All Entries":
                home_screen.load_entries()
            elif tab_bar == "Credit Entries":
                home_screen.load_credit_entries()
            elif tab_bar == "Debit Entries":
                home_screen.load_debit_entries()
            self.screen_manager.get_screen('view_entry').ids.top_app_bar.title = ""
            home_screen.view_entry(self.entry_id)
        except Exception as e:
            print(e)

    def cancel_entry(self):
        #def cancel(self, instance):
        '''row = self.screen_manager.get_screen("home").row
        self.row_item = [str(i) for i in row]
        if instance.text.strip() not in self.row_item:'''
        self.ids.top_app_bar.left_action_items = [
            ["arrow-left", lambda x: self.view_entry_button(x)]
        ]
        self.ids.top_app_bar.right_action_items = []
        self.clear_fields()
        self.screen_manager.get_screen('view_entry').ids.top_app_bar.title = ""
        self.screen_manager.current = "view"