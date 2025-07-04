
# `gradio_medchatinput`
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  

Python library for easily interacting with trained machine learning models

## Installation

```bash
pip install gradio_medchatinput
```

## Usage

```python
import gradio as gr
from gradio_medchatinput import MedChatInput

def process_input(user_input):
    if user_input is None:
        return "No input received."
    
    text = user_input.get("text", "")
    files = user_input.get("files", [])
    
    response_parts = []
    
    if text:
        response_parts.append(f"Text received: {text}")
    
    if files:
        response_parts.append(f"Files received: {len(files)} file(s)")
        for i, file_path in enumerate(files):
            response_parts.append(f"  File {i+1}: {file_path}")
    
    if not text and not files:
        response_parts.append("No text or files received.")
    
    return "\n".join(response_parts)


js = """
function() {
    console.log("Setting up immediate transcription...");
    
    // Set up global transcription function
    window.transcribeAudioImmediate = function(base64Audio) {
        return new Promise((resolve) => {
            // Find the hidden input and output elements
            const triggerEl = document.getElementById('transcription_trigger').querySelector('textarea, input');
            const resultEl = document.getElementById('transcription_result').querySelector('textarea, input');
            
            if (!triggerEl || !resultEl) {
                console.error('Could not find transcription elements');
                resolve('');
                return;
            }
            
            // Set up listener for result
            const originalValue = resultEl.value;
            let checkCount = 0;
            const maxChecks = 500; // 50 seconds timeout
            
            const checkForResult = () => {
                checkCount++;
                if (resultEl.value !== originalValue && resultEl.value !== '') {
                    const result = resultEl.value;
                    resolve(result);
                } else if (checkCount < maxChecks) {
                    setTimeout(checkForResult, 100);
                } else {
                    console.warn('Transcription timeout');
                    resolve('');
                }
            };
            
            // Trigger transcription
            triggerEl.value = base64Audio;
            triggerEl.dispatchEvent(new Event('input', { bubbles: true }));
            
            // Start checking for result
            setTimeout(checkForResult, 100);
        });
    };
    
    console.log("Immediate transcription setup complete");
}
"""

if __name__ == "__main__":
    with gr.Blocks(title="Medical Chat with Voice Input", js=js) as demo:
        chatbot = gr.Chatbot(label="Conversation")
        
        user_input = MedChatInput(
            label="Your message",
            placeholder="Type your message or record audio...",
            sources=["upload", "microphone"],
            auto_transcribe=True,
            transcription_language="fa",
            keep_audio_after_transcribe=False,
            file_types=["image", "audio", "text"],
            max_plain_text_length=2000,
            submit_btn="Send",
            stop_btn=False
        )
        
        transcription_trigger = gr.Textbox(visible=False, elem_id="transcription_trigger")
        transcription_result = gr.Textbox(visible=False, elem_id="transcription_result")
        
        def respond(message, history):
            if message is None:
                return history, {"text": "", "files": []}
            
            response = process_input(message)
            
            user_msg = message.get("text", "")
            if message.get("files"):
                user_msg += f" [+{len(message['files'])} file(s)]"
            
            history.append([user_msg, response])
            
            return history, {"text": "", "files": []}
        
        transcription_trigger.change(
            fn=MedChatInput.transcribe,
            inputs=[transcription_trigger],
            outputs=[transcription_result],
            show_progress=False
        )
        
        user_input.submit(
            respond,
            [user_input, chatbot],
            [chatbot, user_input]
        )
    
    demo.load()
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )

```

## `MedChatInput`

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
str | dict[str, str | list] | Callable | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Default value to show in MedChatInput. A string value, or a dictionary of the form {"text": "sample text", "files": [{path: "files/file.jpg", orig_name: "file.jpg", url: "http://image_url.jpg", size: 100}]}. If a function is provided, the function will be called each time the app loads to set the initial value of this component.</td>
</tr>

<tr>
<td align="left"><code>sources</code></td>
<td align="left" style="width: 25%;">

```python
list[Literal["upload", "microphone"]]
    | Literal["upload", "microphone"]
    | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">A list of sources permitted. "upload" creates a button where users can click to upload or drop files, "microphone" creates a microphone input. If None, defaults to ["upload"].</td>
</tr>

<tr>
<td align="left"><code>file_types</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">List of file extensions or types of files to be uploaded (e.g. ['image', '.json', '.mp4']). "file" allows any file to be uploaded, "image" allows only image files to be uploaded, "audio" allows only audio files to be uploaded, "video" allows only video files to be uploaded, "text" allows only text files to be uploaded.</td>
</tr>

<tr>
<td align="left"><code>file_count</code></td>
<td align="left" style="width: 25%;">

```python
Literal["single", "multiple", "directory"]
```

</td>
<td align="left"><code>"multiple"</code></td>
<td align="left">if single, allows user to upload one file. If "multiple", user uploads multiple files. If "directory", user uploads all files in selected directory. Return type will be list for each file in case of "multiple" or "directory".</td>
</tr>

<tr>
<td align="left"><code>lines</code></td>
<td align="left" style="width: 25%;">

```python
int
```

</td>
<td align="left"><code>1</code></td>
<td align="left">minimum number of line rows to provide in textarea.</td>
</tr>

<tr>
<td align="left"><code>max_lines</code></td>
<td align="left" style="width: 25%;">

```python
int
```

</td>
<td align="left"><code>20</code></td>
<td align="left">maximum number of line rows to provide in textarea.</td>
</tr>

<tr>
<td align="left"><code>placeholder</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">placeholder hint to provide behind textarea.</td>
</tr>

<tr>
<td align="left"><code>label</code></td>
<td align="left" style="width: 25%;">

```python
str | I18nData | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.</td>
</tr>

