from src.interface import create_interface


def main():
    print("Initializing Project...")
    demo = create_interface()

    print("Launching application...")
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)


if __name__ == "__main__":
    main()
