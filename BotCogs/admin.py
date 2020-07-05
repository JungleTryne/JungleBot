import discord
from discord.ext import commands


class AdminCog(commands.Cog):
    def __init__(self, bot) -> None:
        """
        Cog для административных дел на сервере
        :param bot: объект бота
        """
        self.bot = bot

    # TODO: Catch exception of commands.has_role
    @commands.command()
    @commands.has_role("admin")
    async def ban(self, ctx, user: discord.User, *, reason: str = None):
        """
        Команда бана пользователя со сервера
        :param user: Пользователь, которого баним
        :param ctx: Контекст команды
        :param reason: Причина бана
        :return: None
        """

        if reason is None:
            reason = "For being a jerk!"
        message = "Вы были забанены по причине: {0}".format(reason)
        await user.send(message)
        await ctx.guild.ban(user, reason=reason)
        await ctx.channel.send("Пользователь {0} был забанен".format(user))

    @commands.command()
    @commands.has_role("admin")
    async def unban(self, ctx, user_id):
        """
        Команда разбана
        :param user_id: ID пользователя дискорд
        :param ctx: контекстс команды
        :return: None
        """
        ban_list = await ctx.guild.bans()
        for ban_entry in ban_list:
            if str(ban_entry.user.id) == str(user_id):
                await ctx.guild.unban(ban_entry.user)
                await ctx.send("Пользователь {0} разбанен!".format(ban_entry.user.mention))


def setup(bot):
    """
    Функция добавления функциональности Cog к боту
    :param bot: объект бота
    :return: None
    """
    bot.add_cog(AdminCog(bot))
