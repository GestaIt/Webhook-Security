import threading
from src.DiscordBot.discordBot import run_bot
from src.WebServer.webServer import run_server
# from src.Roblox.modelLogger import run_queue_get


def main():
    threading.Thread(target=run_server).start()
    # threading.Thread(target=run_model_log).start()
    # threading.Thread(target=run_queue_get).start()

    run_bot()


if __name__ == "__main__":
    # Run the program
    main()
