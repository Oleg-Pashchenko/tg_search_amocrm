from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import os
import dotenv

dotenv.load_dotenv()

Base = declarative_base()


class TgSearchAccounts(Base):
    __tablename__ = 'TgSearchAccounts'

    id = Column(Integer, primary_key=True)
    radist_api_key = Column(String)
    radist_connection_id = Column(Integer)
    amo_login = Column(String)
    amo_host = Column(String)
    amo_password = Column(String)
    deal_hi_message = Column(String, default="Привет")

    search_words = relationship('SearchWords', back_populates='owner')
    telegram_chats = relationship('TelegramChats', back_populates='owner')


class SearchWords(Base):
    __tablename__ = 'SearchWords'

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('TgSearchAccounts.id'))
    word = Column(String)
    enabled = Column(Boolean)

    owner = relationship('TgSearchAccounts', back_populates='search_words')


class TelegramChats(Base):
    __tablename__ = 'TelegramChats'

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('TgSearchAccounts.id'))
    chat_id = Column(Integer)
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

def add_search_account(radist_api_key, amo_login, amo_host, amo_password, hi_message):
    account = TgSearchAccounts(radist_api_key=radist_api_key, amo_login=amo_login, amo_host=amo_host,
                               amo_password=amo_password, deal_hi_message=hi_message)
    session.add(account)
    session.commit()
    return account


def add_search_word(owner_id, word, enabled=True):
    search_account = session.query(TgSearchAccounts).filter_by(id=owner_id).first()
    if search_account:
        search_word = SearchWords(owner_id=owner_id, word=word, enabled=enabled)
        session.add(search_word)
        session.commit()
        return search_word
    else:
        return None


def add_telegram_chat(owner_id, chat_id, chat_name, enabled=True):
    search_account = session.query(TgSearchAccounts).filter_by(id=owner_id).first()
    if search_account:
        telegram_chat = TelegramChats(owner_id=owner_id, chat_id=chat_id, chat_name=chat_name, enabled=enabled)
        session.add(telegram_chat)
        session.commit()
        return telegram_chat
    else:
        return None


def delete_search_word(word_id):
    search_word = session.query(SearchWords).filter_by(id=word_id).first()
    if search_word:
        session.delete(search_word)
        session.commit()
        return True
    else:
        return False


def edit_search_word_enable_status(word_id, new_status):
    search_word = session.query(SearchWords).filter_by(id=word_id).first()
    if search_word:
        search_word.enabled = new_status
        session.commit()
        return True
    else:
        return False


def edit_telegram_chat_enable_status(chat_id, new_status):
    telegram_chat = session.query(TelegramChats).filter_by(id=chat_id).first()
    if telegram_chat:
        telegram_chat.enabled = new_status
        session.commit()
        return True
    else:
        return False
