import discord
from discord.ext import commands
import random
import os
intents = discord.Intents.default()
intents.message_content = True
import pandas as pd
import requests
import re
import asyncio
import time
from jogos import Jogos
from listar_favoritos import Favoritos
from pretty_help import EmojiMenu, PrettyHelp

bot = commands.Bot(command_prefix='!', intents=intents)
menu = EmojiMenu('◀️', '▶️', '❌') # You can copy-paste any icons you want.
bot.help_command = PrettyHelp(navigation=menu, color=discord.Colour.green()) 

# Adicionando um comando para ajudar
# async def agendar_verificacoes(ctx):
#     while True:
#         await verificar_descontos(ctx)
#         await asyncio.sleep(30000)

@bot.event
async def on_ready():
    print(f'{bot.user} está online!')
    for guild in bot.guilds:  # Para cada guilda em que o bot está
        channel = guild.text_channels[0]  # Escolha um canal (ou modifique conforme necessário)
        # asyncio.create_task(agendar_verificacoes(channel))
    await bot.add_cog(Jogos(bot))
    await bot.add_cog(Favoritos(bot))
bot.run()


