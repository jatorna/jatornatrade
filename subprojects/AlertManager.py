import requests
from subprojects.types.Common import *


class AlertManager:

    def __init__(self, config, is_data_server):
        self.config = config
        self.is_data_server = is_data_server

    def send_telegram_alert(self, msg):

        if msg != "":
            if not self.is_data_server:
                if self.config.general.mode == EngineMode.REALTIME and self.config.general.tgm_alerts:
                    msg_session = self.config.general.session_id + '\n'
                    self.send_msg(msg_session + msg)

            if self.is_data_server and self.config.general.tgm_alerts:
                self.send_msg(msg)

    def send_msg(self, msg):
        id = self.config.general.alerts_bot_group
        token = self.config.general.alerts_bot_token

        url = "https://api.telegram.org/bot" + token + "/sendMessage"
        params = {
            'chat_id': id,
            'text': msg
        }
        requests.post(url, params=params)
