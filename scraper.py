import re
import time
from telethon.sync import TelegramClient

from misc import database
from script_core import amocrm, radist

past_messages_id = []


def create_telegram_client(session_name, api_id, api_hash):
    client = TelegramClient(session_name, int(api_id), api_hash)
    client.start()
    return client


def main():
    while True:
        time.sleep(60)
        accounts = database.get_all_accounts()
        for account in accounts:
            telegram_client = create_telegram_client(account.session_name, account.api_id, account.api_hash)
            amo = amocrm.Amocrm(host=account.amo_host, email=account.amo_login,
                                password=account.amo_password)
            amo.connect()
            r = radist.Radist(api_key=account.radist_api_key,
                              connection_id=account.radist_connection_id)

            keywords = account.search_words.split(',')
            search_groups = database.get_all_enabled_chats_by_user_id(account.id)
            for search_group in search_groups:
                search_title = search_group.chat_name
                group_id = account.link_to_telegram_channel

                def find_keywords(mess):
                    founded_keywords = [keyword for keyword in keywords if
                                        re.search(fr'\b{re.escape(keyword)}\b', mess.text, re.IGNORECASE)]
                    return founded_keywords

                chats = telegram_client.get_dialogs()

                for chat in chats:
                    try:
                        if chat.title == search_title:

                            messages = telegram_client.get_messages(entity=chat, limit=100)
                            for message in messages:
                                if message and (message.id not in past_messages_id):
                                    try:
                                        found_keywords = find_keywords(message)
                                        if found_keywords:
                                            keyword_str = ", ".join(found_keywords)
                                            message_text = f"{message.text}\n\n"
                                            message_text += f"Пользователь: ({message.sender.username}), {message.sender.first_name}\nГруппа: "
                                            message_text += f"<a href='https://t.me/{chat.title.replace(' ', '_')}'>{chat.title}</a>\n"
                                            message_text += f"Ключ: {keyword_str}\n"
                                            message_text += f"<a href='https://t.me/{chat.title.replace(' ', '_')}/{message.id}'>Оригинал сообщения</a>"

                                            past_messages_id.append(message.id)

                                            telegram_client.send_message(int(group_id), message_text, parse_mode='HTML')
                                            if message.sender.username:
                                                r.connect()
                                                print(r.send_message(message=account.deal_hi_message,
                                                               username=message.sender.username))

                                                # amo.execute_filling(fields={'Ключ поиска': keyword_str,
                                                #                                 'Сообщение': message.text,
                                                #                             'Ссылка на сообщение': f"https://t.me/{chat.title.replace(' ', '_')}/{message.id}",
                                                #                             'Беседа': f"https://t.me/{chat.title.replace(' ', '_')}"
                                                #                             },
                                                #                    fio=message.sender.username)




                                    except Exception as e:
                                        print(f"Error processing {chat.title}: {e}")

                    except:
                        print("messages get error")
            telegram_client.disconnect()

if __name__ == '__main__':
    main()
