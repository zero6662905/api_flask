import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from flask_caching import Cache

load_dotenv(dotenv_path=".env_example")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    DB_NAME = "sqlite:///app.db"
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    MAX_FORM_MEMORY_SIZE = 1024 * 1024  # 1MB
    MAX_FORM_PARTS = 500
    
    CACHE_TYPE = 'simple'  # Тип кешу
    CACHE_DEFAULT_TIMEOUT = 30  # Час очікування кешу в секундах
    CACHE_KEY_PREFIX = 'myapp_' 
    

config = Config()
cache = Cache()


engine = create_engine(
    config.DB_NAME,
    echo=True,
)

# Створення конфігурації сессії на основі патерну Фабрика
Session_db = sessionmaker(bind=engine)


# Декларація базового класу для моделей
# Необхідно для реалізації відношень у ORM
class Base(DeclarativeBase):

    def create_db(self):
        """
        Ініціалізація метаданих,
        створює базу даних, якщо відсутня,
        створює таблиці на основі моделей(що спадкуються від Base),
        якщо жодної немає
        """
        self.metadata.create_all(engine)

    def drop_db(self):
        """
        Деструкція метаданих,
        видаляє базу даних, якщо така наявна,
        видаляє усі таблиці
        """
        self.metadata.drop_all(engine)
