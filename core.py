from discord.ext import commands


class JungleClient(commands.Bot):
    def __init__(self, command_prefix) -> None:
        """
        Конструктор JungleClient
        :param command_prefix: префикс бота, для того, чтобы его вызывать
        """
        super().__init__(command_prefix=command_prefix)

    async def on_ready(self) -> None:
        """
        Функция запускается, когда бот готов к работе на сервере
        :return: None
        """
        print('Logged on as {0}'.format(self.user))
