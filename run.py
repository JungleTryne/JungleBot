import os

from core import JungleClient
from secret import BOT_TOKEN
from BotCogs import greeting, admin


absolute_path = os.path.dirname(os.path.abspath(__file__))

modules = [
    greeting,
    admin,
]

if __name__ == '__main__':
    bot = JungleClient('j.')

    for module in modules:
        module.setup(bot)

    bot.run(BOT_TOKEN)
