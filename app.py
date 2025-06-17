from src.audio.core.dolphin import setup_dolphin_model
from src.interface import create_interface


def main():
    print("Initializing Project...")

    print("Setting up Dolphin ASR...")
    if not setup_dolphin_model():
        print("Warning: Dolphin ASR not initialized properly")
    else:
        print("Dolphin ASR initialized successfully")

    print("Creating Gradio interface...")
    demo = create_interface()

    print("Launching application...")
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)


if __name__ == "__main__":
    main()
