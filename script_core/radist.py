import json
import requests

host = 'https://api.radist.online/v2'


class Radist:
    def __init__(self, api_key: str, connection_id: int):
        self.headers = {
            'accept': 'application/json',
            'X-Api-Key': api_key
        }
        self.connection_id = connection_id
        self.company_id = None

    def _get_company_id(self) -> (int, bool):
        try:
            response = requests.get(host + '/companies/?limit=100&offset=0', headers=self.headers)
            if response.status_code == 200:
                return response.json()['companies'][0]['id'], True
            else:
                return 0, False
        except:
            return -1, False

    def _get_connection_id(self) -> (int, bool):
        try:
            response = requests.get(host + f'/companies/{self.company_id}/connections/{self.connection_id}',
                                    headers=self.headers)
            if response.status_code == 200:
                return self.connection_id, True
            else:
                return None, False
        except:
            return None, False

    def _get_chat_by_username(self, username: str) -> (int, bool):
        try:
            data = {
                "connection_id": self.connection_id,
                "user_name": username
            }
            response = requests.post(host + f'/companies/{self.company_id}/messaging/chats/', headers=self.headers,
                                     data=json.dumps(data))
            if response.status_code != 200:
                return -1, False
            else:
                return response.json()['chat_id'], True
        except:
            return -1, False

    def _send_message_to_radist(self, message: str, chat_id: int) -> bool:
        try:
            data = {
                'connection_id': self.connection_id,
                'chat_id': chat_id,
                'mode': 'async',
                'message_type': 'text',
                'text': {
                    'text': message
                }
            }
            response = requests.post(host + f'/companies/{self.company_id}/messaging/messages/',
                                     headers=self.headers,
                                     data=json.dumps(data))
            return response.status_code == 200
        except:
            return False

    def connect(self) -> (str, bool):
        self.company_id, status = self._get_company_id()
        if self.company_id == 0 and not status:
            return "Radist api key не валиден!", False
        elif self.company_id == -1 and not status:
            return "У вас нет активных компаний в Radist!", False
        else:
            self.connection_id, status = self._get_connection_id()
            if status:
                return "Вы успешно авторизованы!", True
            else:
                return "Не правильный connection_id!", False

    def send_message(self, message: str, username: str) -> (str, bool):
        """Создает сделку и отправляет приветственное сообщение"""
        text, status = self.connect()
        if not status:
            return text, status

        chat_id, status = self._get_chat_by_username(username=username)
        if not status:
            return "Не удалось создать или получить чат!", False

        status = self._send_message_to_radist(message=message, chat_id=chat_id)
        if not status:
            return "Не удалось отправить сообщение!", False
        return "Сообщение отправлено!", True
