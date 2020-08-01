import asyncio
import discord
import json

from discord.ext import commands
from UserBase.utils import UserRecord, get_user_history_by_id


class AdminCog(commands.Cog):
    def __init__(self, bot) -> None:
        """
        Cog for admin commands
        :param bot: bot object
        """
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await ctx.channel.send(error)

    @commands.command()
    @commands.has_any_role("Admin", "Moderator")
    async def warn(self, ctx, members: commands.Greedy[discord.Member], *, reason: str = None):
        """
        Command for user warning
        :param ctx: command context
        :param members: list of the users
        :param reason: reason
        :return: None
        """
        if reason is None:
            reason = "For being a jerk"
        if not members:
            return
        for member in members:
            if self.bot.user == member:
                continue

            user_record = UserRecord(member, ctx.guild)
            user_record.set_warn(reason)

            await member.send("You have been warned: {0}".format(reason))
            await ctx.send("{0.mention} has been warned *{1}*".format(member, reason))
            await self.stats_impl(ctx, member)

    @warn.error
    async def warn_handler(self, ctx, what):
        """
         Exception handler for warn command
         :param ctx: exception context
         :param what: exception text
         :return: None
         """
        print("warn_handler: {0}".format(what))
        await ctx.channel.send("User not found or internal error occurred")

    @commands.command()
    @commands.has_any_role("Admin", "Moderator")
    async def mute(self, ctx, members: commands.Greedy[discord.Member],
                   duration: int = 0, *,
                   reason: str = None):
        """
        Mute command
        :param ctx: command context
        :param members: list of the users
        :param duration: mute duration
        :param reason: mute reason
        :return: None
        """

        if reason is None:
            reason = "For being a jerk"
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        if not members:
            await ctx.send("No idea who to mute :)")

        for member in members:
            if self.bot.user == member:
                continue
            user_record = UserRecord(member, ctx.guild)
            user_record.set_mute(duration, reason)

            await member.add_roles(muted_role, reason=reason)
            await member.edit(voice_channel=None)  # Kick the
            await member.send("You have been muted for {0} minutes. Reason: {1}".format(duration, reason))
            await ctx.send("{0.mention} has been muted for *{1}*".format(member, reason))

        if duration > 0:
            await asyncio.sleep(duration * 60)  # if during the mute you give another mute then the second mute won't work
            for member in members:
                await member.remove_roles(muted_role, reason="Mute time elapsed")

    @mute.error
    async def mute_handler(self, ctx, what):
        """
         Mute command exception handler
         :param ctx: command context
         :param what: exception text
         :return: None
         """
        print("mute_handler: {0}".format(what))
        await ctx.channel.send("User not found or internal error occurred")

    @commands.command()
    @commands.has_any_role("Admin", "Moderator")
    async def unmute(self, ctx, members: commands.Greedy[discord.Member]):
        """
        Unmute command
        :param ctx: command context
        :param members: list of users to unmute
        :return: None
        """
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        for member in members:
            await member.remove_roles(muted_role, reason="unmuted my staff member")

    @commands.command()
    @commands.has_any_role("Admin")
    async def clear_stats(self, ctx, user: discord.User):
        """
        Clear statistics command
        :param ctx: command context
        :param user: user object
        :return: None
        """
        user_record = UserRecord(user, ctx.guild)
        user_record.clear_history()
        await ctx.channel.send("User statistics has been cleared")
        await self.stats_impl(ctx, user)

    @clear_stats.error
    async def clear_stats_handler(self, ctx, what):
        """
        clear stats command exception handler
        :param ctx: command context
        :param what: exception text
        :return: None
        """
        print("clear_stats_handler: {0}".format(what))
        await ctx.channel.send("User not found or internal error occurred")

    @staticmethod
    async def stats_impl(ctx, user: discord.User):
        """
        statistic command implementation
        :param ctx: command context
        :param user: user object
        :return: None
        """
        user_record = UserRecord(user, ctx.guild)

        prettified_view = json.dumps(user_record.history, indent=2, sort_keys=True, ensure_ascii=False)
        await ctx.channel.send("```json\n{0}```".format(prettified_view))

    @commands.command()
    @commands.has_any_role("Admin", "Moderator")
    async def stats(self, ctx, user: discord.User):
        """
        
        :param ctx: command context
        :param user: user object
        :return: None
        """
        await self.stats_impl(ctx, user)

    @stats.error
    async def stats_handler(self, ctx, error):
        """
        stats command exception handler
        :param ctx: command context
        :param error: exception text
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
        """
        Note command
        :param ctx: command context
        :param members: members list
        :param note: note text
        :return: None
        """
        for member in members:
            if self.bot.user == member:
                continue
            user_record = UserRecord(member, ctx.guild)
            user_record.set_note(note)
            await self.stats_impl(ctx, member)

    @note.error
    async def note_handler(self, ctx, error):
        """
        note command exception handler
        :param ctx: command context
        :param error: error text
        :return: None
        """
        print("note_handler: {0}".format(error))
        await ctx.channel.send("User not found or internal error occurred")

    async def ban_impl(self, ctx, user: discord.User, reason: str = None):
        """
        Ban command implementation
        :param ctx: command context
        :param user: user object
        :param reason: ban reason
        :return: None
        """
        if reason is None:
            reason = "For being a jerk!"

        if user == self.bot.user:
            return

        user_record = UserRecord(user, ctx.guild)
        user_record.set_ban(reason)

        message = "You have been banned: {0}".format(reason)
        await user.send(message)
        await ctx.guild.ban(user, reason=reason)
        await ctx.channel.send("User {0} has been banned".format(user))

    @commands.command()
    @commands.has_role("Admin")
    async def ban(self, ctx, user: discord.User, *, reason: str = None):
        """
        ban command
        :param user: user object
        :param ctx: command context
        :param reason: ban reason
        :return: None
        """
        await self.ban_impl(ctx, user, reason)
        await self.stats_impl(ctx, user)

    @ban.error
    async def ban_handler(self, ctx, error):
        """
        Exception handler of ban
        :param ctx: command context
        :param error: exception text
        :return: None
        """
        print("ban_handler: {0}".format(error))
        await ctx.channel.send("User not found or internal error occurred")

    @staticmethod
    async def unban_impl(ctx, user_id):
        """
        implementation of unban command
        :param ctx: command context
        :param user_id: discord user id
        :return: None
        """
        ban_list = await ctx.guild.bans()
        for ban_entry in ban_list:
            if str(ban_entry.user.id) == str(user_id):
                await ctx.guild.unban(ban_entry.user)
                await ban_entry.user.send("You have been unbanned!")
                await ctx.send("User {0} has been unbanned!".format(ban_entry.user.mention))

    @commands.command()
    @commands.has_role("Admin")
    async def unban(self, ctx, user_id):
        """
        Unban command
        :param user_id: discord id
        :param ctx: command context
        :return: None
        """
        await self.unban_impl(ctx, user_id)

    @unban.error
    async def unban_handler(self, ctx, error):
        """
        Exception handler of unban
        :param ctx: command context
        :param error: exception text
        :return: None
        """
        print("unban_handler: {0}".format(error))
        await ctx.channel.send("User not found or internal error occurred")

    @commands.command()
    @commands.has_role("Admin")
    async def soft_ban(self, ctx, user: discord.User, *, reason: str = None):
        """
        Softban - ban and instand unban
        :param ctx: command context
        :param user: user object
        :param reason: softban reason
        :return: None
        """
        await self.ban_impl(ctx, user, reason)
        await self.unban_impl(ctx, user.id)

    @soft_ban.error
    async def soft_ban_handler(self, ctx, error):
        """
        Exception handler of soft_ban
        :param ctx: command context
        :param error: exception text
        :return: None
        """
        print("soft_ban_handler: {0}".format(error))
        await ctx.channel.send("User not found or internal error occurred")

    @commands.command()
    @commands.has_any_role("Admin", "Moderator")
    async def prune_until(self, ctx, message_id: str = None):
        """
        Delete all the messages in the chat until the message with [message_id]
        :param ctx: command context
        :param message_id: message id to delete until
        :return: None
        """
        channel = ctx.channel
        messages = await channel.history().flatten()
        for message in messages:
            this_id = str(message.id)
            await message.delete()
            if this_id == message_id:
                break

    @prune_until.error
    async def prune_until_handler(self, ctx, error):
        """
        Exception handler of prune_until
        :param ctx: command context
        :param error: exception text
        :return: None
        """
        print("prune_until_handler: {0}".format(error))
        await ctx.channel.send("Internal error occurred")

    @commands.command()
    @commands.has_any_role("Admin", "Moderator")
    async def prune(self, ctx, number: int):
        """
        Deletes [number] of messages
        :param ctx: command context
        :param number: number of messages
        :return: None
        """
        channel = ctx.channel
        messages = await channel.history(limit=number+1).flatten()
        for message in messages:
            await message.delete()

    @prune.error
    async def prune_handler(self, ctx, error):
        """
        Exception handler of prune
        :param ctx: command context
        :param error: exception text
        :return: None
        """
        print("prune_handler: {0}".format(error))
        await ctx.channel.send("Internal error occurred")

    @commands.command()
    @commands.has_any_role("Admin", "Moderator")
    async def clear_record(self, ctx, user: discord.User, *, time_of_record: str):
        """
        Delete record or note by the time of record/note
        :param ctx: command context
        :param user: user object
        :param time_of_record: time
        :return: None
        """
        user_record = UserRecord(user, ctx.guild)
        user_record.clear_record(time_of_record)
        await self.stats_impl(ctx, user)

    @clear_record.error
    async def clear_record_handler(self, ctx, error):
        """
         Exception handler of clear_record
         :param ctx: command context
         :param error: exception text
         :return: None
         """
        print("clear_record_handler: {0}".format(error))
        await ctx.channel.send("Internal error occurred")


def setup(bot):
    """
    Bot setup. Activates admin cog
    :param bot: bot object
    :return: None
    """
    bot.add_cog(AdminCog(bot))
