# Stores the parse templates for cURL requests

from flask_restful import reqparse

whitelistPostParser = reqparse.RequestParser()
whitelistPostParser.add_argument("rID", required=True, type=int, help="ROBLOX User ID")
whitelistPostParser.add_argument("dID", required=True, type=str, help="Discord User ID")

whitelistDeleteParser = reqparse.RequestParser()
whitelistDeleteParser.add_argument("rID", required=True, type=str, help="ROBLOX User ID")

scriptPostParser = reqparse.RequestParser()
scriptPostParser.add_argument("sName", required=True, type=str, help="Script Name")
scriptPostParser.add_argument("sSource", required=True, type=str, help="Script Source")
scriptPostParser.add_argument("sDescription", required=True, type=str, help="Script Description")
scriptPostParser.add_argument("dID", required=True, type=str, help="Discord User ID")

scriptDeleteParser = reqparse.RequestParser()
scriptDeleteParser.add_argument("sName", required=True, type=str, help="Script Name")
scriptDeleteParser.add_argument("dID", required=True, type=str, help="Discord User ID")

gameLogPostParser = reqparse.RequestParser()
gameLogPostParser.add_argument("pID", required=True, type=int, help="Place ID")
gameLogPostParser.add_argument("jID", required=True, type=str, help="Job ID")

scriptLogPostParser = reqparse.RequestParser()
scriptLogPostParser.add_argument("rID", required=True, type=int, help="Roblox User ID")
scriptLogPostParser.add_argument("jID", required=True, type=str, help="Job ID")
scriptLogPostParser.add_argument("sSource", required=True, type=str, help="Script Source")
scriptLogPostParser.add_argument("pID", required=True, type=int, help="Roblox Place ID")
