import asyncio

from discord.ext import commands


class LogCog(commands.Cog):
    def __init__(self, bot, listen_channels) -> None:
        """
        Cog для логирования всех действий на сервере
        :param bot: объект бота
        :param listen_channels: список каналов, которые логируем
        """
        self.bot = bot
        self.listen_channels = listen_channels
