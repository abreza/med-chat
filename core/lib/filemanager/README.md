---
tags: [gradio-custom-component, SimpleTextbox]
title: gradio_filemanager
short_description: 
colorFrom: blue
colorTo: yellow
sdk: gradio
pinned: false
app_file: space.py
---

# `gradio_filemanager`
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  

Python library for easily interacting with trained machine learning models

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

## `FileManager`

### Initialization

<table>
<thead>
<tr>
<th align="left">name</th>
<th align="left" style="width: 25%;">type</th>
<th align="left">default</th>
<th align="left">description</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left"><code>value</code></td>
<td align="left" style="width: 25%;">

```python
typing.Optional[typing.Dict[str, typing.Any]][
    typing.Dict[str, typing.Any][str, Any], None
]
```

</td>
<td align="left"><code>None</code></td>
<td align="left">A dictionary representing the initial state of the files.</td>
</tr>

<tr>
<td align="left"><code>label</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The component label.</td>
</tr>

<tr>
<td align="left"><code>every</code></td>
<td align="left" style="width: 25%;">

```python
float | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">If `value` is a callable, run the function 'every' number of seconds.</td>
</tr>

<tr>
<td align="left"><code>show_label</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True, shows the component label.</td>
</tr>

<tr>
<td align="left"><code>container</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True, wraps the component in a container.</td>
</tr>

<tr>
<td align="left"><code>scale</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">The relative size of the component.</td>
</tr>

<tr>
<td align="left"><code>min_width</code></td>
<td align="left" style="width: 25%;">

```python
int
```

</td>
<td align="left"><code>160</code></td>
<td align="left">The minimum width of the component.</td>
</tr>

<tr>
<td align="left"><code>visible</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, the component is not visible.</td>
</tr>

<tr>
<td align="left"><code>elem_id</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional string that is assigned as the id of this component in the HTML DOM.</td>
</tr>

<tr>
<td align="left"><code>elem_classes</code></td>
<td align="left" style="width: 25%;">

```python
typing.Union[typing.List[str], str, NoneType][
    typing.List[str][str], str, None
]
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional list of strings that are assigned as the classes of this component in the HTML DOM.</td>
</tr>
</tbody></table>


### Events

| name | description |
|:-----|:------------|
| `change` |  |
| `select` |  |
| `delete` |  |



### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As output:** Is passed, a dictionary representing the files data.
- **As input:** Should return, the dictionary of files data.

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
 
