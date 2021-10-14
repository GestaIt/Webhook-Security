import os
import json
import requests
import time
import queue
from src.SQLServer.modelManager import is_model_logged, is_model_blacklisted
from src.DiscordBot.utilities import queue_model_logging_message
from src.Roblox.roblox import purchase_asset, delete_asset

working_directory = os.getenv("working directory", os.getcwd())

get_model_queue = queue.Queue()


# Retrieves a list of recently updated models
def get_updated_models() -> list[dict]:
    request = requests.get("https://search.roblox.com/catalog/json?CatalogContext=2&Category=6&ResultsPerPage=200&SortType=3")

    items = []

    try:
        for item in request.json():
            creator_type = "user" if item["Creator"].startswith("@") else "group"

            if is_model_blacklisted(item["CreatorAbsoluteUrl"], creator_type) or is_model_logged(item["AssetId"]):
                continue

            item_info = {
                "id": item["AssetId"],
                "name": item["Name"],
                "description": item["Description"],
                "asset_url": f"https://www.roblox.com/library/{item['AssetId']}/",
                "thumbnail_url": item["ThumbnailUrl"],
                "creator_name": item["Creator"],
                "creator_url": item["CreatorAbsoluteUrl"]
            }

            items.append(item_info)
    except json.decoder.JSONDecodeError:
        pass

    return items


def run_model_log() -> None:
    while True:
        models = get_updated_models()

        for model in models:
            queue_model_logging_message(model)
            get_model_queue.put(model)

        time.sleep(3)


def run_queue_get() -> None:
    while True:
        if not get_model_queue.empty():
            model = get_model_queue.get()

            # purchase_asset(cookie, model["id"])
            time.sleep(0.1)
