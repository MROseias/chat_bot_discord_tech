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

bot = commands.Bot(command_prefix='!', intents=intents)

async def get_localized_name(appid):
            url_store = f"https://store.steampowered.com/api/appdetails?appids={appid}&l=brazilian"
            response = requests.get(url_store)
            data = response.json()
            if response.status_code == 200 and data[str(appid)]['success']:
                return data[str(appid)]['data']['name']  # The localized name
            else:
                return None

async def buscar_jogos(jogos_que_achou):   
    jogos="```"
    i=0
    for _, row in jogos_que_achou.iterrows():
        appid = row['appid']
        localized_name = await get_localized_name(appid)
        print(localized_name)
        if localized_name:
            jogos+=f"\nApp ID: {appid}, Nome do Jogo (PT-BR): {localized_name}"
            print(f"\nApp ID: {appid}, Nome do Jogo (PT-BR): {localized_name}")
            i=i+1
            if(i==10):
                break
    jogos+="\n```"
    print(jogos)
    return jogos

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    activity = discord.CustomActivity(name="Implore pela minha !ajuda")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    
@bot.command()
async def jogo(ctx,jogo):    
    if not jogo.isdigit():
        await ctx.send("Vi aqui que você me mandou um nome de jogo, porém eu só consigo buscar promoções a partir de um id. Buscando jogos com nome parecido....")
        url_busca = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
        headers = {
            "accept": "application/json"
        }

        # Fetch the list of all apps
        response = requests.get(url_busca, headers=headers)
        data = response.json()
        apps = data['applist']['apps']
        dataframe = pd.DataFrame(apps)

        # Search for games that match the name (case-insensitive)
        matching_games = dataframe[dataframe['name'].str.contains(jogo, case=False, na=False)]
        # Function to get the localized game name (Brazilian Portuguese) from the Steam Store API
        

        # Pretty print the results with localized names (App ID and Localized Game Name)
        if not matching_games.empty:
            
            await ctx.send("Preparando lista com os Ids dos jogos que eu encontrei: ")
            await ctx.send(await buscar_jogos(matching_games))
        else:
            await ctx.send("Não encontrei nenhum jogo :( . Você esqueceu de colocar algum espaço?")

    else: 
        url=f"https://store.steampowered.com/api/appdetails?appids={jogo}&cc=br&l=brazilian"
        headers = {
            "accept": "application/json"
        }
        response = requests.get(url, headers=headers)
        dataframe=pd.read_json(response.text)
        foto=dataframe[int(jogo)]["data"]["capsule_image"].replace("\\",'')
        await ctx.send(foto)
        texto="\n```"
        texto+=f"\nJogo: "+dataframe[int(jogo)]["data"]["name"]
        descricao_jogo=dataframe[int(jogo)]["data"]["short_description"]
        def remove_html_tags(text):
            clean = re.sub(r'<.*?>', '', text)  # Remove HTML tags
            return clean
        texto+=f"\n\n{remove_html_tags(descricao_jogo)}\n\n"
        if "price_overview" in dataframe[int(jogo)]["data"]:
            desconto=dataframe[int(jogo)]["data"]["price_overview"]["discount_percent"]
            if(desconto>0):
                texto+="\nDesconto de "+str(desconto)+" %"
            else:
                texto+="\nSem desconto"
            preco = dataframe[int(jogo)]["data"]["price_overview"]["final_formatted"]
            texto+=f"\nPreço: "+preco
        else: 
            texto+="\nDe graça!!"
        texto+="\n```"
        
        await ctx.send(texto)
        
        salvar = "Deseja favoritar esse jogo nos favoritos ?"
        await ctx.send(salvar)
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        try:
            # Wait for the user's response
            msg = await bot.wait_for('message', check=check, timeout=30)

            if msg.content.lower() == 'sim':
                # Add the game to the user's favorites
                id=jogo
                nome=await get_localized_name(id)
                dicionario={
                    "id":id,
                    "nome":nome
                }
                dataframe=pd.DataFrame([dicionario])
                dataframe.to_csv("favoritos.csv",mode="a", index=False)
                await ctx.send(f'Ok, adicionando **{nome}** aos seus favoritos...')
            else:
                await ctx.send('Então tá')

        except asyncio.TimeoutError:
            await ctx.send('Vou esperar mais não!')
        print(texto)
@bot.command()
async def lista_jogos_favoritos(ctx):
    try:
        favoritos = pd.read_csv('favoritos.csv')
    except FileNotFoundError:
        await ctx.send("Arquivo favoritos.csv não encontrado.")
        return

    jogos = []

    if not favoritos.empty:
        for _, row in favoritos.iterrows():
            jogos.append(f"{row['id']}: {row['nome']}")
        
        await ctx.send("Meus jogos favoritos:\n" + "\n".join(jogos))
    else:
        await ctx.send("Não há jogos favoritos na lista.")

# Adicionando um comando para ajudar
@bot.command()
async def favoritos(ctx):
    await ctx.send("Use !lista_jogos_favoritos para ver a lista de jogos favoritos.")

bot.run('MTIyODAwODk3MzUwNTEzODc2OQ.GNbZPf.lTMtGZJLc4zjkTbs-ETnQOZF01SBdTkcNgDHhw')


