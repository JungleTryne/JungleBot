from core import JungleClient

from secret import BOT_TOKEN

from BotCogs.greeting import Greetings
import discord
from discord.ext import commands

if __name__ == '__main__':
    bot = JungleClient('.')
    bot.add_cog(Greetings(bot))
    bot.run(BOT_TOKEN)
