
import gradio as gr
from app import demo as app
import os

_docs = {'MedChatInput': {'description': 'Creates a textarea for users to enter string input or display string output and also allows for the uploading of multimedia files.\nIncludes automatic speech-to-text transcription using Dolphin ASR.\n', 'members': {'__init__': {'value': {'type': 'str | dict[str, str | list] | Callable | None', 'default': 'None', 'description': 'Default value to show in MedChatInput. A string value, or a dictionary of the form {"text": "sample text", "files": [{path: "files/file.jpg", orig_name: "file.jpg", url: "http://image_url.jpg", size: 100}]}. If a function is provided, the function will be called each time the app loads to set the initial value of this component.'}, 'sources': {'type': 'list[Literal["upload", "microphone"]]\n    | Literal["upload", "microphone"]\n    | None', 'default': 'None', 'description': 'A list of sources permitted. "upload" creates a button where users can click to upload or drop files, "microphone" creates a microphone input. If None, defaults to ["upload"].'}, 'file_types': {'type': 'list[str] | None', 'default': 'None', 'description': 'List of file extensions or types of files to be uploaded (e.g. [\'image\', \'.json\', \'.mp4\']). "file" allows any file to be uploaded, "image" allows only image files to be uploaded, "audio" allows only audio files to be uploaded, "video" allows only video files to be uploaded, "text" allows only text files to be uploaded.'}, 'file_count': {'type': 'Literal["single", "multiple", "directory"]', 'default': '"multiple"', 'description': 'if single, allows user to upload one file. If "multiple", user uploads multiple files. If "directory", user uploads all files in selected directory. Return type will be list for each file in case of "multiple" or "directory".'}, 'lines': {'type': 'int', 'default': '1', 'description': 'minimum number of line rows to provide in textarea.'}, 'max_lines': {'type': 'int', 'default': '20', 'description': 'maximum number of line rows to provide in textarea.'}, 'placeholder': {'type': 'str | None', 'default': 'None', 'description': 'placeholder hint to provide behind textarea.'}, 'label': {'type': 'str | I18nData | None', 'default': 'None', 'description': 'the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.'}, 'info': {'type': 'str | I18nData | None', 'default': 'None', 'description': 'additional component description, appears below the label in smaller font. Supports markdown / HTML syntax.'}, 'every': {'type': 'Timer | float | None', 'default': 'None', 'description': 'Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.'}, 'inputs': {'type': 'Component | Sequence[Component] | set[Component] | None', 'default': 'None', 'description': 'Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.'}, 'show_label': {'type': 'bool | None', 'default': 'None', 'description': 'if True, will display label.'}, 'container': {'type': 'bool', 'default': 'True', 'description': 'If True, will place the component in a container - providing some extra padding around the border.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.'}, 'min_width': {'type': 'int', 'default': '160', 'description': 'minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.'}, 'interactive': {'type': 'bool | None', 'default': 'None', 'description': 'if True, will be rendered as an editable textbox; if False, editing will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, component will be hidden.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'autofocus': {'type': 'bool', 'default': 'False', 'description': 'If True, will focus on the textbox when the page loads. Use this carefully, as it can cause usability issues for sighted and non-sighted users.'}, 'autoscroll': {'type': 'bool', 'default': 'True', 'description': 'If True, will automatically scroll to the bottom of the textbox when the value changes, unless the user scrolls up. If False, will not scroll to the bottom of the textbox when the value changes.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.'}, 'key': {'type': 'int | str | tuple[int | str, ...] | None', 'default': 'None', 'description': "in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render."}, 'preserved_by_key': {'type': 'list[str] | str | None', 'default': '"value"', 'description': "A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor."}, 'text_align': {'type': 'Literal["left", "right"] | None', 'default': 'None', 'description': 'How to align the text in the textbox, can be: "left", "right", or None (default). If None, the alignment is left if `rtl` is False, or right if `rtl` is True. Can only be changed if `type` is "text".'}, 'rtl': {'type': 'bool', 'default': 'False', 'description': 'If True and `type` is "text", sets the direction of the text to right-to-left (cursor appears on the left of the text). Default is False, which renders cursor on the right.'}, 'submit_btn': {'type': 'str | bool | None', 'default': 'True', 'description': 'If False, will not show a submit button. If a string, will use that string as the submit button text.'}, 'stop_btn': {'type': 'str | bool | None', 'default': 'False', 'description': 'If True, will show a stop button (useful for streaming demos). If a string, will use that string as the stop button text.'}, 'max_plain_text_length': {'type': 'int', 'default': '1000', 'description': 'Maximum length of plain text in the textbox. If the text exceeds this length, the text will be pasted as a file. Default is 1000.'}, 'auto_transcribe': {'type': 'bool', 'default': 'True', 'description': 'If True, automatically transcribe audio recordings to text using Dolphin ASR. Default is True.'}, 'transcription_language': {'type': 'str | None', 'default': 'None', 'description': "Language code for transcription (e.g., 'en', 'fa'). If None, auto-detection is used."}, 'transcription_region': {'type': 'str | None', 'default': 'None', 'description': "Region code for transcription (e.g., 'US', 'UK'). If None, no region is specified."}, 'keep_audio_after_transcribe': {'type': 'bool', 'default': 'False', 'description': 'If True, keeps the audio file in the files list after transcription. Default is False.'}}, 'postprocess': {'value': {'type': 'MultimodalValue | str | None', 'description': "The output data received by the component from the user's function in the backend."}}, 'preprocess': {'return': {'type': 'MultimodalValue | None', 'description': "The preprocessed input data sent to the user's function in the backend."}, 'value': None}}, 'events': {'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the MedChatInput changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'input': {'type': None, 'default': None, 'description': 'This listener is triggered when the user changes the value of the MedChatInput.'}, 'select': {'type': None, 'default': None, 'description': 'Event listener for when the user selects or deselects the MedChatInput. Uses event data gradio.SelectData to carry `value` referring to the label of the MedChatInput, and `selected` to refer to state of the MedChatInput. See EventData documentation on how to use this event data'}, 'submit': {'type': None, 'default': None, 'description': 'This listener is triggered when the user presses the Enter key while the MedChatInput is focused.'}, 'focus': {'type': None, 'default': None, 'description': 'This listener is triggered when the MedChatInput is focused.'}, 'blur': {'type': None, 'default': None, 'description': 'This listener is triggered when the MedChatInput is unfocused/blurred.'}, 'stop': {'type': None, 'default': None, 'description': 'This listener is triggered when the user reaches the end of the media playing in the MedChatInput.'}}}, '__meta__': {'additional_interfaces': {'MultimodalValue': {'source': 'class MultimodalValue(TypedDict):\n    text: NotRequired[str]\n    files: NotRequired[list[str]]'}}, 'user_fn_refs': {'MedChatInput': ['MultimodalValue']}}}

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
# `gradio_medchatinput`

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


js = \"\"\"
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
\"\"\"

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
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `MedChatInput`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["MedChatInput"]["members"]["__init__"], linkify=['MultimodalValue'])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["MedChatInput"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As input:** Is passed, the preprocessed input data sent to the user's function in the backend.
- **As output:** Should return, the output data received by the component from the user's function in the backend.

 ```python
def predict(
    value: MultimodalValue | None
) -> MultimodalValue | str | None:
    return value
```
""", elem_classes=["md-custom", "MedChatInput-user-fn"], header_links=True)




    code_MultimodalValue = gr.Markdown("""
## `MultimodalValue`
```python
class MultimodalValue(TypedDict):
    text: NotRequired[str]
    files: NotRequired[list[str]]
```""", elem_classes=["md-custom", "MultimodalValue"], header_links=True)

    demo.load(None, js=r"""function() {
    const refs = {
            MultimodalValue: [], };
    const user_fn_refs = {
          MedChatInput: ['MultimodalValue'], };
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
