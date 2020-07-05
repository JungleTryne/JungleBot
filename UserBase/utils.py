from typing import Optional

import discord
import json

from run import absolute_path
# TODO: Бот может быть использован на нескольких серверах!!
# TODO: Бага: создает несклько копий одного пользователя


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
    if user.id not in data:
        return None
    return data[user.id]


def save_user_history(user: discord.User, history: dict) -> None:
    """
    Сохранение статистики пользователя
    :param user: объект пользователя
    :param history: его история
    :return: None
    """
    with open(absolute_path + '/JsonBases/db.json', 'r') as json_file:
        data = json.load(json_file)

    data[user.id] = history

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
        self.history["notes"] = {}
        self.history["records"] = {}
