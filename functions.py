import json
import uuid
import datetime
from ctrader_api import cTraderAPI


class Functions(object):

    def open_signal(self, data: dict) -> bool:

        # Set start new deal command
        api = cTraderAPI(data["customer_id"])
        response = api.createNewOrder(data)
        print(response)

        signal_details = {
            "deal_type": "SMARTTRADE",
            "log_id": data["log_id"],
            "customer_id": data["customer_id"],
            "strategy_bot_id": data["strategy_bot_id"],
            "strategy_id": data["strategy_id"],
            "signal_id": data["signal_id"],
            "auto_trigger": True,   # Needed to restart the deal status automated.
        }

        return {"status": True, "msg": "SIGNAL_PUBLISHED", "data": {}}

    def get_symbol_list(self, data: dict) -> bool:
        api = cTraderAPI(data["customer_id"])
        symbols = api.getFullSymbolList()
        return symbols

    def get_client_id(self, data: dict) -> bool:
        client_settings = cTraderAPI(data["customer_id"]).getClientID()
        return client_settings
