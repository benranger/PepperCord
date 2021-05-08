from bot import bot, activeConfigManager
from tools.managers import extensionManager
from art import tprint

activeExtensionManager = extensionManager(bot)

@bot.event
async def on_ready():
  tprint('PepperCord', font = 'xsans')
  print(f'Logged in as {bot.user.name} ({bot.user.id})')

if __name__ == '__main__':
  print(activeExtensionManager.loadExtension())
  print(activeExtensionManager.listExtensions())
  bot.run(activeConfigManager.readKey('discord.api.token'))
