<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import type { Gradio } from "@gradio/utils";
  import { Block } from "@gradio/atoms";
  import { StatusTracker } from "@gradio/statustracker";
  import type { LoadingStatus } from "@gradio/statustracker";

  export let elem_id = "";
  export let elem_classes: string[] = [];
  export let visible = true;
  export let value: {
    [key: string]: {
      file_id: string;
      name: string;
      size: number;
      type: string;
      subtype?: string;
      path: string;
      orig_name: string;
    };
  } | null = {};
  export let label: string;
  export let show_label: boolean;
  export let container = true;
  export let scale: number | null = null;
  export let min_width: number | undefined = undefined;
  export let loading_status: LoadingStatus | undefined = undefined;
  export let gradio: Gradio<{
    change: any;
    select: { file_id: string; selected: boolean };
    delete: { file_id: string };
  }>;

  const dispatch = createEventDispatcher();

  let selected_files: Set<string> = new Set();

  function handleSelectionChange(file_id: string, checked: boolean): void {
    if (checked) {
      selected_files.add(file_id);
    } else {
      selected_files.delete(file_id);
    }
    selected_files = selected_files; // Trigger reactivity
    gradio.dispatch("select", {
      file_id: file_id,
      selected: checked,
    });
    dispatch("select", {
      selected: Array.from(selected_files),
    });
  }

  function handleDelete(file_id: string): void {
    if (value && value[file_id]) {
      const new_value = { ...value };
      delete new_value[file_id];
      value = new_value;

      if (selected_files.has(file_id)) {
        selected_files.delete(file_id);
        selected_files = selected_files;
      }
      gradio.dispatch("delete", { file_id });
      gradio.dispatch("change", value);
    }
  }

  function getFileIcon(type: string, subtype?: string): string {
    if (type === "medical") {
      return subtype === "dicom" ? "🏥" : "🧠";
    }
    switch (type) {
      case "image":
        return "🖼️";
      case "text":
        return "📄";
      case "audio":
        return "🎵";
      case "video":
        return "🎬";
      default:
        return "📁";
    }
  }

  function formatFileSize(bytes: number): string {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB", "TB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  }

  $: file_count = value ? Object.keys(value).length : 0;
  $: selected_count = selected_files.size;
  $: files_array = value ? Object.values(value) : [];
</script>

<Block {visible} {elem_id} {elem_classes} {container} {scale} {min_width}>
  {#if loading_status}
    <StatusTracker
      autoscroll={gradio.autoscroll}
      i18n={gradio.i18n}
      {...loading_status}
    />
  {/if}
  <div class="file-manager-container">
    {#if file_count > 0}
      <div class="file-stats">
        <strong>📂 Managed Files ({file_count})</strong>
        <span class="selected-count">{selected_count} selected</span>
      </div>
      <div class="file-list">
        {#each files_array as file (file.file_id)}
          <div
            class="file-item"
            class:selected={selected_files.has(file.file_id)}
          >
            <div class="file-item-content">
              <div class="file-item-main">
                <label class="file-item-label">
                  <input
                    type="checkbox"
                    class="file-checkbox"
                    checked={selected_files.has(file.file_id)}
                    on:change={(e) =>
                      handleSelectionChange(
                        file.file_id,
                        e.currentTarget.checked
                      )}
                  />
                  <span class="file-icon"
                    >{getFileIcon(file.type, file.subtype)}</span
                  >
                  <div class="file-info">
                    <div class="file-name" title={file.orig_name}>
                      {file.orig_name}
                    </div>
                    <div class="file-meta">
                      <span class="file-type">{file.type.toUpperCase()}</span>
                      <span class="file-size">{formatFileSize(file.size)}</span>
                    </div>
                  </div>
                </label>
              </div>
              <div class="file-actions">
                <button
                  class="remove-btn"
                  title="Remove file"
                  on:click={() => handleDelete(file.file_id)}>🗑️</button
                >
              </div>
            </div>
          </div>
        {/each}
      </div>
    {:else}
      <div class="empty-file-list">
        <div class="empty-icon">📁</div>
        <p class="empty-title">No files uploaded</p>
        <p class="empty-subtitle">
          Upload images, text, or medical files (DICOM/NIfTI)
        </p>
      </div>
    {/if}
  </div>
</Block>

<style>
  .file-manager-container {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
    border: 1px solid var(--border-color-primary);
    border-radius: var(--radius-lg);
    height: 100%;
  }
  .file-stats {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-sm) var(--spacing-md);
    background: var(--background-fill-secondary);
    border-bottom: 1px solid var(--border-color-primary);
  }
  .file-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
    overflow-y: auto;
    flex-grow: 1;
  }
  .file-item {
    display: flex;
    align-items: center;
    padding: var(--spacing-sm);
    border: 1px solid var(--border-color-primary);
    border-radius: var(--radius-md);
    transition: background-color 0.2s;
  }
  .file-item.selected {
    background-color: var(--color-accent-soft);
    border-left: 4px solid var(--color-accent);
  }
  .file-item-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }
  .file-item-main {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
  }
  .file-item-label {
    display: flex;
    align-items: center;
    cursor: pointer;
    gap: var(--spacing-md);
  }
  .file-icon {
    font-size: var(--text-xl);
  }
  .file-info {
    display: flex;
    flex-direction: column;
  }
  .file-name {
    font-weight: var(--weight-semibold);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 150px;
  }
  .file-meta {
    display: flex;
    gap: var(--spacing-sm);
    color: var(--text-color-secondary);
    font-size: var(--text-sm);
  }
  .file-actions .remove-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: var(--text-lg);
    color: var(--text-color-secondary);
  }
  .empty-file-list {
    text-align: center;
    padding: var(--size-10);
    color: var(--text-color-secondary);
  }
  .empty-icon {
    font-size: var(--text-xxl);
    margin-bottom: var(--spacing-md);
  }
</style>
