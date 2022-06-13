import os
from ctrader_open_api import Client, Protobuf, TcpProtocol, Auth, EndPoints
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
from ctrader_open_api.messages.OpenApiMessages_pb2 import *
from ctrader_open_api.messages.OpenApiModelMessages_pb2 import *
from twisted.internet import reactor
from google.protobuf import json_format
import datetime
import json


class cTraderAPI(object):

    def __init__(self, customer_id: str) -> None:
        print(f"Customer: {customer_id}\n===========\n")
        self.resultsResponseCallback = None     # This will loaded in the last step of the API calls
        self.functionToCall = ""
        self.functionParams = {}
        self.plugin_settings = {}

        try:

            self.plugin_settings = {
                'customer_id': 'aae8465e-7933-4e20-ac4f-13dcd7f7233a',
                'exchange_id': '3f365288-1991-485e-833a-aa4d5c40cb43',
                'exchange_settings': {
                    'exchange_name': 'cTrader',
                    'access_token': os.getenv("CTRADER_ACCESS_TOKEN"),
                    'refresh_token': '',
                    'is_live': False,
                    'last_refresh': '2022-06-13T13:17:40.531641+00:00',
                    'exchange_create_date': '2022-06-13T13:17:40.531661+00:00',
                    'enabled': True,
                    'client_id': 23973654
                },
                'exchange_status': 'CONNECTED',
                'exchange_system_name': 'ctrader',
                'vendor_id': '0'
            }

            print(f"Settings: {self.plugin_settings}\n===========\n")
            if self.plugin_settings["exchange_settings"]["enabled"]:
                self.client_id = self.plugin_settings["exchange_settings"]["client_id"]
                self.access_token = self.plugin_settings["exchange_settings"]["access_token"]
                self.refresh_token = self.plugin_settings["exchange_settings"]["refresh_token"]
                self.is_live = self.plugin_settings["exchange_settings"]["is_live"]
                self.client = Client(EndPoints.PROTOBUF_LIVE_HOST if self.is_live else EndPoints.PROTOBUF_DEMO_HOST, EndPoints.PROTOBUF_PORT, TcpProtocol)
            else:
                raise Exception('cTrader not enabled for this customer, abort!')

        except Exception as e:
            # there is no customer at all, so return 0 to create the first customer on debtor 1
            print(f"cTrader not configured")
            print(f"Error in GetPluginSettings: {e.__str__()}")
            raise Exception('cTrader not configured for this customer, abort!')

        # Check if the last refresh date is 14 day's old.
        current_date = datetime.datetime.now()
        days = datetime.timedelta(14)
        token_time = self.plugin_settings["exchange_settings"]["last_refresh"].split('T')[0]
        token_time = datetime.datetime.strptime(token_time, '%Y-%m-%d')

        # check if info needs to refresh? Token is valid for 2628000 seconds (30 day's)
        if token_time < (current_date - days):
            print("need refresh")
            # TODO: refresh token

    # def __del__(self):
    #     print("I'm being automatically destroyed. Goodbye!")

    def getSymbolDetails(self, requestSymbol: str):
        """Getting the symbol details from a given symbol.

        Args:
            ctidTraderAccountId (int): _description_
            accessToken (str): _description_
            requestSymbol (str): _description_

        Returns:
            _type_: _description_
        """
        # print(symbol)
        # print(ctidTraderAccountId)
        # Set the correct function to call
        self.functionToCall = "ProtoOASymbolsListReq"
        self.functionParams["ctidTraderAccountId"] = self.client_id
        self.functionParams["accessToken"] = self.access_token
        self.__start()

        symbolList = self.resultsResponseCallback
        # print(symbolList)
        data = list(filter(lambda symbol: symbol.symbolName == requestSymbol, symbolList.symbol))
        print(data)
        return {
            "symbolId": data[0].symbolId,
            "symbolName": data[0].symbolName,
            "enabled": data[0].enabled,
            "baseAssetId": data[0].baseAssetId,
            "quoteAssetId": data[0].quoteAssetId,
            "quoteAssetId": data[0].quoteAssetId,
            "symbolCategoryId": data[0].symbolCategoryId,
            "description": data[0].description,
        }

    def getFullSymbolList(self):
        """Getting the full supported symbol list

        Args:
            ctidTraderAccountId (int): _description_
            accessToken (str): _description_

        Returns:
            _type_: _description_
        """
        # Set the correct function to call
        self.functionToCall = "ProtoOASymbolsListReq"
        self.functionParams["ctidTraderAccountId"] = int(self.client_id)
        self.functionParams["accessToken"] = str(self.access_token)
        self.__start()

        symbolList = self.resultsResponseCallback
        data = list(map(self.__transformSymbols, symbolList.symbol))
        return data

    def getClientID(self) -> int:
        """Getting the ctidTraderAccountId from the API

        Args:
            accessToken (str): _description_

        Returns:
            _type_: _description_
        """
        # Set the function and parameters
        self.functionParams["accessToken"] = self.access_token
        self.functionToCall = "ProtoOAGetAccountListByAccessTokenReq"
        self.__start()

        # Process results
        # print(self.resultsResponseCallback)
        client_object = json.loads(json_format.MessageToJson(self.resultsResponseCallback))
        # print(client_object)
        # print("=" * 80)
        if self.resultsResponseCallback is not None:
            # return self.resultsResponseCallback.ctidTraderAccount[0].ctidTraderAccountId
            return client_object["ctidTraderAccount"][0]
        else:
            return {}

    def createNewOrder(self, data: dict) -> object:

        # ProtoOAAmendOrderReq = order aanpassen
        # ProtoOACancelOrderReq = order annuleren
        # ProtoOANewOrderReq = new order
        self.functionParams = data
        self.functionParams["accessToken"] = self.access_token
        self.functionParams["ctidTraderAccountId"] = self.client_id

        self.functionToCall = "ProtoOANewOrderReq"
        self.__start()

        # Process results
        bla = json_format.MessageToJson(self.resultsResponseCallback)
        # print(self.resultsResponseCallback)
        print(bla)

        return False

    def __getSymbolsList(self, result):
        """This function returns the full symbol list.

        Args:
            result (_type_): _description_
        """
        request = ProtoOASymbolsListReq()
        request.ctidTraderAccountId = self.functionParams["ctidTraderAccountId"]  # 23973654
        deferred = self.client.send(request)
        deferred.addCallbacks(self.__resultsResponseCallback, self.__onError)

    def __createNewOrder(self, result):
        """ First STEP: getting the symbolID

        Args:
            result (_type_): _description_
        """
        request = ProtoOASymbolsListReq()
        request.ctidTraderAccountId = self.functionParams["ctidTraderAccountId"]  # 23973654
        deferred = self.client.send(request)
        deferred.addCallbacks(self.__createNewOrderStepCallback, self.__onError)

    def __createNewOrderStepCallback(self, result):
        """Called from the first step__createNewOrder, continue create a new order
            https://spotware.github.io/open-api-docs/messages/#protooaneworderreq

        Args:
            result (_type_): _description_
        """
        symbolList = Protobuf.extract(result)

        data = list(filter(lambda symbol: symbol.symbolName == self.functionParams["data"]["pair"], symbolList.symbol))
        print(data)
        self.functionParams["symbolId"] = data[0].symbolId
        print(self.functionParams)

        request = ProtoOANewOrderReq()
        request.ctidTraderAccountId = self.functionParams["ctidTraderAccountId"]
        request.comment = self.functionParams["data"]["note"]

        # Order position
        request.symbolId = self.functionParams["symbolId"]
        request.orderType = 2 if self.functionParams["data"]["position"]["order_type"] == "limit" else 1     # 1 = Market, 2 = Limit
        request.tradeSide = 1 if self.functionParams["data"]["position"]["type"] == "buy" else 2             # 1 = BUY / LONG, 2 = SELL / SHORT
        request.volume = int(self.functionParams["base_order_volume"] / 0.01)                   # The volume represented in 0.01
        request.limitPrice = self.functionParams["data"]["position"]["price"]    # If ordertype is limit

        # Stop loss settings
        # request.stopLoss = 24
        request.stopLoss = self.functionParams["data"]["stop_loss"]["price"]
        request.trailingStopLoss = True

        # Take profit settings
        request.takeProfit = self.functionParams["data"]["take_profit"]["steps"][0]["price"]
        request.clientOrderId = f"signal_id::{self.functionParams['signal_id']}"

        deferred = self.client.send(request)
        deferred.addCallbacks(self.__resultsResponseCallback, self.__onError)

    def __transformSymbols(self, data):
        """This function transforms the Symbol output.

        Args:
            data (_type_): _description_

        Returns:
            _type_: _description_
        """

        return {
            "symbolId": data.symbolId,
            "symbolName": data.symbolName,
            "enabled": data.enabled,
            "baseAssetId": data.baseAssetId,
            "quoteAssetId": data.quoteAssetId,
            "quoteAssetId": data.quoteAssetId,
            "symbolCategoryId": data.symbolCategoryId,
            "description": data.description,
        }

    def __getAccountListByAccessToken(self, result):
        # Application has been authenticated.
        # print("init ProtoOAGetAccountListByAccessTokenReq")
        request = ProtoOAGetAccountListByAccessTokenReq()
        request.accessToken = self.functionParams["accessToken"]
        deferred = self.client.send(request)
        deferred.addCallbacks(self.__resultsResponseCallback, self.__onError)

    def __accountAuthReq(self, result):
        """This function needs to check if the account has been authorisated

        Args:
            result (_type_): _description_
        """
        print("\nAccount authentication")
        request = ProtoOAAccountAuthReq()
        request.ctidTraderAccountId = self.functionParams["ctidTraderAccountId"]
        request.accessToken = self.functionParams["accessToken"]
        deferred = self.client.send(request)

        if self.functionToCall == "ProtoOASymbolsListReq":
            deferred.addCallbacks(self.__getSymbolsList, self.__onError)
            # deferred.addCallbacks(accountAuthResponseCallback, onError)

        elif self.functionToCall == "ProtoOANewOrderReq":
            deferred.addCallbacks(self.__createNewOrder, self.__onError)

        else:
            print("functionToCall to set or unknown!")
            self.__stop()
            return False

    def __connected(self, client):  # Callback for client connection
        """This is the first API call for application authentication. From there is will call the next job

        Args:
            client (_type_): _description_

        Returns:
            _type_: _description_
        """

        request = ProtoOAApplicationAuthReq()
        request.clientId = os.getenv("CTRADER_APP_CLIENT_ID")
        request.clientSecret = os.getenv("CTRADER_APP_CLIENT_SECRET")
        deferred = client.send(request)

        # Setting the correct callback function based on the functionToCall variable
        if self.functionToCall == "ProtoOAGetAccountListByAccessTokenReq":
            deferred.addCallbacks(self.__getAccountListByAccessToken, self.__onError)

        # elif self.functionToCall == "ProtoOANewOrderReq":
        #     deferred.addCallbacks(self.__getSymbolsList, self.__onError)

        else:
            # Other functions need to pass also the __accountAuthReq
            deferred.addCallbacks(self.__accountAuthReq, self.__onError)

    def __resultsResponseCallback(self, result):
        print("\nCallback received")
        # Saving the results object.
        self.resultsResponseCallback = Protobuf.extract(result)
        self.__stop()

    def __start(self):

        # Setting optional client callbacks
        self.client.setConnectedCallback(self.__connected)
        self.client.setDisconnectedCallback(self.__disconnected)
        self.client.setMessageReceivedCallback(self.__onMessageReceived)

        # Starting the client service
        self.client.startService()

        # Run Twisted reactor, we imported it earlier
        if not reactor.running:
            reactor.run()

    def __stop(self):
        # stopService

        if reactor.running:
            self.client.stopService()
            reactor.stop()

    def __onError(self, client, failure):  # Call back for errors
        print("\nMessage Error: ", failure)

    def __disconnected(self, client, reason):  # Callback for client disconnection
        print("\nDisconnected")
        self.__stop()

    def __onMessageReceived(self, client, message):  # Callback for receiving all messages
        # print(message.payloadType)
        # print(ProtoHeartbeatEvent().payloadType)
        # print("onMessageReceived=========")
        if message.payloadType in [
                ProtoOAGetAccountListByAccessTokenRes().payloadType,
                ProtoOASymbolsListRes().payloadType,
                ProtoOAAccountAuthRes().payloadType,
        ]:
            return
        print("\nMessage received: \n", Protobuf.extract(message))
