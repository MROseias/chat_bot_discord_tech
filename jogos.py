from discord.ext import tasks, commands
import pandas as pd
import discord
import requests
import asyncio


class Jogos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_localized_name(self,appid):
            url_store = f"https://store.steampowered.com/api/appdetails?appids={appid}&l=brazilian"
            response = requests.get(url_store)
            data = response.json()
            if response.status_code == 200 and data[str(appid)]['success']:
                return data[str(appid)]['data']['name']  # The localized name
            else:
                return None

    async def buscar_jogos(self,ctx,jogos_que_achou):   
        jogos="```"
        i=0
        enviou_jogos=False
        for _, row in jogos_que_achou.iterrows():
            appid = row['appid']
            localized_name = await self.get_localized_name(appid)
            print(localized_name)
            if localized_name:
                jogos+=f"\nApp ID: {appid}, Nome do Jogo (PT-BR): {localized_name}"
                print(f"\nApp ID: {appid}, Nome do Jogo (PT-BR): {localized_name}")
                i=i+1
                if(i%10==0):
                    jogos+="\n```"
                    print(jogos)
                    await ctx.send(jogos)
                    jogos="```"
        if(i %10!=0):
            jogos+="\n```"
            print(jogos)
            await ctx.send(jogos)         
        
    @commands.command(help="Esse comando serve para buscar o preço de um jogo na Steam.")
    async def jogo(self,ctx,jogo):    
        if not jogo.isdigit():
            await ctx.send("Vi aqui que você me mandou um nome de jogo, porém eu só consigo buscar promoções a partir de um id. Buscando jogos com nome parecido....")
            url_busca = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
            headers = {
                "accept": "application/json"
            }


            response = requests.get(url_busca, headers=headers)
            data = response.json()
            apps = data['applist']['apps']
            dataframe = pd.DataFrame(apps)

            matching_games = dataframe[dataframe['name'].str.contains(jogo, case=False, na=False)]

            if not matching_games.empty:
                
                await ctx.send("Preparando lista com os Ids dos jogos que eu encontrei: ")
                await self.buscar_jogos(ctx,matching_games)
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

            texto+=f"\n\n{descricao_jogo}\n\n"
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
                msg = await self.bot.wait_for('message', check=check, timeout=30)

                if msg.content.lower() == 'sim':
                    id=jogo
                    nome=await self.get_localized_name(id)
                    dicionario={
                        "id":id,
                        "nome":nome
                    }
                    dataframe=pd.DataFrame([dicionario])
                    dataframe.to_csv("favoritos.csv",mode="a", index=False, header=False)
                    await ctx.send(f'Ok, adicionando **{nome}** aos seus favoritos...')
                else:
                    await ctx.send('Então tá')

            except asyncio.TimeoutError:
                await ctx.send('Vou esperar mais não!')
            print(texto)
            
    