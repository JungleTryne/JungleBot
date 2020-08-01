from discord.ext import commands


class Greetings(commands.Cog):
    def __init__(self, bot) -> None:
        """
        Cog welcoming new users
        :param bot: bot object
        """
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member) -> None:
        """
        Function is called on new member join event
        :param member: new user object
        :return: None
        """
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send('Welcome {0.mention}.'.format(member))


def setup(bot):
    """
    Bot setup. Activates greeting cog
    :param bot: bot object
    :return: None
    """
    bot.add_cog(Greetings(bot))
