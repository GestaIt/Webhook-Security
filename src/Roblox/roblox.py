import requests
import json.decoder

asset_details_cache = {}


# used to easily generate the request details
def generate_request_info(cookie: str, csrf: str = "") -> tuple[dict, dict]:
    cookies = {
        ".ROBLOSECURITY": cookie
    }

    headers = {
        "X-CSRF-TOKEN": csrf
    }

    return cookies, headers


# generates a cross reference token to use in a requests headers, returns true if successful
def generate_reference_token(session: requests.Session, cookie: str) -> tuple[bool, str]:
    request_details = generate_request_info(cookie)

    try:
        response = session.post("https://auth.roblox.com/v2/logout", cookies=request_details[0])

        reference_token = response.headers["x-csrf-token"]
    except (KeyError, OSError, requests.exceptions.ProxyError):
        return False, ""

    return True, reference_token


# gets the specified assets details
def get_asset_details(session: requests.Session, asset_id: str) -> tuple[bool, dict]:
    try:
        if asset_id not in asset_details_cache.keys():
            response = session.get(f"https://api.roblox.com/marketplace/productinfo?assetId={asset_id}")

            if response.status_code == 200:
                response_json = response.json()

                asset_details_cache[asset_id] = response_json
                return True, response_json
            else:
                return False, {}
        else:
            return True, asset_details_cache[asset_id]
    except (OSError, requests.exceptions.ProxyError):
        return False, {}


# makes the authenticated user purchase an asset
def purchase_asset(cookie: str, asset_id: str, session: requests.Session = None) -> bool:
    if session is None:
        session = requests.session()

    asset_details_success, asset_info = get_asset_details(session, asset_id)

    if asset_details_success:
        creator_id = asset_info["Creator"]["Id"]
        success, cross_reference_token = generate_reference_token(session, cookie)

        if success:
            cookies, headers = generate_request_info(cookie, cross_reference_token)
            body = {
                "expectedCurrency": 1,
                "expectedPrice": 0,
                "expectedSellerId": creator_id
            }

            try:
                response = session.post(f"https://economy.roblox.com/v1/purchases/products/{asset_info['ProductId']}",
                                        cookies=cookies, headers=headers, json=body)

                if response.status_code == 200:
                    return True
                else:
                    return False
            except (OSError, requests.exceptions.ProxyError):
                return False
        else:
            return False
    else:
        return False


# makes the authenticated user delete an asset from their inventory, if they own it
def delete_asset(cookie: str, asset_id: str, session: requests.Session = None) -> bool:
    if session is None:
        session = requests.session()

    success, cross_reference_token = generate_reference_token(session, cookie)

    if success:
        cookies, headers = generate_request_info(cookie, cross_reference_token)
        body = {"assetId": asset_id}

        try:
            response = session.post("https://www.roblox.com/asset/delete-from-inventory",
                                    cookies=cookies, headers=headers, json=body)

            if response.status_code == 200:
                return True
            else:
                return False
        except (OSError, requests.exceptions.ProxyError):
            return False
    else:
        return False


# retrieves the universe id from a given place id
def get_universe_id(game_id: int) -> tuple[bool, str]:
    response = requests.get(f"https://api.roblox.com/universes/get-universe-containing-place?placeid={game_id}")

    try:
        response_json = response.json()
        universe_id = response_json["UniverseId"]
    except (json.decoder.JSONDecodeError, IndexError, ConnectionResetError):
        print(f"Failed to get universe id for {game_id}")
        return False, ""

    return True, str(universe_id)


# retrieves details for a given game
def get_game_details(game_id: int) -> tuple[bool, dict[str, str]]:
    get_successful, game_universe_id = get_universe_id(game_id)

    if get_successful:
        response = requests.get(f"https://games.roblox.com/v1/games?universeIds={game_universe_id}")

        try:
            response_json = response.json()
            details = response_json["data"][0]
        except (KeyError, IndexError, json.decoder.JSONDecodeError, ConnectionResetError):
            print(f"Failed to get game details for {game_id}")
            return False, {}

        return True, details
    else:
        print(f"failed to get universe id for {game_id}")
        return False, {}


# retrieves details for a given user
def get_player_id(username: str) -> tuple[bool, int]:
    json_arguments = {
        "usernames": [
            username
        ],
        "excludeBannedUsers": False
    }

    response = requests.post("https://users.roblox.com/v1/usernames/users", json=json_arguments)

    try:
        response_json = response.json()
        player_id = response_json["data"][0]["id"]
    except (KeyError, IndexError, json.decoder.JSONDecodeError, ConnectionResetError):
        print(f"Failed to get player id for {username}")
        return False, 0

    return True, player_id


# retrieves the name of a given user id
def get_player_name(user_id: int) -> tuple[bool, str]:
    json_arguments = {
        "userIds": [
            user_id
        ],
        "excludeBannedUsers": False
    }

    response = requests.post("https://users.roblox.com/v1/users", json=json_arguments)

    try:
        response_json = response.json()
        name = response_json["data"][0]["name"]
    except (KeyError, IndexError, json.decoder.JSONDecodeError, ConnectionResetError):
        print(f"Failed to get username for {user_id}")
        return False, ""

    return True, name


# Returns the id from the specified URL
def get_id_from_url(url: str) -> str:
    asset_id = ""

    for character in url:
        if character.isdigit():
            asset_id = asset_id + character

    return asset_id
