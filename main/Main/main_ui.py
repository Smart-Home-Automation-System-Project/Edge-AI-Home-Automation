from web.server import init_webui

if __name__ == "__main__":
    init_webui()
    try:
        while True:
            pass  # Keep the main thread alive
    except KeyboardInterrupt:
        print("Stopped.")
