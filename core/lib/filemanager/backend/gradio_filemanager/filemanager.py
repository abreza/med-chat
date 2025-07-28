from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional

import gradio as gr
from gradio.components.base import Component
from gradio.data_classes import GradioModel, GradioRootModel


class FileManagerData(GradioModel):
    file_id: str
    name: str
    size: int
    type: str
    subtype: Optional[str] = None
    path: str
    orig_name: str


class FilesData(GradioRootModel):
    root: Dict[str, FileManagerData]


class FileManager(Component):
    """
    A custom component to manage and display a list of uploaded files with selection and deletion capabilities.
    """

    EVENTS = ["change", "select", "delete"]
    data_model = FilesData

    def __init__(
        self,
        value: Dict[str, Any] | None = None,
        *,
        label: str | None = None,
        every: float | None = None,
        show_label: bool = True,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: List[str] | str | None = None,
    ):
        """
        Initializes the FileManager component.

        Parameters:
            value: A dictionary representing the initial state of the files.
            label: The component label.
            every: If `value` is a callable, run the function 'every' number of seconds.
            show_label: If True, shows the component label.
            container: If True, wraps the component in a container.
            scale: The relative size of the component.
            min_width: The minimum width of the component.
            visible: If False, the component is not visible.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM.
        """
        self.managed_files_dir = Path(
            gr.utils.get_upload_folder()) / "file_manager"
        self.managed_files_dir.mkdir(parents=True, exist_ok=True)
        super().__init__(
            label=label,
            every=every,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            value=value,
        )

    def preprocess(self, payload: FilesData | None) -> Dict[str, Any] | None:
        """
        Processes the payload from the frontend.

        Parameters:
            payload: The FilesData object from the frontend.
        Returns:
            A dictionary representing the files data.
        """
        if payload is None:
            return None
        return {k: v.model_dump() for k, v in payload.root.items()}

    def postprocess(self, value: Dict[str, Any] | None) -> FilesData | None:
        """
        Processes the value to be sent to the frontend.

        Parameters:
            value: The dictionary of files data.
        Returns:
            A FilesData object.
        """
        if value is None:
            return None
        return FilesData(root=value)

    def example_payload(self) -> Any:
        return {}

    def example_value(self) -> Any:
        return {}
