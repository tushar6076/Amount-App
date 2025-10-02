from kivy.lang.builder import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import  MDFlatButton
import sqlite3

Builder.load_string(
'''
<DeleteContent>
    orientation: "vertical"
    spacing: "10dp"
    size_hint_y: None
    height: dp(90)
    MDLabel:
        text: "Are you sure, you want to delete this entry?"
        halign: "center"
    MDBoxLayout:
        pos_hint: {'center_x': 0.8, 'center_y': 0.1}
        spacing: dp(10)
        MDFlatButton:
            text: "CANCEL"
            theme_text_color: "Custom"
            on_release: app.root.get_screen('view_entry').dismiss_dialog(self)
        MDRaisedButton:
            text: "DELETE"
            md_bg_color: 1, 0, 0, 1
            theme_text_color: "Custom"
            on_release:
                app.root.get_screen('view_entry').delete_entry(self)'''
)

class DeleteContent(MDBoxLayout):
    pass

class ViewEntryScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = MDApp.get_running_app()
        self.screen_manager = app.screen_manager
        self.delete_dialog = None

    def home_button(self, instance):
        self.ids.top_app_bar.title = ""
        self.screen_manager.current = "home"

    def edit_entry_button(self):
        self.row = self.screen_manager.get_screen("home").row
        edit_screen = self.screen_manager.get_screen("edit_entry")
        edit_screen.ids.top_app_bar.title = f"Entry Number : {str(self.row[0])}"
        edit_screen.ids.person_name.text = self.row[1]
        edit_screen.ids.branch_name.text = self.row[2]
        edit_screen.ids.transaction_date.text = self.row[3]
        edit_screen.ids.amount.text = str(self.row[4])
        edit_screen.ids.transaction_type.text = self.row[5]
        edit_screen.ids.transaction_method.text = self.row[6]
        edit_screen.ids.received_by.text = self.row[7]
        self.screen_manager.current = "edit_entry"

    def delete_option(self):
        if not self.delete_dialog:
            self.delete_dialog = MDDialog(
                title="DELETE ENTRY",
                type = "custom",
                radius = [25, 5, 25, 5],
                auto_dismiss = False,
                content_cls = DeleteContent(),
            )
        self.delete_dialog.open()

    def delete_entry(self, instance):
        self.row = self.screen_manager.get_screen("home").row
        self.conn = sqlite3.connect("account_details.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("DELETE FROM entries WHERE id = ?", (self.row[0],))
        self.conn.commit()
        self.conn.close()
        home_screen = self.screen_manager.get_screen("home")
        tab_bar = home_screen.ids.tabs.get_current_tab().title
        if tab_bar == "All Entries":
            home_screen.load_entries()
        elif tab_bar == "Credit Entries":
            home_screen.load_credit_entries()
        elif tab_bar == "Debit Entries":
            home_screen.load_debit_entries()
        self.ids.top_app_bar.title = ""
        self.screen_manager.current = "home"
        self.delete_dialog.content_cls.clear_widgets()
        self.delete_dialog.title = "Entry Delted"
        self.delete_dialog.content_cls.add_widget(
            MDLabel(
                text = "Entry deleted successfully.....",
                pos_hint = {'top': 1},
                halign = 'center',
            )
        )
        self.delete_dialog.content_cls.add_widget(
            MDFlatButton(
                    text = "OKAY",
                    theme_text_color = "Custom",
                    pos_hint = {'center_x': 0.9, 'center_y': 0.1},
                    on_release = self.dismiss_dialog,
                ),
        )

    def dismiss_dialog(self, instance):
        if self.delete_dialog:
            self.delete_dialog.dismiss()
            self.delete_dialog = None