import gradio as gr


class MedicalTheme(gr.themes.Soft):
    def __init__(self):
        super().__init__(
            primary_hue=gr.themes.colors.blue,
            secondary_hue=gr.themes.colors.gray,
            neutral_hue=gr.themes.colors.slate,
            font=gr.themes.GoogleFont("Inter"),
        )

        self.set(
            body_background_fill="*neutral_50",
            body_background_fill_dark="*neutral_900",

            block_background_fill="white",
            block_background_fill_dark="*neutral_800",

            block_border_color="*neutral_200",
            block_border_color_dark="*neutral_700",

            body_text_color="*neutral_700",
            body_text_color_dark="*neutral_100",
            body_text_color_subdued="*neutral_500",
            body_text_color_subdued_dark="*neutral_400",

            input_background_fill="white",
            input_background_fill_dark="*neutral_700",
            input_border_color="*neutral_300",
            input_border_color_dark="*neutral_600",

            button_primary_background_fill="*primary_500",
            button_primary_background_fill_dark="*primary_600",
            button_primary_text_color="white",
            button_primary_text_color_dark="white",

            button_secondary_background_fill="*neutral_100",
            button_secondary_background_fill_dark="*neutral_700",
            button_secondary_text_color="*neutral_700",
            button_secondary_text_color_dark="*neutral_100",

            background_fill_primary="white",
            background_fill_primary_dark="*neutral_800",
            background_fill_secondary="*neutral_50",
            background_fill_secondary_dark="*neutral_700",
        )
