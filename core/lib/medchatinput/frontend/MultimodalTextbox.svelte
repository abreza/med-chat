<script lang="ts">
	import {
		onMount,
		beforeUpdate,
		afterUpdate,
		createEventDispatcher,
		tick
	} from "svelte";
	import { text_area_resize, resize } from "./utils";
	import { BlockTitle } from "@gradio/atoms";
	import { Upload } from "@gradio/upload";
	import { Image } from "@gradio/image/shared";
	import type { FileData, Client } from "@gradio/client";
	import type { WaveformOptions } from "./types";
	import {
		Clear,
		File as FileIcon,
		Music,
		Paperclip,
		Video,
		Send,
		Square,
		Microphone
	} from "@gradio/icons";
	import type { SelectData } from "@gradio/utils";

	export let value: { text: string; files: FileData[] } = {
		text: "",
		files: []
	};

	export let value_is_output = false;
	export let lines = 1;
	export let i18n;
	export let placeholder = "Type here...";
	export let disabled = false;
	export let label: string;
	export let info: string | undefined = undefined;
	export let show_label = true;
	export let max_lines: number;
	export let submit_btn: string | boolean | null = null;
	export let stop_btn: string | boolean | null = null;
	export let rtl = false;
	export let autofocus = false;
	export let text_align: "left" | "right" | undefined = undefined;
	export let autoscroll = true;
	export let root: string;
	export let file_types: string[] | null = null;
	export let max_file_size: number | null = null;
	export let upload: Client["upload"];
	export let stream_handler: Client["stream"];
	export let file_count: "single" | "multiple" | "directory" = "multiple";
	export let max_plain_text_length = 1000;
	export let waveform_settings: Record<string, any>;
	export let waveform_options: WaveformOptions = {
		show_recording_waveform: true
	};
	export let sources: ["microphone" | "upload"] = ["upload"];
	export let auto_transcribe = true;
	export let keep_audio_after_transcribe = false;
	
	let upload_component: Upload;
	let el: HTMLTextAreaElement | HTMLInputElement;
	let can_scroll: boolean;
	let previous_scroll_top = 0;
	let user_has_scrolled_up = false;
	export let dragging = false;
	let uploading = false;
	let oldValue = value.text;

	let recording = false;
	let transcribing = false;
	let mediaRecorder: MediaRecorder | null = null;
	let audioChunks: Blob[] = [];
	let recordingStartTime: number = 0;

	$: dispatch("drag", dragging);

	let full_container: HTMLDivElement;

	$: if (oldValue !== value?.text) {
		dispatch("change", value);
		oldValue = value?.text;
	}

	$: if (value === null) value = { text: "", files: [] };
	$: value, el && lines !== max_lines && resize(el, lines, max_lines);

	const dispatch = createEventDispatcher<{
		change: typeof value;
		submit: undefined;
		stop: undefined;
		blur: undefined;
		select: SelectData;
		input: undefined;
		focus: undefined;
		drag: boolean;
		upload: FileData[] | FileData;
		clear: undefined;
		load: FileData[] | FileData;
		error: string;
		start_recording: undefined;
		pause_recording: undefined;
		stop_recording: undefined;
		transcription_complete: string;
	}>();

	beforeUpdate(() => {
		can_scroll = el && el.offsetHeight + el.scrollTop > el.scrollHeight - 100;
	});

	const scroll = (): void => {
		if (can_scroll && autoscroll && !user_has_scrolled_up) {
			el.scrollTo(0, el.scrollHeight);
		}
	};

	async function handle_change(): Promise<void> {
		dispatch("change", value);
		if (!value_is_output) {
			dispatch("input");
		}
	}

	onMount(() => {
		if (autofocus && el !== null) {
			el.focus();
		}
	});

	afterUpdate(() => {
		if (can_scroll && autoscroll) {
			scroll();
		}
		value_is_output = false;
	});

	function handle_select(event: Event): void {
		const target: HTMLTextAreaElement | HTMLInputElement = event.target as
			| HTMLTextAreaElement
			| HTMLInputElement;
		const text = target.value;
		const index: [number, number] = [
			target.selectionStart as number,
			target.selectionEnd as number
		];
		dispatch("select", { value: text.substring(...index), index: index });
	}

	async function handle_keypress(e: KeyboardEvent): Promise<void> {
		await tick();
		if (e.key === "Enter" && e.shiftKey && lines > 1) {
			e.preventDefault();
			dispatch("submit");
		} else if (
			e.key === "Enter" &&
			!e.shiftKey &&
			lines === 1 &&
			max_lines >= 1
		) {
			e.preventDefault();
			dispatch("submit");
		}
	}

	function handle_scroll(event: Event): void {
		const target = event.target as HTMLElement;
		const current_scroll_top = target.scrollTop;
		if (current_scroll_top < previous_scroll_top) {
			user_has_scrolled_up = true;
		}
		previous_scroll_top = current_scroll_top;

		const max_scroll_top = target.scrollHeight - target.clientHeight;
		const user_has_scrolled_to_bottom = current_scroll_top >= max_scroll_top;
		if (user_has_scrolled_to_bottom) {
			user_has_scrolled_up = false;
		}
	}

	async function handle_upload({
		detail
	}: CustomEvent<FileData>): Promise<void> {
		handle_change();
		if (Array.isArray(detail)) {
			for (let file of detail) {
				value.files.push(file);
			}
			value = value;
		} else {
			value.files.push(detail);
			value = value;
		}
		await tick();
		dispatch("change", value);
		dispatch("upload", detail);
	}

	function remove_thumbnail(event: MouseEvent, index: number): void {
		handle_change();
		event.stopPropagation();
		value.files.splice(index, 1);
		value = value;
	}

	function handle_upload_click(): void {
		upload_component.open_upload();
	}

	function handle_stop(): void {
		dispatch("stop");
	}

	function handle_submit(): void {
		dispatch("submit");
	}

	async function start_recording(): Promise<void> {
		try {
			const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
			mediaRecorder = new MediaRecorder(stream);
			audioChunks = [];

			mediaRecorder.ondataavailable = (event) => {
				audioChunks.push(event.data);
			};

			mediaRecorder.onstop = async () => {
				const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
				
				if (auto_transcribe) {
					await transcribe_audio_immediate(audioBlob);
				}
				
				await upload_audio_blob(audioBlob);
				
				stream.getTracks().forEach(track => track.stop());
			};

			mediaRecorder.start();
			recording = true;
			recordingStartTime = Date.now();
			dispatch("start_recording");
		} catch (error) {
			console.error("Error starting recording:", error);
			dispatch("error", "Failed to access microphone. Please check permissions.");
		}
	}

	async function stop_recording(): Promise<void> {
		if (mediaRecorder && recording) {
			mediaRecorder.stop();
			recording = false;
			dispatch("stop_recording");
		}
	}

	async function transcribe_audio_immediate(audioBlob: Blob): Promise<void> {
		if (!auto_transcribe) return;
		
		try {
			transcribing = true;
			
			const arrayBuffer = await audioBlob.arrayBuffer();
			const uint8Array = new Uint8Array(arrayBuffer);
			const base64String = btoa(String.fromCharCode(...uint8Array));
			
			const transcriptionResult = await (window as any).transcribeAudioImmediate(base64String);
			
			if (transcriptionResult && transcriptionResult.trim()) {
				if (value.text) {
					value.text += " " + transcriptionResult;
				} else {
					value.text = transcriptionResult;
				}
				
				await handle_change();
				dispatch("transcription_complete", transcriptionResult);
			}
			
		} catch (error) {
			console.error("Error during immediate transcription:", error);
			dispatch("error", "Failed to transcribe audio. The audio will still be uploaded.");
		} finally {
			transcribing = false;
		}
	}


	async function upload_audio_blob(blob: Blob): Promise<void> {
		try {
			const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
			const audioFile = new window.File([blob], `recording_${timestamp}.wav`, {
				type: "audio/wav",
				lastModified: Date.now()
			});

			if (!auto_transcribe || keep_audio_after_transcribe) {
				upload_component.load_files([audioFile]);
			}
		} catch (error) {
			console.error("Error uploading audio:", error);
			dispatch("error", "Failed to upload audio recording.");
		}
	}

	async function handle_microphone_click(): Promise<void> {
		if (disabled) return;
		
		if (recording) {
			await stop_recording();
		} else {
			await start_recording();
		}
	}

	async function handle_paste(event: ClipboardEvent): Promise<void> {
		if (!event.clipboardData) return;
		const items = event.clipboardData.items;
		const text = event.clipboardData.getData("text");

		if (text && text.length > max_plain_text_length) {
			event.preventDefault();
			const file = new window.File([text], "pasted_text.txt", {
				type: "text/plain",
				lastModified: Date.now()
			});
			if (upload_component) {
				upload_component.load_files([file]);
			}
			return;
		}

		for (let index in items) {
			const item = items[index];
			if (item.kind === "file" && item.type.includes("image")) {
				const blob = item.getAsFile();
				if (blob) upload_component.load_files([blob]);
			}
		}
	}

	function handle_dragenter(event: DragEvent): void {
		event.preventDefault();
		dragging = true;
	}

	function handle_dragleave(event: DragEvent): void {
		event.preventDefault();
		const rect = full_container.getBoundingClientRect();
		const { clientX, clientY } = event;
		if (
			clientX <= rect.left ||
			clientX >= rect.right ||
			clientY <= rect.top ||
			clientY >= rect.bottom
		) {
			dragging = false;
		}
	}

	function handle_drop(event: DragEvent): void {
		event.preventDefault();
		dragging = false;
		if (event.dataTransfer && event.dataTransfer.files) {
			const files = Array.from(event.dataTransfer.files);

			if (file_types) {
				const valid_files = files.filter((file) => {
					return file_types.some((type) => {
						if (type.startsWith(".")) {
							return file.name.toLowerCase().endsWith(type.toLowerCase());
						}
						return file.type.match(new RegExp(type.replace("*", ".*")));
					});
				});

				const invalid_files = files.length - valid_files.length;
				if (invalid_files > 0) {
					dispatch(
						"error",
						`${invalid_files} file(s) were rejected. Accepted formats: ${file_types.join(", ")}`
					);
				}

				if (valid_files.length > 0) {
					upload_component.load_files(valid_files);
				}
			} else {
				upload_component.load_files(files);
			}
		}
	}
