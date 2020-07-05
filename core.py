import discord


class JungleClient(discord.Client):
    async def on_ready(self):
        """
        Функция запускается, когда бот готов к работе на сервере
        :return: None
        """
        print('Logged on as {0}'.format(self.user))

    @staticmethod
    async def on_message(message):
        """
        Функция вызывается, если на сервере отправили сообщение
        :param message: сообщение от какого-то пользователя
        :return: None
        """
        print('Message from {0.author} : {0.content}'.format(message))
