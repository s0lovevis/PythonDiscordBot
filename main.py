import json
from yandex_music import Client

from bot import YamBot, YamCommands

with open('config.json') as json_file:
    data = json.load(json_file)

DISCORD_TOKEN = data['bot_token']
LOGIN = data['yam_account']['login']
PASSWORD = data['yam_account']['password']

yam_client = Client.fromCredentials(LOGIN, PASSWORD, report_new_fields=False)

bot = YamBot(command_prefix=']', yam_client=yam_client, help_command=None)
bot.add_cog(YamCommands(bot, yam_client))
bot.run(DISCORD_TOKEN)
