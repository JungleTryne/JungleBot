from core import JungleClient
from secret import BOT_TOKEN

from BotCogs import greeting, admin

modules = [
    greeting,
    admin,
]

if __name__ == '__main__':
    bot = JungleClient('.')

    for module in modules:
        module.setup(bot)

    bot.run(BOT_TOKEN)
