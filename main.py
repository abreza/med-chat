from app.ui.main_interface import create_main_interface


def main():
    print("🚀 Initializing Voice AI Assistant...")
    interface = create_main_interface()
    
    print("🌐 Launching application...")
    interface.launch(
        server_name="0.0.0.0", 
        server_port=7860, 
        share=False
    )


if __name__ == "__main__":
    main()