<tr>
<td align="left"><code>info</code></td>
<td align="left" style="width: 25%;">

```python
str | I18nData | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">additional component description, appears below the label in smaller font. Supports markdown / HTML syntax.</td>
</tr>

<tr>
<td align="left"><code>every</code></td>
<td align="left" style="width: 25%;">

```python
Timer | float | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.</td>
</tr>

<tr>
<td align="left"><code>inputs</code></td>
<td align="left" style="width: 25%;">

```python
Component | Sequence[Component] | set[Component] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.</td>
</tr>

<tr>
<td align="left"><code>show_label</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">if True, will display label.</td>
</tr>

<tr>
<td align="left"><code>container</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True, will place the component in a container - providing some extra padding around the border.</td>
</tr>

<tr>
<td align="left"><code>scale</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.</td>
</tr>

<tr>
<td align="left"><code>min_width</code></td>
<td align="left" style="width: 25%;">

```python
int
```

</td>
<td align="left"><code>160</code></td>
<td align="left">minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.</td>
</tr>

<tr>
<td align="left"><code>interactive</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">if True, will be rendered as an editable textbox; if False, editing will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.</td>
</tr>

<tr>
<td align="left"><code>visible</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, component will be hidden.</td>
</tr>

<tr>
<td align="left"><code>elem_id</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>autofocus</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True, will focus on the textbox when the page loads. Use this carefully, as it can cause usability issues for sighted and non-sighted users.</td>
</tr>

<tr>
<td align="left"><code>autoscroll</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True, will automatically scroll to the bottom of the textbox when the value changes, unless the user scrolls up. If False, will not scroll to the bottom of the textbox when the value changes.</td>
</tr>

<tr>
<td align="left"><code>elem_classes</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>render</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.</td>
</tr>

<tr>
<td align="left"><code>key</code></td>
<td align="left" style="width: 25%;">

```python
int | str | tuple[int | str, ...] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.</td>
</tr>

<tr>
<td align="left"><code>preserved_by_key</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>"value"</code></td>
<td align="left">A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.</td>
</tr>

<tr>
<td align="left"><code>text_align</code></td>
<td align="left" style="width: 25%;">

```python
Literal["left", "right"] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">How to align the text in the textbox, can be: "left", "right", or None (default). If None, the alignment is left if `rtl` is False, or right if `rtl` is True. Can only be changed if `type` is "text".</td>
</tr>

<tr>
<td align="left"><code>rtl</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True and `type` is "text", sets the direction of the text to right-to-left (cursor appears on the left of the text). Default is False, which renders cursor on the right.</td>
</tr>

<tr>
<td align="left"><code>submit_btn</code></td>
<td align="left" style="width: 25%;">

```python
str | bool | None
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, will not show a submit button. If a string, will use that string as the submit button text.</td>
</tr>

<tr>
<td align="left"><code>stop_btn</code></td>
<td align="left" style="width: 25%;">

```python
str | bool | None
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True, will show a stop button (useful for streaming demos). If a string, will use that string as the stop button text.</td>
</tr>

<tr>
<td align="left"><code>max_plain_text_length</code></td>
<td align="left" style="width: 25%;">

```python
int
```

</td>
<td align="left"><code>1000</code></td>
<td align="left">Maximum length of plain text in the textbox. If the text exceeds this length, the text will be pasted as a file. Default is 1000.</td>
</tr>

<tr>
<td align="left"><code>auto_transcribe</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True, automatically transcribe audio recordings to text using Dolphin ASR. Default is True.</td>
</tr>

<tr>
<td align="left"><code>transcription_language</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Language code for transcription (e.g., 'en', 'fa'). If None, auto-detection is used.</td>
</tr>

<tr>
<td align="left"><code>transcription_region</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Region code for transcription (e.g., 'US', 'UK'). If None, no region is specified.</td>
</tr>

<tr>
<td align="left"><code>keep_audio_after_transcribe</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True, keeps the audio file in the files list after transcription. Default is False.</td>
</tr>
</tbody></table>


### Events

| name | description |
|:-----|:------------|
| `change` | Triggered when the value of the MedChatInput changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input. |
| `input` | This listener is triggered when the user changes the value of the MedChatInput. |
| `select` | Event listener for when the user selects or deselects the MedChatInput. Uses event data gradio.SelectData to carry `value` referring to the label of the MedChatInput, and `selected` to refer to state of the MedChatInput. See EventData documentation on how to use this event data |
| `submit` | This listener is triggered when the user presses the Enter key while the MedChatInput is focused. |
| `focus` | This listener is triggered when the MedChatInput is focused. |
| `blur` | This listener is triggered when the MedChatInput is unfocused/blurred. |
| `stop` | This listener is triggered when the user reaches the end of the media playing in the MedChatInput. |



### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As output:** Is passed, the preprocessed input data sent to the user's function in the backend.
- **As input:** Should return, the output data received by the component from the user's function in the backend.

 ```python
 def predict(
     value: MultimodalValue | None
 ) -> MultimodalValue | str | None:
     return value
 ```
 

## `MultimodalValue`
```python
class MultimodalValue(TypedDict):
    text: NotRequired[str]
    files: NotRequired[list[str]]
```
