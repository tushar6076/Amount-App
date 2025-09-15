import os
os.environ['KIVY_NO_CONSOLELOG'] = '1'
from kivy.lang.builder import Builder
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.tab import MDTabs, MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.toast import toast
import shutil
import sqlite3
from home import HomeScreen
from add_entry import AddEntryScreen
from view_entry import ViewEntryScreen
from edit_entry import EditEntryScreen
from settings import SettingsScreen
from plyer import filechooser
from xlsxwriter import Workbook
import os

Builder.load_file("home.kv")
Builder.load_file("add_entry.kv")
Builder.load_file("view_entry.kv")
Builder.load_file("edit_entry.kv")
Builder.load_file("settings.kv")
Builder.load_file("navigation_drawer.kv")

class Mail_Content(MDBoxLayout):
    pass

class Tab(MDTabsBase,MDFloatLayout):
    pass
        
class AccountDetailsApp(MDApp):

    dialog = None
    dialog_2 = None
    dialog_box = None

    def build(self):
        with open("account_details.db", "a"):
            pass

        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        self.screen_manager = MDScreenManager()

        self.screen_manager.add_widget(HomeScreen(name="home"))
        self.screen_manager.add_widget(AddEntryScreen(name="add_entry"))
        self.screen_manager.add_widget(ViewEntryScreen(name="view_entry"))
        self.screen_manager.add_widget(EditEntryScreen(name="edit_entry"))
        self.screen_manager.add_widget(SettingsScreen(name="settings"))
        tabs = MDTabs()

        # Add tabs with explicit icon and/or title
        tabs.add_widget(Tab(title="All Entries", text="all entries content"))
        tabs.add_widget(Tab(title="Credit Entries", text="credit entries content"))
        tabs.add_widget(Tab(title="Debit Entries", text="debit entries content"))
        # Initialize database
        self.init_db()

        return self.screen_manager
    
    def on_start(self):
        '''if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE, Permission.INTERNET])
            '''
        entry_list = self.screen_manager.get_screen('home').ids.all_entry_list
        self.screen_manager.get_screen("home").load_entries(entry_list)

    def init_db(self):
        self.conn = sqlite3.connect("account_details.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS entries
                               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                person_name VARCHAR(50),
                                branch_name VARCHAR(50),
                                day VARCHAR(10),
                                transaction_date DATE,
                                amount DECIMAL(10, 2),
                                transaction_type VARCHAR(10),
                                received_by VARCHAR(50))''')
        self.conn.commit()
        self.conn.close()

    def change_theme_style(self, active):
        if active:
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"

    def select_theme_color(self, chip):
        for child in self.screen_manager.get_screen("settings").ids.theme_color_layout.children:
            
            if child.text == chip.text:
                child.active = True
                self.theme_cls.primary_palette = chip.text
            else:
                child.active = False

    def export_data(self):
        self.conn = sqlite3.connect("account_details.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT * FROM entries ORDER BY transaction_date DESC")
        rows = self.cursor.fetchall()
        self.conn.close()

        if not rows:
            self.dialog_2 = MDDialog(
                title="Alert",
                text=f"NO Data To Export.",
                buttons=[
                    MDFlatButton(
                        text = "DISMISS",
                        on_release = self.dismiss_dialog
                    )
                ]
            )
            self.dialog_2.open()
            return
        if platform == "android":
            try:
                xlsx_file = "data.xlsx"
                from android.storage import primary_external_storage_path
                os.mkdir(f"{primary_external_storage_path()}/Documents")
                path = f"{primary_external_storage_path()}/Documents/{xlsx_file}"
                shutil.copy(f"{os.getcwd()}/{xlsx_file}", path)
            except:
                toast(f"Delete the existing {xlsx_file} file to export new file.")

        else:
            file_path = filechooser.save_file(title="Save Excel File", filters=[("Excel Files", "*.xlsx")])
            if not file_path:
                return
            file_path = file_path[0] if isinstance(file_path, list) else file_path

            workbook = Workbook(file_path)
            worksheet = workbook.add_worksheet()

            headers = ["S.No.", "Person Name", "Branch Name", "Day", "Transaction Date", "Amount", "Transaction Type", "Received By"]
            for col_num, header in enumerate(headers):
                worksheet.write(0, col_num, header)

            for row_num, row_data in enumerate(rows, start=1):
                for col_num, cell_data in enumerate(row_data):
                    worksheet.write(row_num, col_num, cell_data)

            workbook.close()
            self.dialog = MDDialog(
                title="Data Exported",
                text=f"Data exported to {file_path}",
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
        if self.dialog_2:
            self.dialog_2.dismiss()
        if self.dialog_box:
            self.dialog_box.dismiss()

    def send_email(self):
        if not self.dialog_box:
            self.dialog_box = MDDialog(
                title = "Mailing Excel File",
                type = "custom",
                radius = [25, 5, 25, 5],
                auto_dismiss = False,
                content_cls = Mail_Content(),
                buttons = [
                    MDFlatButton(
                        text = "CANCEL",
                        theme_text_color = "Custom",
                        on_release = self.dismiss_dialog,
                    ),
                    MDFlatButton(
                        text = "Email",
                        theme_text_color = "Custom",
                        on_release = self.email,
                    )
                ]
            )
        self.dialog_box.open()

    def update_text(self, instance, text):
        self.receiver = text

    def email(self, instance):
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.mime.base import MIMEBase
            from email import encoders

            body = '''Hey, This is a mail sent from TD group to 
            access the requested excel file which is attached in this mail.\n
            Thankyou for contacting us.'''

            sender_address = 'tushardewangan7759@gmail.com'
            sender_pass = 'djjntifkeancgyjb'
            receiver_adress = self.receiver

            message = MIMEMultipart()
            message['From'] = sender_address
            message['To'] = receiver_adress
            message['Subject'] = 'Exported Excel File'
            message.attach(MIMEText(body, 'plain'))

            attachment = open(os.path.join(os.getcwd(), 'data.xlsx'), 'rb')
            p = MIMEBase('applicatiion', 'octet-stream')
            p.set_payload((attachment).read())
            encoders.encode_base64(p)
            p.add_header("Content-Disposition", "attachment", filename='data.xlsx')
            message.attach(p)

            session = smtplib.SMTP('smtp.gmail.com', 587)
            session.starttls()
            session.login(sender_address, sender_pass)

            text = message.as_string()
            session.sendmail(sender_address, receiver_adress, text)
            session.quit()
            self.dialog_box.clear_widets()
            self.dialog_box.add_widget(
                MDLabel(
                    text = "Successfully Send! Check out your mail box.",
                    halign = "center",
                    pos_hint = {"center_x": 0.5, "center_y": 0.7},
                    theme_text_color = "Secondary",
                ),
                MDRaisedButton(
                    text = "Okay",
                    hilign = "center",
                    pos_hint = {"center_x": 0.5, "center_y": 0.25},
                    on_release = self.dismiss_dialog,
                ),
            )


        except smtplib.SMTPRecipientsRefused:
            self.ids.email.text=""

        '''except:
            MDSnackbar(
                MDLabel(
                    text="Internet connection not found!",
                    halign="center",
                )
            ).open()'''

if __name__ == "__main__":
    AccountDetailsApp().run()