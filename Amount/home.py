from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import ThreeLineListItem
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.properties import StringProperty
from kivy.animation import Animation
from kivy.clock import Clock
import sqlite3

class ItemDrawer(ThreeLineListItem):
    icon = StringProperty()

class HomeScreen(MDScreen):

    dialog = None
    search_bar_active = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = MDApp.get_running_app()
        self.screen_manager = app.screen_manager
        self.instance = self.ids.tabs.children[0]

    def fetch_details(self, instance, rows):
        for row in rows:
            item = ItemDrawer(text=f"{row[1]} - {row[5]}", secondary_text=f"{row[4]}", tertiary_text=f"Received By: {row[7]}", icon="file-document-box")
            item.bind(on_release=lambda x, entry_id=row[0]: self.view_entry(entry_id))
            instance.add_widget(item)
        self.conn.close()

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        self.instance = instance_tab.children[0].children[-1]
        if tab_text == "all entries content":
            self.screen_manager.get_screen("home").ids.all_entry_list.clear_widgets()
            self.load_entries(self.instance)
        elif tab_text == "credit entries content":
            self.screen_manager.get_screen("home").ids.credit_entry_list.clear_widgets()
            self.load_credit_entries(self.instance)
        elif tab_text == "debit entries content":
            self.screen_manager.get_screen("home").ids.debit_entry_list.clear_widgets()
            self.load_debit_entries(self.instance)

    def load_entries(self, instance):
        self.conn = sqlite3.connect("account_details.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT * FROM entries ORDER BY transaction_date DESC")
        rows = self.cursor.fetchall()
        self.conn.close()
        self.fetch_details(instance, rows)

    def load_credit_entries(self, instance):
        self.conn = sqlite3.connect("account_details.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT * FROM entries WHERE transaction_type = 'Credit' ORDER BY transaction_date DESC")
        rows = self.cursor.fetchall()
        self.conn.close()
        self.fetch_details(instance, rows)

    def load_debit_entries(self, instance):
        self.conn = sqlite3.connect("account_details.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT * FROM entries WHERE transaction_type = 'Debit' ORDER BY transaction_date DESC")
        rows = self.cursor.fetchall()
        self.fetch_details(instance, rows)

    def menu_button(self):
        nav_drawer = self.ids.nav_drawer
        nav_drawer.set_state("toggle")
        if nav_drawer.state == "close":
            nav_drawer.set_state("open")
        else:
            None

    def search_option(self):
        self.top_app_bar = self.ids.top_app_bar
        self.search_input = self.ids.search_input
        self.search_button = self.ids.search_button
        
        if not self.search_bar_active:
            anim = Animation(opacity=1, duration=1, transition="out_quart")
            anim.start(self.search_input)
            self.top_app_bar.title = ""
            self.search_bar_active = True
        else:
            anim = Animation(opacity=0, duration=0.5, 
                             transition="in_quart", 
                             )
            anim.start(self.search_input)
            self.top_app_bar.title = "Account Details"
            self.search_input.text = ""
            self.search_bar_active = False

    def search(self, instance, text):
        self.search_text = f"%{text}%"
        self.conn = sqlite3.connect("account_details.db")
        self.cursor = self.conn.cursor()
        tup = tuple([self.search_text for i in range(8)])
        try:
            self.cursor.execute('''SELECT * FROM entries WHERE id LIKE ? 
                                OR person_name LIKE ? 
                                OR branch_name LIKE ? 
                                OR day LIKE ? 
                                OR transaction_date LIKE ? 
                                OR amount LIKE ? 
                                OR transaction_type LIKE ? 
                                OR received_by LIKE ? ''', tup)
            rows = self.cursor.fetchall()
            self.fetch_details(self.instance, rows)
        except sqlite3.OperationalError:
            self.dialog = MDDialog(
                title="Alert",
                text=f"An Error has occurred.....",
                buttons=[
                    MDFlatButton(
                        text = "DISMISS",
                        on_release = self.dismiss_dialog
                    )
                ]
            )
            self.dialog.open()

    def dismiss_dialog(self, instance):
        if self.dialog:
            self.dialog.dismiss()

    def view_entry(self, entry_id):
        self.entry_id = entry_id
        print(self.entry_id)
        self.conn = sqlite3.connect("account_details.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
        self.row = self.cursor.fetchone()
        self.conn.close()
        view_screen = self.screen_manager.get_screen("view_entry")
        view_screen.ids.top_app_bar.title += str(self.row[0])
        view_screen.ids.person_name.text += self.row[1]
        view_screen.ids.branch_name.text += self.row[2]
        view_screen.ids.day.text += self.row[3]
        view_screen.ids.transaction_date.text += self.row[4]
        view_screen.ids.amount.text += str(self.row[5])
        view_screen.ids.transaction_type.text += self.row[6]
        view_screen.ids.received_by.text += self.row[7]
        self.screen_manager.current = "view_entry"

    def go_to_add_entry(self):
        self.screen_manager.current = "add_entry"