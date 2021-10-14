# Stores the parse templates for cURL requests

from flask_restful import reqparse

gameLogPostParser = reqparse.RequestParser()
gameLogPostParser.add_argument("pID", required=True, type=int, help="Place ID")
gameLogPostParser.add_argument("jID", required=True, type=str, help="Job ID")

scriptLogPostParser = reqparse.RequestParser()
scriptLogPostParser.add_argument("rID", required=True, type=int, help="Roblox User ID")
scriptLogPostParser.add_argument("jID", required=True, type=str, help="Job ID")
scriptLogPostParser.add_argument("sSource", required=True, type=str, help="Script Source")
scriptLogPostParser.add_argument("pID", required=True, type=int, help="Roblox Place ID")
