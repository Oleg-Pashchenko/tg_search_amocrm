import json
import requests

host = 'https://api.radist.online/v2'


class Radist:
    def __init__(self, api_key: str):
        self.headers = {
            'accept': 'application/json',
            'X-Api-Key': api_key
        }

    def _get_company_id(self) -> (int, bool):
        try:
            response = requests.get(host + '/companies/?limit=100&offset=0', headers=self.headers)
            if response.status_code == 200:
                return response.json()['companies'][0]['id'], True
            else:
                return 0, False
        except:
            return -1, False

    def is_api_key_valid(self) -> (str, bool):
        response, status = self._get_company_id()
        if response == 0 and not status:
            return "Radist api key не валиден!", False
        elif response == -1 and not status:
            return "У вас нет активных компаний в Radist!", False
        else:
            return response, True

    def send_message(self, message: str, username: str):
        """Создает сделку и отправляет приветственное сообщение"""
        pass


# radist = Radist(api_key=api_key)
# print(radist.is_api_key_valid())

"""

headers = {
    'accept': 'application/json',
    'X-Api-Key': api_key
}

company_id = 25757  # API
{
    "connection_id": 44309,
    "chat_id": 44309,
    "mode": "async",
    "message_type": "text",
    "text": {
        "text": "Test"
    }
}
host = 'https://api.radist.online/v2'
url = f'/companies/{company_id}/messaging/chats/'
body = {
    "connection_id": 0,
    "contact_id": 0,
    "phone": "string",
    "user_name": "string"
}

response = requests.post(host + url, headers=headers, data=json.dumps(body))
print(response.status_code)
print(response.json())
"""