</script>

<div
	class="full-container"
	class:dragging
	bind:this={full_container}
	on:dragenter={handle_dragenter}
	on:dragleave={handle_dragleave}
	on:dragover|preventDefault
	on:drop={handle_drop}
	role="group"
	aria-label="Multimedia input field"
>
	<BlockTitle {root} {show_label} {info} {rtl}>{label}</BlockTitle>
	{#if value.files.length > 0 || uploading}
		<div
			class="thumbnails scroll-hide"
			aria-label="Uploaded files"
			data-testid="container_el"
			style="display: {value.files.length > 0 || uploading ? 'flex' : 'none'};"
		>
			{#each value.files as file, index}
				<span role="listitem" aria-label="File thumbnail">
					<button class="thumbnail-item thumbnail-small">
						<button
							class:disabled
							class="delete-button"
							on:click={(event) => remove_thumbnail(event, index)}
							><Clear /></button
						>
						{#if file.mime_type && file.mime_type.includes("image")}
							<Image
								src={file.url}
								title={null}
								alt=""
								loading="lazy"
								class={"thumbnail-image"}
							/>
						{:else if file.mime_type && file.mime_type.includes("audio")}
							<Music />
						{:else if file.mime_type && file.mime_type.includes("video")}
							<Video />
						{:else}
							<FileIcon />
						{/if}
					</button>
				</span>
			{/each}
			{#if uploading}
				<div class="loader" role="status" aria-label="Uploading"></div>
			{/if}
		</div>
	{/if}

	<div class="input-container">
		{#if sources?.includes("upload") && !(file_count === "single" && value.files.length > 0)}
			<Upload
				bind:this={upload_component}
				on:load={handle_upload}
				{file_count}
				filetype={file_types}
				{root}
				{max_file_size}
				bind:dragging
				bind:uploading
				show_progress={false}
				disable_click={true}
				on:error
				hidden={true}
				{upload}
				{stream_handler}
			/>
			<button
				data-testid="upload-button"
				class="upload-button"
				{disabled}
				on:click={disabled ? undefined : handle_upload_click}
				><Paperclip /></button
			>
		{/if}
		{#if sources && sources.includes("microphone")}
			<button
				data-testid="microphone-button"
				class="microphone-button"
				class:recording
				class:transcribing={auto_transcribe && transcribing}
				{disabled}
				on:click={handle_microphone_click}
				title={recording 
					? "Stop recording" 
					: transcribing 
					? "Transcribing..." 
					: auto_transcribe 
					? "Record and transcribe audio" 
					: "Record audio"}
			>
				<Microphone />
				{#if auto_transcribe}
					<span class="transcribe-indicator">T</span>
				{/if}
				{#if recording}
					<span class="recording-pulse"></span>
				{:else if transcribing}
					<span class="transcribing-pulse"></span>
				{/if}
			</button>
		{/if}
		<!-- svelte-ignore a11y-autofocus -->
		<textarea
			data-testid="textbox"
			use:text_area_resize={{
				text: value.text,
				lines: lines,
				max_lines: max_lines
			}}
			class="scroll-hide"
			class:no-label={!show_label}
			dir={rtl ? "rtl" : "ltr"}
			bind:value={value.text}
			bind:this={el}
			{placeholder}
			rows={lines}
			{disabled}
			{autofocus}
			on:keypress={handle_keypress}
			on:blur
			on:select={handle_select}
			on:focus
			on:scroll={handle_scroll}
			on:paste={handle_paste}
			style={text_align ? "text-align: " + text_align : ""}
		/>
		{#if submit_btn}
			<button
				class="submit-button"
				class:padded-button={submit_btn !== true}
				{disabled}
				on:click={disabled ? undefined : handle_submit}
			>
				{#if submit_btn === true}
					<Send />
				{:else}
					{submit_btn}
				{/if}
			</button>
		{/if}
		{#if stop_btn}
			<button
				class="stop-button"
				class:padded-button={stop_btn !== true}
				on:click={handle_stop}
			>
				{#if stop_btn === true}
					<Square fill={"none"} stroke_width={2.5} />
				{:else}
					{stop_btn}
				{/if}
			</button>
		{/if}
	</div>
</div>

<style>
	.full-container {
		width: 100%;
		position: relative;
		padding: var(--block-padding);
		border: 1px solid transparent;
	}

	.full-container.dragging {
		border: 1px solid var(--color-accent);
		border-radius: calc(var(--radius-sm) - 1px);
	}

	.full-container.dragging::after {
		content: "";
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		pointer-events: none;
	}

	.input-container {
		display: flex;
		position: relative;
		align-items: flex-end;
	}

	textarea {
		flex-grow: 1;
		outline: none !important;
		background: var(--block-background-fill);
		padding: var(--input-padding);
		color: var(--body-text-color);
		font-weight: var(--input-text-weight);
		font-size: var(--input-text-size);
		line-height: var(--line-sm);
		border: none;
		margin-top: 0px;
		margin-bottom: 0px;
		resize: none;
		position: relative;
		z-index: 1;
		text-align: left;
	}
	textarea[dir="rtl"] {
		text-align: right;
	}

	textarea[dir="rtl"] ~ .submit-button {
		order: -1;
		margin-left: 0;
		margin-right: var(--spacing-sm);
	}

	textarea[dir="rtl"] ~ .submit-button :global(svg) {
		transform: scaleX(-1);
	}

	textarea.no-label {
		padding-top: 5px;
		padding-bottom: 5px;
	}

	textarea:disabled {
		-webkit-opacity: 1;
		opacity: 1;
	}

	textarea::placeholder {
		color: var(--input-placeholder-color);
	}

	.microphone-button,
	.upload-button,
	.submit-button,
	.stop-button {
		border: none;
		text-align: center;
		text-decoration: none;
		font-size: 14px;
		cursor: pointer;
		border-radius: 15px;
		min-width: 30px;
		height: 30px;
		flex-shrink: 0;
		display: flex;
		justify-content: center;
		align-items: center;
		z-index: var(--layer-1);
		margin-left: var(--spacing-sm);
		position: relative;
	}
	.padded-button {
		padding: 0 10px;
	}

	.microphone-button,
	.stop-button,
	.upload-button,
	.submit-button {
		background: var(--button-secondary-background-fill);
	}

	.microphone-button:hover:not(:disabled),
	.stop-button:hover:not(:disabled),
	.upload-button:hover:not(:disabled),
	.submit-button:hover:not(:disabled) {
		background: var(--button-secondary-background-fill-hover);
	}

	.microphone-button:disabled,
	.stop-button:disabled,
	.upload-button:disabled,
	.submit-button:disabled {
		background: var(--button-secondary-background-fill);
		cursor: not-allowed;
	}
	.microphone-button:active,
	.stop-button:active,
	.upload-button:active,
	.submit-button:active {
		box-shadow: var(--button-shadow-active);
	}

	.microphone-button.transcribing {
		background: var(--color-orange-100);
		border: 1px solid var(--color-orange-500);
	}

	.microphone-button.recording {
		background: var(--color-red-100);
		border: 1px solid var(--color-red-500);
	}

	.transcribe-indicator {
		position: absolute;
		top: -2px;
		right: -2px;
		background: var(--color-accent);
		color: white;
		border-radius: 50%;
		width: 12px;
		height: 12px;
		font-size: 8px;
		font-weight: bold;
		display: flex;
		align-items: center;
		justify-content: center;
		line-height: 1;
	}

	.recording-pulse {
		position: absolute;
		top: -3px;
		left: -3px;
		right: -3px;
		bottom: -3px;
		border: 2px solid var(--color-red-500);
		border-radius: 50%;
		animation: pulse 1.5s infinite;
	}

	.transcribing-pulse {
		position: absolute;
		top: -3px;
		left: -3px;
		right: -3px;
		bottom: -3px;
		border: 2px solid var(--color-orange-500);
		border-radius: 50%;
		animation: pulse 2s infinite;
	}

	@keyframes pulse {
		0% {
			transform: scale(0.8);
			opacity: 1;
		}
		50% {
			transform: scale(1.1);
			opacity: 0.7;
		}
		100% {
			transform: scale(0.8);
			opacity: 1;
		}
	}

	.submit-button :global(svg) {
		height: 22px;
		width: 22px;
	}
	.microphone-button :global(svg),
	.upload-button :global(svg) {
		height: 17px;
		width: 17px;
	}

	.stop-button :global(svg) {
		height: 16px;
		width: 16px;
	}

	.loader {
		display: flex;
		justify-content: center;
		align-items: center;
		--ring-color: transparent;
		position: relative;
		border: 5px solid #f3f3f3;
		border-top: 5px solid var(--color-accent);
		border-radius: 50%;
		width: 25px;
		height: 25px;
		animation: spin 2s linear infinite;
	}

	@keyframes spin {
		0% {
			transform: rotate(0deg);
		}
		100% {
			transform: rotate(360deg);
		}
	}

	.thumbnails :global(img) {
		width: var(--size-full);
		height: var(--size-full);
		object-fit: cover;
		border-radius: var(--radius-lg);
	}

	.thumbnails {
		display: flex;
		align-items: center;
		gap: var(--spacing-lg);
		overflow-x: scroll;
		padding-top: var(--spacing-sm);
		margin-bottom: 6px;
	}

	.thumbnail-item {
		display: flex;
		justify-content: center;
		align-items: center;
		--ring-color: transparent;
		position: relative;
		box-shadow:
			0 0 0 2px var(--ring-color),
			var(--shadow-drop);
		border: 1px solid var(--border-color-primary);
		border-radius: var(--radius-lg);
		background: var(--background-fill-secondary);
		aspect-ratio: var(--ratio-square);
		width: var(--size-full);
		height: var(--size-full);
		cursor: default;
	}

	.thumbnail-small {
		flex: none;
		transform: scale(0.9);
		transition: 0.075s;
		width: var(--size-12);
		height: var(--size-12);
	}

	.thumbnail-item :global(svg) {
		width: 30px;
		height: 30px;
	}

	.delete-button {
		display: flex;
		justify-content: center;
		align-items: center;
		position: absolute;
		right: -7px;
		top: -7px;
		color: var(--button-secondary-text-color);
		background: var(--button-secondary-background-fill);
		border: none;
		text-align: center;
		text-decoration: none;
		font-size: 10px;
		cursor: pointer;
		border-radius: 50%;
		width: 20px;
		height: 20px;
	}

	.disabled {
		display: none;
	}

	.delete-button :global(svg) {
		width: 12px;
		height: 12px;
	}

	.delete-button:hover {
		filter: brightness(1.2);
		border: 0.8px solid var(--color-grey-500);
	}
</style>
