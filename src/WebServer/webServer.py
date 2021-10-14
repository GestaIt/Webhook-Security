from flask import Flask, request
from flask_restful import Api, Resource
from waitress import serve
from logging import getLogger, INFO

from src.DiscordBot.utilities import queue_game_logging_message
from src.WebServer.requestParsers import gameLogPostParser
from src.WebServer.linker import get_key_guild
from src.Roblox.roblox import get_game_details


class GameLogsPost(Resource):
    @staticmethod
    def post() -> tuple[list, int]:
        args = gameLogPostParser.parse_args()
        headers = request.headers

        if "AUTH-TOKEN" in headers:
            fetch_success, key_information = get_key_guild(headers["AUTH-TOKEN"])

            if fetch_success:
                place_id = args["pID"]
                job_id = args["jID"]

                details_success, place_details = get_game_details(place_id)

                if details_success and len(job_id) == 36:
                    queue_status = queue_game_logging_message(key_information["game_logging_channel"],
                                                              place_details, job_id)

                    if queue_status:
                        return [], 200

        return [], 500


def run_server():
    app = Flask(__name__)
    api = Api(app)

    logger = getLogger("waitress")
    logger.setLevel(INFO)

    api.add_resource(GameLogsPost, "/api/v1/log/game")

    print("serving webserver")
    serve(app, host="0.0.0.0", port=80, threads=4, connection_limit=5000)
