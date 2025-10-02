import os
os.environ['KIVY_NO_CONSOLELOG'] = '1'
from kivy.utils import platform
from kivy.lang.builder import Builder
from kivy.clock import Clock
from threading import Thread
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.tab import MDTabs, MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
#from kivymd.color_definitions import palette
#from kivymd.color_definitions import colors
#from kivymd.uix.chip import MDChip
#import shutil
import sqlite3
from datetime import date
from home import HomeScreen
from add_entry import AddEntryScreen
from view_entry import ViewEntryScreen
from edit_entry import EditEntryScreen
from settings import SettingsScreen
from plyer import filechooser
from xlsxwriter import Workbook
import os
#from io import BytesIO
#import platform
if platform == 'android':
    from android import activity
    from android.permissions import check_permission, request_permissions, Permission
    from jnius import autoclass, JavaException
    # Function to check Android version
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Build_VERSION = autoclass('android.os.Build$VERSION')
    Intent = autoclass('android.content.Intent')
    Context = autoclass('android.content.Context')
    NotificationBuilder = autoclass('android.app.Notification$Builder')
    NotificationManager = autoclass('android.app.NotificationManager')
    Uri = autoclass('android.net.Uri')
    DocumentsContract = autoclass('android.provider.DocumentsContract')
    Settings = autoclass('android.provider.Settings')
    sdk_int = Build_VERSION.SDK_INT

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
        
