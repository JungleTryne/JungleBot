from core import JungleClient
from secret import BOT_TOKEN

from BotCogs import greeting, admin

if __name__ == '__main__':
    bot = JungleClient('.')
    greeting.setup(bot)
    admin.setup(bot)

    bot.run(BOT_TOKEN)
