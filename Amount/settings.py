from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

class SettingsScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = MDApp.get_running_app()
        self.screen_manager = app.screen_manager
        self.info_dialog = None

    def home_button(self, instance):
        self.screen_manager.current = "home"

    def info(self):
        if not self.info_dialog:
            self.info_dialog = MDDialog(
                #type = "alert", default option
                title = "Info",
                text = '''This app helps you securely manage your account details, including personal info, credentials, and records. Easily add, edit, search, and organize data, with options to export or back up for safe storage.''',
                buttons = [
                    MDFlatButton(
                        text = "DISMISS",
                        on_release = lambda x: self.info_dialog.dismiss()
                    ),
                ]
            )
        self.info_dialog.open()