class FinoraApp(MDApp):

    def build(self):
        self.dialog = None
        self.dialog_box = None
        with open("settings.txt", "a"):
            pass
        with open("account_details.db", "a"):
            pass
        # Set the accent color palette
        # Available palettes: 'Red', 'Pink', 'Purple', 'DeepPurple', 'Indigo', 'Blue',
        # 'LightBlue', 'Cyan', 'Teal', 'Green', 'LightGreen', 'Lime', 'Yellow',
        # 'Amber', 'Orange', 'DeepOrange', 'Brown', 'Gray', 'BlueGray'
        self.screen_manager = MDScreenManager()

        self.screen_manager.add_widget(HomeScreen(name="home"))
        self.screen_manager.add_widget(AddEntryScreen(name="add_entry"))
        self.screen_manager.add_widget(ViewEntryScreen(name="view_entry"))
        self.screen_manager.add_widget(EditEntryScreen(name="edit_entry"))
        self.screen_manager.add_widget(SettingsScreen(name="settings"))
        tabs = MDTabs()

        # Add tabs with explicit icon and/or title
        tabs.add_widget(Tab(title="All Entries"))
        tabs.add_widget(Tab(title="Credit Entries"))
        tabs.add_widget(Tab(title="Debit Entries"))
        
        with open("settings.txt", "r") as file:
            data = file.read()
            if data:
                data_list = data.split("\n")
                self.theme_cls.theme_style = data_list[0]
                #self.theme_cls.primary_palette = data_list[1]

        #self.theme_cls.accent_pallete = 'Teal'
        self.theme_cls.primary_palette = 'Gray'
        self.load_theme()
        self.load_permission()
        # Initialize database
        self.init_db()

        return self.screen_manager
    
    def on_start(self):
        if platform == 'android':
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE, Permission.INTERNET, Permission.POST_NOTIFICATIONS])

        self.screen_manager.get_screen("home").load_entries()
        #self.load_colors()

    def load_permission(self):
        if platform == 'android':
            self.screen_manager.get_screen('settings').ids.notification_switch.active = check_permission(Permission.POST_NOTIFICATIONS)

    def init_db(self):
        self.conn = sqlite3.connect("account_details.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS entries
                               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                person_name VARCHAR(25),
                                branch_name VARCHAR(50),
                                transaction_date DATE,
                                amount DECIMAL(10, 2),
                                transaction_type VARCHAR(10),
                                transaction_method VARCHAR(6),
                                received_by VARCHAR(25))''')
        self.conn.commit()
        self.conn.close()

    def load_theme(self):
        if self.theme_cls.theme_style == "Dark":
            self.screen_manager.get_screen('settings').ids.theme_switch.active = True
            self.screen_manager.get_screen("settings").ids.theme_icon.icon = "lightbulb-off-outline"
            for screen in self.screen_manager.screens:
                if "top_app_bar" in screen.ids:
                    screen.ids.top_app_bar.md_bg_color = (0.13, 0.13, 0.13, 1)
            self.screen_manager.get_screen('home').ids.tabs.tab_bar.md_bg_color = (0.13, 0.13, 0.13, 1)
            self.screen_manager.get_screen('home').ids.add_entry_button.md_bg_color = (0.85, 0.9, 0.95, 0.95)
            self.screen_manager.get_screen('home').ids.add_entry_button.text_color = (0, 0, 0, 1)
        else:
            for screen in self.screen_manager.screens:
                if "top_app_bar" in screen.ids:
                    screen.ids.top_app_bar.md_bg_color = (0.94, 0.94, 0.94, 1)
            self.screen_manager.get_screen('home').ids.tabs.tab_bar.md_bg_color = (0.94, 0.94, 0.94, 1)
    '''def load_colors(self):
        for color in palette:
            hex_color = colors[color]['500']
            if self.theme_cls.primary_palette == color:
                self.screen_manager.get_screen('settings').ids.theme_color_layout.add_widget(
                MDChip(
                    text = color,
                    md_bg_color = colors[color]['50'],
                    elevation = 4,
                    on_release = self.select_theme_color
                )
            )
            else:
                self.screen_manager.get_screen('settings').ids.theme_color_layout.add_widget(
                    MDChip(
                        text = color,
                        md_bg_color = hex_color,
                        on_release = self.select_theme_color
                    )
                )

    def write_data(self, data):
        file_obj = open("settings.txt", "w+")
        file_obj.write(data)
        file_obj.flush()
        file_obj.close()'''

    def change_theme_style(self, active):
        if active:
            self.theme_cls.theme_style = "Dark"
            self.screen_manager.get_screen("settings").ids.theme_icon.icon = "lightbulb-off-outline"
            for screen in self.screen_manager.screens:
                screen.ids.top_app_bar.md_bg_color = (0.13, 0.13, 0.13, 1)
            self.screen_manager.get_screen('home').ids.tabs.tab_bar.md_bg_color = (0.13, 0.13, 0.13, 1)
            self.screen_manager.get_screen("home").ids.tabs.text_color_active = (1, 1, 1, 0.6)
            self.screen_manager.get_screen('home').ids.add_entry_button.md_bg_color = (0.85, 0.9, 0.95, 0.95)
            self.screen_manager.get_screen('home').ids.add_entry_button.text_color = (0, 0, 0, 1)
        else:
            self.theme_cls.theme_style = "Light"
            self.screen_manager.get_screen("settings").ids.theme_icon.icon = "lightbulb-off-outline"
            for screen in self.screen_manager.screens:
                if "top_app_bar" in screen.ids:
                    screen.ids.top_app_bar.md_bg_color = (0.94, 0.94, 0.94, 1)
            self.screen_manager.get_screen('home').ids.tabs.tab_bar.md_bg_color = (0.94, 0.94, 0.94, 1)
            self.screen_manager.get_screen("home").ids.tabs.text_color_active = (0,0,0,0.6)
            self.screen_manager.get_screen('home').ids.add_entry_button.md_bg_color = (0.6, 0.65, 0.8, 0.95)
            self.screen_manager.get_screen('home').ids.add_entry_button.text_color = (1, 1, 1, 1)
            
        with open("settings.txt", "w+") as file_obj:
            file_obj.write(self.theme_cls.theme_style)
            file_obj.close()
        '''data = f"{self.theme_cls.theme_style}\n{self.theme_cls.primary_palette}"
        self.write_data(data)

    def select_theme_color(self, chip):
        for child in self.screen_manager.get_screen("settings").ids.theme_color_layout.children:
            if child.text == chip.text:
                self.theme_cls.primary_palette = chip.text
                child.md_bg_color = colors[child.text]['50']
                child.elevation = 4
                
            else:
                child.md_bg_color = colors[child.text]['500']
                child.elevation = 0
        data = f"{self.theme_cls.theme_style}\n{self.theme_cls.primary_palette}"
        self.write_data(data)'''

    def on_resume(self):
        """Called automatically when app resumes (after settings)"""
        '''if sdk_int >= 33:
            is_granted = check_permission(Permission.POST_NOTIFICATIONS)
        else:
            is_granted = True  # Notifications are always allowed < API 33'''

        # Update switch to reflect actual permission
        settings_screen = self.screen_manager.get_screen('settings')
        settings_screen.ids.notification_switch.active = check_permission(Permission.POST_NOTIFICATIONS)

    def toggle_notifications(self, obj):
        if platform == "android":
            if obj.active:
                # POST_NOTIFICATIONS is required only on API 33+
                #if sdk_int >= 33:
                def callback(permissions, grants):
                    for perm, grant in zip(permissions, grants):
                        if grant:
                            obj.active = True
                        else:
                            obj.active = False

                request_permissions([Permission.POST_NOTIFICATIONS], callback)
            else:
                # Open app settings for this app
                activity = PythonActivity.mActivity
                intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
                uri = autoclass('android.net.Uri').parse(f"package:{activity.getPackageName()}")
                intent.setData(uri)
                activity.startActivity(intent)

    def build_xlsx(self, xlsx_file):
        file_path = os.path.join(os.getcwd(), xlsx_file)
        self.conn = sqlite3.connect("account_details.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT * FROM entries ORDER BY transaction_date DESC")
        rows = self.cursor.fetchall()
        self.conn.close()
        workbook = Workbook(file_path)
        worksheet = workbook.add_worksheet("Account Details")

        headers = ["S.No.", "Person Name", "Branch Name", "Transaction Date", "Amount", "Transaction Type", "Transaction Method", "Received By"]
        head_format = workbook.add_format({'bold':True, 'border':True, 'align':'center', 'valign':'center', 'font': 'Arial', 'font_size':12})
        body_format = workbook.add_format({'border':True, 'align':'left', 'valign':'center', 'font': 'Calibri', 'font_size':10})
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, head_format)
            if header == 'Person Name':
                worksheet.data_validation(
                    1, col_num, len(rows), col_num,
                    {"validate": "length",
                     "criteria": "between",
                     "minimum": 3,
                     "maximum": 25,
                     "input_title": "Person Name",
                     "input_message": "Enter Person Name.",
                     "error_title": "Invalid Name!",
                     "error_message": "The entered name must not contain numbers and must be between 3 and 25 letters.",
                     },
                )
            if header == 'Branch Name':
                worksheet.data_validation(
                    1, col_num, len(rows), col_num,
                    {"validate": "length",
                     "criteria": "between",
                     "minimum": 3,
                     "maximum": 50,
                     "input_title": "Branch Name",
                     "input_message": "Enter Branch Name.",
                     "error_title": "Invalid Name!",
                     "error_message": "The entered name must not contain numbers and must not exceed 50 letters.",
                     },
                )
            if header == 'Transaction Date':
                worksheet.data_validation(
                    1, col_num, len(rows), col_num,
                    {"validate": "date",
                     "criteria": "less than",
                     "value": date.today(),
                     "input_title": "Transaction Date",
                     "input_message": "Enter transaction date.",
                     "error_title": "Invalid Date!",
                     "error_message": f"The entered date must not exceed {date.today().strftime('%Y-%b-%d')}.",
                     },
                )
            if header == 'Amount':
                worksheet.data_validation(
                    1, col_num, len(rows), col_num,
                    {"validate": "decimal",
                     "criteria": "greater than",
                     "value": 0,
                     "input_title": "Amount",
                     "input_message": "Enter Amount.",
                     "error_title": "Invalid Number!",
                     "error_message": "The entered amount must be greater than 0.",
                     },
                )
            if header == 'Transaction Type':
                worksheet.data_validation(
                    1, col_num, len(rows), col_num,
                    {"validate": "list",
                     "source": ['Debit', 'Credit'],
                     "input_title": "Transaction Type",
                     "input_message": "Select transaction type from the given options.",
                     },
                )
            if header == 'Transaction Method':
                worksheet.data_validation(
                    1, col_num, len(rows), col_num,
                    {"validate": "list",
                     "source": ["Cash", "Check", "GPay", "Paytm", "PhonePe"],
                     "input_title": "Transaction Method",
                     "input_message": "Select the way of transaction from the given options.",
                     },
                )
            if header == "Received By":
                worksheet.data_validation(
                    1, col_num, len(rows), col_num,
                    {"validate": "length",
                     "criteria": "between",
                     "minimum": 3,
                     "maximum": 25,
                     "input_title": "Received By",
                     "input_message": "Enter Person Name who received it.",
                     "error_title": "Invalid Name!",
                     "error_message": "The entered name must not contain numbers and must be between 3 and 25 letters.",
                     },
                )

        for row_num, row_data in enumerate(rows, start=1):
            for col_num, cell_data in enumerate(row_data):
                worksheet.write(row_num, col_num, cell_data, body_format)

        worksheet.autofit()
        workbook.close()
        return file_path
    
    def android_notify(self, title, message):
        activity = PythonActivity.mActivity
        notification_service = activity.getSystemService(Context.NOTIFICATION_SERVICE)

        # Notification channel (required for API 26+)
        channel_id = "finora_channel_id"
        channel_name = "Finora Notifications"
        if sdk_int >= 26:
            NotificationChannel = autoclass('android.app.NotificationChannel')
            importance = NotificationManager.IMPORTANCE_DEFAULT
            channel = NotificationChannel(channel_id, channel_name, importance)
            notification_service.createNotificationChannel(channel)
            builder = NotificationBuilder(activity, channel_id)
            builder.setChannelId(channel_id)
        else:
            builder = NotificationBuilder(activity)

        # Small icon — must be a valid drawable
        builder.setSmallIcon(activity.getApplicationInfo().icon)
        builder.setContentTitle(title)
        builder.setContentText(message)
        builder.setAutoCancel(True)

        notification = builder.build()
        notification_service.notify(1, notification)

    def pick_folder(self):
        if not self.screen_manager.get_screen('home').ids.entry_list.children:
            if check_permission(Permission.POST_NOTIFICATIONS):
                self.android_notify(
                    title="Alert",
                    message="NO Data To Export."
                )
            else:
                if not self.dialog:
                    self.dialog = MDDialog(
                        title="Alert",
                        text="NO Data To Export.",
                        buttons=[
                            MDFlatButton(
                                text = "DISMISS",
                                on_release = self.dismiss_dialog
                            )
                        ]
                    )
                self.dialog.open()
            return
        if platform == "android":
            """Open folder picker via SAF"""
            current_activity = PythonActivity.mActivity
            intent = Intent(Intent.ACTION_OPEN_DOCUMENT_TREE)
            current_activity.startActivityForResult(intent, 4001)
        else:
            self.export_data()

    def on_activity_result(self, requestCode, resultCode, data):
        """
        Called from activity.bind(...). Expecting ACTION_OPEN_DOCUMENT_TREE result.
        """
        try:
            if requestCode == 4001 and data:
                folder_uri = data.getData()
                if not folder_uri:
                    print("No folder URI returned")
                    return

                # Debug print - very useful to paste here if issues persist
                print("RAW URI:", folder_uri.toString())
                try:
                    is_tree = DocumentsContract.isTreeUri(folder_uri)
                except JavaException as e:
                    print("DocumentsContract.isTreeUri() raised:", e)
                    is_tree = False
                print("IS TREE:", is_tree)

                # Persist permission
                current_activity = PythonActivity.mActivity
                resolver = current_activity.getContentResolver()
                take_flags = (Intent.FLAG_GRANT_READ_URI_PERMISSION |
                            Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
                try:
                    resolver.takePersistableUriPermission(folder_uri, take_flags)
                except JavaException as e:
                    # Some providers / devices may require different handling; just log
                    print("takePersistableUriPermission failed:", e)

                # Build file on disk (you already create it in build_xlsx)
                xlsx_file = 'data.xlsx'
                file_path = self.build_xlsx(xlsx_file=xlsx_file)
                if not os.path.exists(file_path):
                    print("File not found:", file_path)
                    return

                # Call save function (robust)
                self.save_xlsx_to_folder(folder_uri, xlsx_file, file_path)
        except Exception as e:
            print("on_activity_result general exception:", e)

    def save_xlsx_to_folder(self, folder_uri, filename, file_path):
        """
        Robust SAF write for Android 14:
        - Handles existing files
        - Persists permissions
        - Writes in buffered chunks
        - Notifies user on completion
        """

        current_activity = PythonActivity.mActivity
        resolver = current_activity.getContentResolver()
        take_flags = (Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION)

        try:
            # Persist permission
            resolver.takePersistableUriPermission(folder_uri, take_flags)
        except JavaException as e:
            print("takePersistableUriPermission failed:", e)

        # STEP 1: Get tree doc ID and parent URI
        try:
            tree_doc_id = DocumentsContract.getTreeDocumentId(folder_uri)
            parent_doc_uri = DocumentsContract.buildDocumentUriUsingTree(folder_uri, tree_doc_id)
        except JavaException as e:
            print("Error building parent document URI:", e)
            return

        # STEP 2: Search for existing file
        existing_file_uri = None
        cursor = None
        try:
            children_uri = DocumentsContract.buildChildDocumentsUriUsingTree(folder_uri, tree_doc_id)
            cursor = resolver.query(children_uri, ["display_name", "document_id"], None, None, None)
            if cursor:
                while cursor.moveToNext():
                    name_index = cursor.getColumnIndex("display_name")
                    docid_index = cursor.getColumnIndex("document_id")
                    name = cursor.getString(name_index) if name_index >= 0 else None
                    doc_id = cursor.getString(docid_index) if docid_index >= 0 else None
                    if name == filename:
                        existing_file_uri = DocumentsContract.buildDocumentUriUsingTree(folder_uri, doc_id)
                        print("Found existing file ->", existing_file_uri.toString())
                        break
        except JavaException as e:
            print("Cursor/query error:", e)
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass

        # STEP 3: Create or reuse document URI
        try:
            if existing_file_uri:
                out_uri = existing_file_uri
                print("Overwriting existing file:", out_uri.toString())
            else:
                out_uri = DocumentsContract.createDocument(
                    resolver,
                    parent_doc_uri,  # Must use parent_doc_uri, not raw tree_uri
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    filename
                )
                if out_uri:
                    print("Created new file URI:", out_uri.toString())
                else:
                    print("Failed to create new document")
                    return
        except JavaException as e:
            print("Error creating document:", e)
            return

        # STEP 4: Write the file in buffered chunks
        try:
            out_stream = resolver.openOutputStream(out_uri)
            if not out_stream:
                print("openOutputStream returned None")
                return

            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    out_stream.write(chunk)
            out_stream.close()
            print(f"{filename} exported successfully to {out_uri.toString()}")

            # Notify user
            if check_permission(Permission.POST_NOTIFICATIONS):
                self.android_notify(
                    title="Export Complete",
                    message=f"{filename} has been successfully exported!"
                )
            else:
                if not self.dialog:
                    self.dialog = MDDialog(
                        title="Exported",
                        text=f"Excel File Exported Successfully.",
                        buttons=[MDFlatButton(text="OKAY", on_release=self.dismiss_dialog)]
                    )
                self.dialog.open()
        except JavaException as e:
            print("Java exception while writing file stream:", e)
        except Exception as e:
            print("General exception while writing file:", e)

    def export_data(self):
        if platform == 'windows':
            file_path = filechooser.save_file(title="Save Excel File", filters=[("Excel Files", "*.xlsx")])
            if not file_path:
                return
            file_path = file_path[0] if isinstance(file_path, list) else file_path
            self.build_xlsx(file_path)

        else:
            file_path = f'{os.getcwd()}/data.xlsx'
            self.build_xlsx(file_path)

        if not self.dialog:
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
        if self.dialog_box:
            self.dialog_box.dismiss()
            self.dialog_box = None

    def send_email(self):
        if not self.dialog_box:
            self.dialog_box = MDDialog(
                title = "Mailing Excel File",
                type = "custom",
                radius = [25, 5, 25, 5],
                auto_dismiss = False,
                content_cls = Mail_Content(),
            )
        self.dialog_box.open()

    def update(self, instance):
        if instance.error == True:
            instance.error = False
            #instance.line_color_normal = (0, 0, 0, 1)
            instance.line_color_focus = (0, 0, 0, 1)
            instance.text = ""
            instance.hint_text = "Enter your email adress"

            # Change hint text color → use theme overrides
            #instance.hint_text_color_normal = (0, 0, 0, 1)
            instance.hint_text_color_focus = (0, 0, 0, 1)

            # Change helper text and color
            instance.helper_text = "Example: abc@gmail.com"
            instance.helper_text_mode = "persistent"  # force show
            #instance.helper_text_color_normal = (0, 0, 0, 1)
            instance.helper_text_color_focus = (0, 0, 0, 1)

    def update_text(self, instance, text): 
        self.receiver = text

    def progress(self):
        self.dialog_box.content_cls.ids.spinner.active = True

        # Run email process in a separate thread
        Thread(target=self.email).start()

    def email(self):
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.mime.base import MIMEBase
            from email import encoders

            body = '''Hey, This is a mail sent from TD group to 
            access the requested excel file which is attached in this mail.\n
            Thankyou for contacting us.'''

            sender_address = 'tushar.dewangan6076@gmail.com'
            sender_pass = 'sfjoxrfaqzuacdoj'
            receiver_adress = self.receiver

            message = MIMEMultipart()
            message['From'] = sender_address
            message['To'] = receiver_adress
            message['Subject'] = 'Exported Excel File'
            message.attach(MIMEText(body, 'plain'))

            # building an xlsx file if not exist
            file_path = self.build_xlsx(xlsx_file='data.xlsx')

            attachment = open(file_path, 'rb')
            p = MIMEBase('application', 'octet-stream')
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
            Clock.schedule_once(self.progress_over)

        except smtplib.SMTPRecipientsRefused:
            Clock.schedule_once(self.progress_refused)          

        except:
            Clock.schedule_once(self.progress_internet) 

    def progress_over(self, dt):
        self.dialog_box.content_cls.ids.spinner.active = False
        self.dialog_box.content_cls.clear_widgets()
        self.dialog_box.title = "Excel file Mailed!"
        self.dialog_box.content_cls.add_widget(
            MDLabel(
                text = "Successfully mailed excel file.....",
                pos_hint = {'top': 1},
                halign = 'center',
            )
        )
        self.dialog_box.content_cls.add_widget(
            MDFlatButton(
                    text = "OKAY",
                    theme_text_color = "Custom",
                    pos_hint = {'center_x': 0.9, 'center_y': 0.1},
                    on_release = self.dismiss_dialog,
                ),
        )

    def progress_refused(self, dt):
        self.dialog_box.content_cls.ids.spinner.active = False
        email_field = self.dialog_box.content_cls.ids.email
        email_field.focus = True
        email_field.error = True
        #email_field.line_color_normal = (1, 0, 0, 1)
        email_field.line_color_focus = (1, 0, 0, 1)
        email_field.text = ""
        email_field.hint_text = "Enter Valid Email Address"

        # Change hint text color → use theme overrides
        #email_field.hint_text_color_normal = (1, 0, 0, 1)
        email_field.hint_text_color_focus = (1, 0, 0, 1)

        # Change helper text and color
        email_field.helper_text = "Invalid Email Address..."
        email_field.helper_text_mode = "persistent"  # force show
        #email_field.helper_text_color_normal = (1, 0, 0, 1)
        email_field.helper_text_color_focus = (1, 0, 0, 1)

    def progress_internet(self, dt):
        self.dialog_box.content_cls.ids.spinner.active = False
        self.dialog_box.content_cls.clear_widgets()
        self.dialog_box.title = "Internet Connection Error"
        self.dialog_box.content_cls.add_widget(
            MDLabel(
                text = "Internet connection not found.....",
                pos_hint = {'top': 1},
                halign = 'center',
            )
        )
        self.dialog_box.content_cls.add_widget(
            MDFlatButton(
                    text = "OKAY",
                    theme_text_color = "Custom",
                    pos_hint = {'center_x': 0.9, 'center_y': 0.1},
                    on_release = self.dismiss_dialog,
                ),
        )

if platform == "android":
    def on_activity_result(requestCode, resultCode, intent):
        app = FinoraApp.get_running_app()
        if app:
            app.on_activity_result(requestCode, resultCode, intent)

    activity.bind(on_activity_result=on_activity_result)
            

if __name__ == "__main__":
    FinoraApp().run()
