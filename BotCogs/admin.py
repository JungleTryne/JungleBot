import asyncio
import discord
import json

from discord.ext import commands
from UserBase.utils import UserRecord, get_user_history_by_id


class AdminCog(commands.Cog):
    def __init__(self, bot) -> None:
        """
        Cog для административных дел на сервере
        :param bot: объект бота
        """
        self.bot = bot

    @commands.command()
    @commands.has_any_role("Admin", "Moderator")
    async def mute(self, ctx, members: commands.Greedy[discord.Member],
                   duration: int = 0, *,
                   reason: str = None):
        """
        Команда мута пользователей на сервере
        :param ctx: контекст команды
        :param members: список пользователей для мута
        :param duration: продолжительность мута в минутах
        :param reason: причина мута
        :return: None
        """

        if reason is None:
            reason = "For being a jerk"
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        if not members:
            await ctx.send("Не смог понять, кого мутить :)")

        for member in members:
            if self.bot.user == member:
                continue
            user_record = UserRecord(member, ctx.guild)
            user_record.set_mute(duration, reason)

            await member.add_roles(muted_role, reason=reason)
            await member.edit(voice_channel=None)  # Кикаем пользователя
            await ctx.send("{0.mention} был замучен за *{1}*".format(member, reason))

        if duration > 0:
            await asyncio.sleep(duration * 60)  # Если во время мута дать еще один мут, то сработает только первый
            for member in members:
                await member.remove_roles(muted_role, reason="Время мута вышло")

    @mute.error
    async def mute_handler(self, ctx, what):
        """
        Обработчик ошибок команды mute
        :param ctx: контекст команды
        :param what: текст ошибки
        :return: None
        """
        print("mute_handler: {0}".format(what))
        await ctx.channel.send("User not found or internal error occurred")

    @commands.command()
    @commands.has_any_role("Admin", "Moderator")
    async def unmute(self, ctx, members: commands.Greedy[discord.Member]):
        """
        Команда размута пользователя сервера
        :param ctx: контекст команды
        :param members: список пользователей для размута
        :return: None
        """
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        for member in members:
            await member.remove_roles(muted_role, reason="Разбанен стафом")

    @commands.command()
    @commands.has_any_role("Admin")
    async def clear_stats(self, ctx, user: discord.User):
        """
        Команда очистки статистики пользователя
        :param ctx: контекст команды
        :param user: объект пользователя
        :return: None
        """
        user_record = UserRecord(user, ctx.guild)
        user_record.clear_history()
        await ctx.channel.send("История пользователя была очищена")

    @clear_stats.error
    async def clear_stats_handler(self, ctx, what):
        """
        Обработчик ошибок команды clear_stats
        :param ctx: контекст команды
        :param what: текст ошибки
        :return: None
        """
        print("clear_stats_handler: {0}".format(what))
        await ctx.channel.send("User not found or internal error occurred")

    @commands.command()
    @commands.has_any_role("Admin", "Moderator")
    async def stats(self, ctx, user: discord.User):
        """
        Команда печатания статистики пользователя
        :param ctx: контекст команды
        :param user: объект пользователя
        :return: None
        """
        user_record = UserRecord(user, ctx.guild)

        prettified_view = json.dumps(user_record.history, indent=2, sort_keys=True)
        await ctx.channel.send("```json\n{0}```".format(prettified_view))

    @stats.error
    async def stats_handler(self, ctx, error):
        """
        Локальный обработчик ошибок команды stats.
        :param ctx: контектст команды
        :param error: исключение
        :return: None
        """
        print(error.args)

        if isinstance(error, commands.BadArgument):
            user_id = error.args[0].split()[1][1:-1]
            history = get_user_history_by_id(ctx.guild, user_id)
            if not history:
                await ctx.channel.send("User Not Found")
                return
            prettified_view = json.dumps(history, indent=2, sort_keys=True)
            await ctx.channel.send("```{0}```".format(prettified_view))

    @commands.command()
    @commands.has_any_role("Admin", "Moderator")
    async def note(self, ctx, members: commands.Greedy[discord.Member], *, note: str = None):
        for member in members:
            if self.bot.user == member:
                continue
            user_record = UserRecord(member, ctx.guild)
            user_record.set_note(note)

    @note.error
    async def note_handler(self, ctx, error):
        """
        Обработчик ошибок команды note
        :param ctx: контекст команды
        :param error: текст ошибки
        :return: None
        """
        print("note_handler: {0}".format(error))
        await ctx.channel.send("User not found or internal error occurred")

    @commands.command()
    @commands.has_role("Admin")
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

        user_record = UserRecord(user, ctx.guild)
        user_record.set_ban(reason)

        message = "Вы были забанены по причине: {0}".format(reason)
        await user.send(message)
        await ctx.guild.ban(user, reason=reason)
        await ctx.channel.send("Пользователь {0} был забанен".format(user))

    @ban.error
    async def ban_handler(self, ctx, error):
        print("ban_handler: {0}".format(error))
        await ctx.channel.send("User not found or internal error occurred")

    @commands.command()
    @commands.has_role("Admin")
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

    @unban.error
    async def unban_handler(self, ctx, error):
        print("unban_handler: {0}".format(error))
        await ctx.channel.send("User not found or internal error occurred")


def setup(bot):
    """
    Функция добавления функциональности Cog к боту
    :param bot: объект бота
    :return: None
    """
    bot.add_cog(AdminCog(bot))
