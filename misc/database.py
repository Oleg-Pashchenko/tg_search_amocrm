from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import os
import dotenv

dotenv.load_dotenv()

Base = declarative_base()


class TgSearchAccounts(Base):
    __tablename__ = 'TgSearchAccounts'

    id = Column(Integer, primary_key=True)
    email = Column(String)
    password = Column(String)

    radist_api_key = Column(String)
    radist_connection_id = Column(Integer)
    amo_login = Column(String)
    amo_host = Column(String)
    amo_password = Column(String)
    deal_hi_message = Column(String, default="Привет")
    link_to_telegram_channel = Column(String, default="")
    search_words = Column(String, default="")

    telegram_chats = relationship('TelegramChats', back_populates='owner')


class TelegramChats(Base):
    __tablename__ = 'TelegramChats'

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('TgSearchAccounts.id'))
    chat_id = Column(BigInteger)
    chat_name = Column(String)
    enabled = Column(Boolean)

    owner = relationship('TgSearchAccounts', back_populates='telegram_chats')


# Database setup
engine = create_engine(f'postgresql://{os.getenv("DB_LOGIN")}:{os.getenv("DB_PASSWORD")}'
                       f'@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}', echo=True)
Base.metadata.create_all(bind=engine)

# Session setup
Session = sessionmaker(bind=engine)
session = Session()


# Methods to interact with the database

def add_search_account(radist_api_key, radist_connection_id, amo_login, amo_host, amo_password, hi_message, email,
                       password):
    account = TgSearchAccounts(radist_api_key=radist_api_key, radist_connection_id=radist_connection_id,
                               amo_login=amo_login, amo_host=amo_host,
                               amo_password=amo_password, deal_hi_message=hi_message, email=email, password=password)
    session.add(account)
    session.commit()
    return account


def add_telegram_chat(owner_id, chat_id, chat_name, enabled=True):
    search_account = session.query(TgSearchAccounts).filter_by(id=owner_id).first()
    if search_account:
        telegram_chat = TelegramChats(owner_id=owner_id, chat_id=chat_id, chat_name=chat_name, enabled=enabled)
        session.add(telegram_chat)
        session.commit()
        return telegram_chat
    else:
        return None


def edit_telegram_chat_enable_status(chat_id, new_status):
    telegram_chat = session.query(TelegramChats).filter_by(id=chat_id).first()
    if telegram_chat:
        telegram_chat.enabled = new_status
        session.commit()
        return True
    else:
        return False


def get_username_status(username: str):
    telegram_account = session.query(TgSearchAccounts).filter_by(email=username).one_or_none()
    return telegram_account is not None


def auth_correct(username: str, password: str) -> bool:
    telegram_account = session.query(TgSearchAccounts).filter_by(email=username, password=password).one_or_none()
    return telegram_account is not None


def get_user(username: str) -> bool:
    telegram_account = session.query(TgSearchAccounts).filter_by(email=username).first()
    return telegram_account


def get_chats_by_user(user_id: int):
    telegram_chats = session.query(TelegramChats).order_by(TelegramChats.enabled).filter_by(owner_id=user_id).all()
    return telegram_chats[::-1]


def disable_chats_by_user_id(user_id: int):
    chats = get_chats_by_user(user_id)
    for chat in chats:
        chat.enabled = False
        session.add(chat)
    session.commit()


def enable_chat(chat_id: int):
    chat = session.query(TelegramChats).filter_by(chat_id=chat_id).first()
    chat.enabled = True
    session.add(chat)
    session.commit()


def update_search_info(keywords, hi_message, account_to_post, user_id: int):
    telegram_account = session.query(TgSearchAccounts).filter_by(id=user_id).first()
    telegram_account.deal_hi_message = hi_message.strip()
    telegram_account.link_to_telegram_channel = account_to_post.strip()
    telegram_account.search_words = keywords.strip()
    session.add(telegram_account)
    session.commit()


def get_search_info(user_id: int):
    telegram_account = session.query(TgSearchAccounts).filter_by(id=user_id).first()
    return telegram_account
