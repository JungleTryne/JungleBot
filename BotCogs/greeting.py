from discord.ext import commands


class Greetings(commands.Cog):
    def __init__(self, bot) -> None:
        """
        Cog для приветствия новых пользователей на сервере
        :param bot: объект бота
        """
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member) -> None:
        """
        Функция вызывается, когда member присоединился к сервера
        :param member: объект пользователя
        :return: None
        """
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send('Welcome {0.mention}.'.format(member))
