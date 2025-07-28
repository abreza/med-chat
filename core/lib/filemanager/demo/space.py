
import gradio as gr
from app import demo as app
import os

_docs = {'FileManager': {'description': 'A custom component to manage and display a list of uploaded files with selection and deletion capabilities.', 'members': {'__init__': {'value': {'type': 'typing.Optional[typing.Dict[str, typing.Any]][\n    typing.Dict[str, typing.Any][str, Any], None\n]', 'default': 'None', 'description': 'A dictionary representing the initial state of the files.'}, 'label': {'type': 'str | None', 'default': 'None', 'description': 'The component label.'}, 'every': {'type': 'float | None', 'default': 'None', 'description': "If `value` is a callable, run the function 'every' number of seconds."}, 'show_label': {'type': 'bool', 'default': 'True', 'description': 'If True, shows the component label.'}, 'container': {'type': 'bool', 'default': 'True', 'description': 'If True, wraps the component in a container.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'The relative size of the component.'}, 'min_width': {'type': 'int', 'default': '160', 'description': 'The minimum width of the component.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, the component is not visible.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the HTML DOM.'}, 'elem_classes': {'type': 'typing.Union[typing.List[str], str, NoneType][\n    typing.List[str][str], str, None\n]', 'default': 'None', 'description': 'An optional list of strings that are assigned as the classes of this component in the HTML DOM.'}}, 'postprocess': {'value': {'type': 'typing.Optional[typing.Dict[str, typing.Any]][\n    typing.Dict[str, typing.Any][str, Any], None\n]', 'description': 'The dictionary of files data.'}}, 'preprocess': {'return': {'type': 'typing.Optional[typing.Dict[str, typing.Any]][\n    typing.Dict[str, typing.Any][str, Any], None\n]', 'description': 'A dictionary representing the files data.'}, 'value': None}}, 'events': {'change': {'type': None, 'default': None, 'description': ''}, 'select': {'type': None, 'default': None, 'description': ''}, 'delete': {'type': None, 'default': None, 'description': ''}}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'FileManager': []}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_filemanager`

<div style="display: flex; gap: 7px;">
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  
</div>

Python library for easily interacting with trained machine learning models
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_filemanager
```

## Usage

```python
import gradio as gr
from gradio_filemanager import FileManager

# Mock file data for the demo
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
    "uuid3": {
        "file_id": "uuid3",
        "name": "brain.nii",
        "size": 512000,
        "type": "medical",
        "subtype": "nifti",
        "path": "/tmp/brain.nii",
        "orig_name": "brain.nii",
    },
    "uuid4": {
        "file_id": "uuid4",
        "name": "xray.jpg",
        "size": 150000,
        "type": "image",
        "subtype": None,
        "path": "/tmp/xray.jpg",
        "orig_name": "xray.jpg",
    }
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
                selected_display = gr.JSON(label="Selected Files")
                deleted_display = gr.Textbox(label="Last Deleted File ID")

        def handle_upload(files, current_files):
            new_files = current_files.copy() if current_files else {}
            for file in files:
                file_id = str(hash(file.name))
                new_files[file_id] = {
                    "file_id": file_id,
                    "name": file.name,
                    "size": len(open(file.name, 'rb').read()),
                    "type": "file",
                    "subtype": None,
                    "path": file.name,
                    "orig_name": file.name,
                }
            return new_files

        def handle_selection(evt: gr.SelectData):
            # This is a placeholder for actual selection logic handling
            # The component's internal state handles the visual selection
            # This event can be used to trigger other actions in the app
            print(f"Selection event: {evt.value}")
            # To demonstrate, we could update a state or another component
            # In this simple demo, we just print
            pass

        def handle_deletion(evt: gr.SelectData):
            # This event is triggered from the frontend when a file is deleted
            # The component's value is updated automatically on the frontend
            # This backend handler is for any additional logic needed
            deleted_id = evt.value['file_id']
            print(f"Deleted file with ID: {deleted_id}")
            return deleted_id

        upload_button.upload(
            handle_upload, [upload_button, file_manager], file_manager)
        file_manager.select(handle_selection, None, None)
        file_manager.delete(handle_deletion, file_manager, deleted_display)

    demo.launch()


if __name__ == "__main__":
    main()

```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `FileManager`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["FileManager"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["FileManager"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As input:** Is passed, a dictionary representing the files data.
- **As output:** Should return, the dictionary of files data.

 ```python
def predict(
    value: typing.Optional[typing.Dict[str, typing.Any]][
    typing.Dict[str, typing.Any][str, Any], None
]
) -> typing.Optional[typing.Dict[str, typing.Any]][
    typing.Dict[str, typing.Any][str, Any], None
]:
    return value
```
""", elem_classes=["md-custom", "FileManager-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          FileManager: [], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
