from typing import Optional

import discord
import json

from datetime import datetime

from run import absolute_path


# TODO: Бот может быть использован на нескольких серверах!!

def save_data(func):
    """
    Декоратор сохранения изменений данных пользователя функцией func
    :param func: декорируемая функция
    :return: декорированная функия
    """

    def decorated(self, *args):
        func(self, *args)
        save_user_history(self.user, self.history)

    return decorated


def get_user_history(user: discord.User) -> Optional[dict]:
    """
    Функция получения словаря-статистики пользователя на сервере
    :param user: объект пользователя
    :return: его история
    """
    with open(absolute_path + '/JsonBases/db.json', 'r') as json_file:
        data = json.load(json_file)
    if str(user.id) not in data:
        return None
    return data[str(user.id)]


def get_user_history_by_id(user_id: str) -> Optional[dict]:
    """
    Функция получения словария-статистики пользователя на сервере по его DiscordID
    требуется в случае того, что пользователь, например, был забанен на сервере и
    discord.py не способен распарсить его ID
    :param user_id: ID пользователя
    :return: None
    """
    with open(absolute_path + '/JsonBases/db.json', 'r') as json_file:
        data = json.load(json_file)
    if user_id not in data:
        return None
    return data[user_id]


def save_user_history(user: discord.User, history: dict) -> None:
    """
    Сохранение статистики пользователя
    :param user: объект пользователя
    :param history: его история
    :return: None
    """
    with open(absolute_path + '/JsonBases/db.json', 'r') as json_file:
        data = json.load(json_file)

    data[str(user.id)] = history

    with open(absolute_path + '/JsonBases/db.json', 'w') as json_file:
        json.dump(data, json_file)


class UserRecord:
    def __init__(self, user: discord.User):
        """
        Класс-обёртка для сохрания логов
        Сохраняем все действия модераторов и администраторов:
        баны, кики, муты, заметки
        """
        self.user = user
        self.history = get_user_history(self.user)

        if not self.history:
            self.generate_history()

    @save_data
    def generate_history(self):
        """
        Функция генерации истории пользователя, если она пуста
        :return: None
        """
        self.history = dict()
        self.history["id"] = self.user.id
        self.history["name"] = self.user.name
        self.history["notes"] = []
        self.history["records"] = []

    @save_data
    def set_mute(self, duration, reason):
        """
        Функция создает запись в базе данных в случае, если пользователь замьючен
        :param duration: продолжительность (в минутах)
        :param reason: причина мута
        :return: None
        """
        mute = dict()
        mute['record_type'] = 'mute'
        mute['duration'] = duration
        mute['reason'] = reason
        mute['time'] = datetime.now()
        self.history['records'].append(mute)

    @save_data
    def set_ban(self, reason):
        """
        Функция создает запись в базе данных в случае, если пользователь забанен
        :param reason: причина бана
        :return: None
        """
        ban = dict()
        ban['record_type'] = 'ban'
        ban['reason'] = reason
        ban['time'] = str(datetime.now())
        self.history['records'].append(ban)
