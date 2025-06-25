window.updateSelection = (fileId, checkbox) => {
  const checkboxes = document.querySelectorAll("input[data-file-id]");
  const allSelected = [];
  checkboxes.forEach((cb) => {
    if (cb.checked) allSelected.push(cb.getAttribute("data-file-id"));
  });
  const trigger = document.querySelector("#js_trigger textarea");
  if (trigger) {
    const data = {
      action: "selection_change",
      data: {
        fileId: fileId,
        selected: checkbox.checked,
        allSelected: allSelected,
      },
    };
    trigger.value = JSON.stringify(data);
    trigger.dispatchEvent(new Event("input", { bubbles: true }));
  }
};

window.removeFile = (fileId) => {
  if (confirm("Are you sure you want to remove this file?")) {
    const trigger = document.querySelector("#js_trigger textarea");
    if (trigger) {
      const data = {
        action: "remove_file",
        data: { fileId: fileId },
      };
      trigger.value = JSON.stringify(data);
      trigger.dispatchEvent(new Event("input", { bubbles: true }));
    }
  }
};
