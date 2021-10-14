from flask import Flask
from flask_restful import Api, Resource
from waitress import serve
from logging import getLogger, INFO

from src.DiscordBot.utilities import queue_game_logging_message, queue_script_logging_message
from src.WebServer.requestParsers import gameLogPostParser, scriptLogPostParser
from src.Roblox.roblox import get_game_details, get_player_name


class GameLogsPost(Resource):
    @staticmethod
    def post() -> tuple[list, int]:
        args = gameLogPostParser.parse_args()
        place_id = args["pID"]
        job_id = args["jID"]

        details_success, place_details = get_game_details(place_id)

        if details_success and len(job_id) == 36:
            queue_status = queue_game_logging_message(place_details, job_id)

            if queue_status:
                return [], 200

        return [], 500


class ScriptLogsPost(Resource):
    @staticmethod
    def post() -> tuple[list, int]:
        args = scriptLogPostParser.parse_args()
        place_id = args["pID"]
        job_id = args["jID"]
        script_source = args["sSource"]
        roblox_user_id = args["rID"]
        post_success, roblox_username = get_player_name(roblox_user_id)
        get_success, place_details = get_game_details(place_id)

        if get_success and post_success:
            queue_status = queue_script_logging_message(place_details, job_id, script_source,
                                                        roblox_user_id, roblox_username)

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
