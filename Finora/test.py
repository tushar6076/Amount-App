from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from io import BytesIO

from jnius import autoclass, cast

# Android classes
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Intent = autoclass('android.content.Intent')
Uri = autoclass('android.net.Uri')
DocumentsContract = autoclass('android.provider.DocumentsContract')

# Excel library
import xlsxwriter

class ExportXlsxWriterApp(App):
    FILE_NAME = "test_export.xlsx"

    def build(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        btn_folder = Button(text="Pick Folder to Export XLSX")
        btn_folder.bind(on_release=self.pick_folder)
        layout.add_widget(btn_folder)

        return layout

    def pick_folder(self, instance):
        """Open folder picker via SAF"""
        current_activity = PythonActivity.mActivity
        intent = Intent(Intent.ACTION_OPEN_DOCUMENT_TREE)
        current_activity.startActivityForResult(intent, 4001)

    def on_activity_result(self, requestCode, resultCode, data):
        if requestCode == 4001 and data:
            folder_uri = data.getData()
            print("Selected folder URI:", folder_uri.toString())

            # Persist permission
            current_activity = PythonActivity.mActivity
            current_activity.getContentResolver().takePersistableUriPermission(
                folder_uri,
                Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION
            )

            # Create XLSX in memory using xlsxwriter
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet("Sheet1")

            # Sample data
            data = [
                ["Name", "Age", "City"],
                ["Alice", 25, "New York"],
                ["Bob", 30, "London"],
            ]
            for row_idx, row in enumerate(data):
                for col_idx, value in enumerate(row):
                    worksheet.write(row_idx, col_idx, value)

            workbook.close()
            output.seek(0)

            # Save the XLSX file to selected folder
            self.save_xlsx_to_folder(folder_uri, self.FILE_NAME, output.read())

    def save_xlsx_to_folder(self, folder_uri, filename, file_bytes):
        """Save XLSX to SAF folder, overwrite if exists"""
        current_activity = PythonActivity.mActivity
        resolver = current_activity.getContentResolver()

        # Check if file already exists
        children_uri = DocumentsContract.buildChildDocumentsUriUsingTree(
            folder_uri, DocumentsContract.getTreeDocumentId(folder_uri)
        )
        cursor = resolver.query(children_uri, None, None, None, None)

        existing_file_uri = None
        if cursor:
            while cursor.moveToNext():
                display_name_index = cursor.getColumnIndex("display_name")
                if display_name_index >= 0:
                    name = cursor.getString(display_name_index)
                    if name == filename:
                        doc_id_index = cursor.getColumnIndex("document_id")
                        doc_id = cursor.getString(doc_id_index)
                        existing_file_uri = DocumentsContract.buildDocumentUriUsingTree(
                            folder_uri, doc_id
                        )
                        break
            cursor.close()

        if existing_file_uri:
            print("File exists. Overwriting:", filename)
            out_stream = resolver.openOutputStream(existing_file_uri)
        else:
            print("Creating new file:", filename)
            new_file_uri = DocumentsContract.createDocument(
                resolver,
                folder_uri,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename
            )
            out_stream = resolver.openOutputStream(new_file_uri)

        out_stream.write(file_bytes)
        out_stream.close()
        print(f"Excel file saved successfully: {filename}")


# Hook Android activity result
from android import activity
def on_activity_result(requestCode, resultCode, intent):
    app = ExportXlsxWriterApp.get_running_app()
    if app:
        app.on_activity_result(requestCode, resultCode, intent)

activity.bind(on_activity_result=on_activity_result)

if __name__ == "__main__":
    ExportXlsxWriterApp().run()
