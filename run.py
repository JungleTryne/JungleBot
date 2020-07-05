from core import JungleClient

from secret import BOT_TOKEN

if __name__ == '__main__':
    client = JungleClient()
    client.run(BOT_TOKEN)
