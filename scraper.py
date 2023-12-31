import os
import time

from telethon.sync import TelegramClient
from telethon.tl.patched import Message
from misc import database
from script_core import amocrm, radist

messages_history = {}


def create_telegram_client(session_name, api_id, api_hash):
    client = TelegramClient(session_name, int(api_id), api_hash)
    client.start()
    return client


def main():
    while True:
        start = time.time()
        accounts = database.get_all_accounts()
        for id, account in enumerate(accounts):
            print(id + 1, '/', len(accounts), ':', account.session_name + ".session")
            if not os.path.exists(account.session_name + ".session"):
                continue

            if account.session_name not in messages_history.keys():
                messages_history[account.session_name] = {}

            s = time.time()
            telegram_client = create_telegram_client(
                account.session_name, account.api_id, account.api_hash
            )
            print('Telegram connect time:', time.time() - s)

            keywords = account.search_words.split(",")
            search_groups = database.get_all_enabled_chats_by_user_id(account.id)
            for search_group in search_groups:
                search_title = search_group.chat_name
                group_id = account.link_to_telegram_channel

                def find_keywords(mess):
                    founded_keywords = [
                        keyword
                        for keyword in keywords
                        if keyword.lower().strip() in mess.text.lower().strip()
                    ]
                    return founded_keywords
                s = time.time()
                chats = telegram_client.get_dialogs()
                print('Get dialogs time:', time.time() - s)
                for chat in chats:
                    try:
                        if chat.title == search_title:
                            s = time.time()
                            messages = telegram_client.get_messages(
                                entity=chat, limit=100
                            )
                            print('Get messages time:', time.time() - s)
                            for message in messages:
                                message: Message = message
                                if (
                                        chat.title
                                        in messages_history[account.session_name].keys()
                                        and messages_history[account.session_name][
                                    chat.title
                                ]
                                        >= message.date
                                ):
                                    continue

                                messages_history[account.session_name] = {
                                    chat.title: message.date
                                }

                                if message:
                                    if not isinstance(message, Message):
                                        continue
                                    try:
                                        found_keywords = find_keywords(message)
                                        if found_keywords:
                                            print("Найдено сообщение!")
                                            keyword_str = ", ".join(found_keywords)
                                            message_text = f"{message.text}\n\n"

                                            try:
                                                first_name = message.sender.first_name
                                            except:
                                                first_name = "-"

                                            message_text += f"Пользователь: ({message.sender.username}), {first_name}\nГруппа: "
                                            # message_text += f"<a href='https://t.me/{chat.title.replace(' ', '_')}'>{chat.title}</a>\n"
                                            message_text += f"Ключ: {keyword_str}\n"
                                            # message_text += f"<a href='https://t.me/{chat.title.replace(' ', '_')}/{message.id}'>Оригинал сообщения</a>"
                                            if chat.entity.username:
                                                message_text += f"<a href='https://t.me/{chat.entity.username}'>{chat.title}</a>\n"
                                                message_text += f"<a href='https://t.me/{chat.entity.username}/{message.id}'>Оригинал сообщения</a>"
                                            else:
                                                message_text += f"<a href='https://web.telegram.org/a/#{chat.id}'>{chat.title}</a>\n"
                                                message_text += f"<a href='https://web.telegram.org/a/#{chat.id}/{message.id}'>Оригинал сообщения</a>"
                                            time.sleep(1)
                                            telegram_client.send_message(
                                                int(group_id),
                                                message_text,
                                                parse_mode="HTML",
                                            )

                                    except Exception as e:
                                        print(f"Error processing {chat.title}: {e}")

                    except:
                        print("messages get error")
            s = time.time()
            telegram_client.disconnect()
            print('Disconnect time', time.time() - s)
        print('Execution time:', time.time() - start)


if __name__ == "__main__":
    main()
