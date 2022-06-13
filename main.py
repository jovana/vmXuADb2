import os
from dotenv import load_dotenv
import json
import requests

load_dotenv()

from functions import Functions

# This lambda does not have access to the private VPC network.
# So it will invoked from other lambda or ECS, retrive all settings
# to make call to 3th party (on the internet)


def handler(event, context):
    # print(event)

    # Check if function needs to run in debug mode
    if 'DEBUG' in event and event['DEBUG']:
        debug_mode = True
    else:
        debug_mode = False

    if debug_mode:
        msg_body = event
    else:
        # Getting the msg body from the SQS queue, needs to convert to json dict
        msg_body = event

    print(f"{json.dumps(msg_body)}\n===========\n")

    # Command to open Signal
    if msg_body['action'] == "open_signal":
        result = Functions().open_signal(msg_body)
        # sys.exit(0)
        return result

    # command for reloading the symbol list
    if msg_body['action'] == "get_symbol_list":
        result = Functions().get_symbol_list(msg_body)
        # sys.exit(0)
        return result

    # Command for getting the client_id
    if msg_body['action'] == "get_client_id":

        # Test the internet access
        url = "https://demo.ctraderapi.com:5035/"
        print(url)
        response = requests.get(url).content
        print(response)
        # End test

        result = Functions().get_client_id(msg_body)
        print(result)

        return result


# Manual invocation of the script (only used for testing / development)
if __name__ == "__main__":
    # Test data
    test = {
        "DEBUG": True,
        "action": "get_client_id",
        "signal_id": "fe1e8843-5feb-44e4-8dfd-e5197c5a5ac8",
        "customer_id": "aae8465e-7933-4e20-ac4f-13dcd7f7233a",
        "strategy_bot_id": "5fed0bf5-4ae5-46bc-be3f-ca1ccab1634a",
        "strategy_id": "2ed84bbd-0c56-4bd9-8acd-16de689a1f54",
        "data": {
            "account_id": None,
            "note": "Created by HapyBots Signal service. Please check your HappyBots accounts for details.",
            "pair": "NAS100",
            "instant": False,
            "position": {
                "type": "buy",
                "price": 11855,
                "order_type": "limit",
            },
            "take_profit": {
                "enabled": True,
                "steps": [{
                    "order_type": "limit",
                    "price": 12000,
                    "volume": 100
                }]
            },
            "stop_loss": {
                "enabled": True,
                "breakeven": False,
                "order_type": "limit",
                "price": 11800,
            }},
        "account_id": None,
        "position_value": 1.0,
        "signal_order_price": 11857,
        "base_order_volume": 0.1,
    }

    # status update
    # test = {
    #     "command": "get_smarttrade_status",
    #     "exchange_settings": {
    #         "api_key": os.getenv("3C_API_KEY"),
    #         "secret": os.getenv("3C_SECRET"),
    #     },
    #     "log_id": "1f6f405e-e10b-4cc0-8965-e02a5da4f799",
    #     "deal_id": 15125839, "auto_trigger": False,
    #     "customer_id": "aae8465e-7933-4e20-ac4f-13dcd7f7233a",
    #     "strategy_bot_id": "46f8f8c7-dae5-49cc-8acb-e2f93ab9304b",
    #     "strategy_id": "5cb70eb4-e60a-4c76-9416-5291f62f7177"}

    # Test function
    print(handler(test, None))
