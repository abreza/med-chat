import os
import uuid
from gradio_filemanager import FileManager
import gradio as gr

mock_files_data = {
    "uuid1": {
        "file_id": "uuid1",
        "name": "report.txt",
        "size": 1024,
        "type": "text",
        "subtype": None,
        "path": "/tmp/report.txt",
        "orig_name": "report.txt",
    },
    "uuid2": {
        "file_id": "uuid2",
        "name": "scan.dcm",
        "size": 204800,
        "type": "medical",
        "subtype": "dicom",
        "path": "/tmp/scan.dcm",
        "orig_name": "scan.dcm",
    },
}


def main():
    with gr.Blocks() as demo:
        gr.Markdown("# FileManager Custom Component Demo")

        with gr.Row():
            with gr.Column(scale=1):
                file_manager = FileManager(
                    label="Managed Files", value=mock_files_data)
                upload_button = gr.UploadButton(
                    "Click to Upload", file_count="multiple")

            with gr.Column(scale=1):
                selected_display = gr.JSON(label="Selected File Event Data")
                deleted_display = gr.Textbox(label="Last Deleted File ID")

        def handle_upload(files, current_files):
            new_files = current_files.copy() if current_files else {}
            for file in files:
                file_id = str(uuid.uuid4())
                ext = os.path.splitext(file.name)[1].lower()
                file_type = "file"
                if ext in ['.txt', '.md', '.csv']:
                    file_type = "text"
                elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
                    file_type = "image"

                new_files[file_id] = {
                    "file_id": file_id,
                    "name": os.path.basename(file.name),
                    "size": os.path.getsize(file.name),
                    "type": file_type,
                    "subtype": None,
                    "path": file.name,
                    "orig_name": os.path.basename(file.name),
                }
            return new_files

        def handle_selection(evt_data: gr.EventData):
            """
            The event payload is a dictionary stored in the `_data` attribute of the EventData object.
            """
            print(f"Selection event: {evt_data._data}")
            # Return the dictionary payload to be displayed in the JSON component.
            return evt_data._data

        def handle_deletion(evt_data: gr.EventData):
            """
            Access the 'file_id' key from the `_data` attribute of the EventData object.
            """
            deleted_id = evt_data._data['file_id']
            print(f"Deleted file with ID: {deleted_id}")
            return deleted_id

        upload_button.upload(
            handle_upload, [upload_button, file_manager], file_manager)

        file_manager.select(handle_selection, None, selected_display)

        file_manager.delete(handle_deletion, None, deleted_display)

    demo.launch()


if __name__ == "__main__":
    main()
