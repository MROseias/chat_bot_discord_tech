from discord.ext import tasks, commands
import pandas as pd
import discord
import requests
import asyncio


class Favoritos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.verificar_descontos.start()
        
    def cog_unload(self):
        self.verificar_descontos.cancel()
    
    @commands.command()
    async def desfavoritar(self,ctx,id):
        df= pd.read_csv('favoritos.csv')
        print(df)
        print(id)
        if(not id.isdigit()):
            await ctx.send("Só sou capaz de remover por id!!!")
            return
        id=int(id)
        
        df = df[df['id'] != id]
        df.to_csv('favoritos.csv', mode='w',index=False)
        await ctx.send("Jogo removido.")
        
    
    @commands.command()
    async def favoritos(self,ctx):
        await ctx.send("Use !lista_jogos_favoritos para ver a lista de jogos favoritos do servidor.")
        
    @commands.command(help="Esse comando lista os jogos favoritados.")
    async def lista_jogos_favoritos(self,ctx):
        try:
            favoritos = pd.read_csv('favoritos.csv')
        except FileNotFoundError:
            print("Arquivo favoritos.csv não encontrado, criando.")
            with open("favoritos.csv", "w") as arquivo:
                arquivo.write("id,nomeid\n")
            return

        jogos = "```\nid, nome\n"

        if not favoritos.empty:
            for _, row in favoritos.iterrows():
                jogos+=f"{row['id']}: {row['nomeid']}\n"
            jogos+="\n```"
            await ctx.send("Jogos favoritos:\n\n"+jogos)
        else:
            await ctx.send("Não há jogos favoritos na lista.")
            
    @tasks.loop(hours=6.0)
    async def verificar_descontos(self):
        print("começando o loop")
        try:
            favoritos = pd.read_csv('favoritos.csv')
        except FileNotFoundError:
            print("Arquivo favoritos.csv não encontrado, criando.")
            with open("favoritos.csv", "w") as arquivo:
                arquivo.write("id,nomeid\n")            
            return
        except Exception :
            print()

        jogos = favoritos.to_dict(orient='records')

        for jogo in jogos:
            jogo_id = jogo['id']
            response = requests.get(f'https://store.steampowered.com/api/appdetails?appids={jogo_id}&cc=br')
            dados = response.json()
            if dados[str(jogo_id)]['success']:
                detalhes = dados[str(jogo_id)]['data']
                if 'price_overview' in detalhes:
                    preco_original = detalhes['price_overview']['final_formatted']
                    preco_com_desconto = detalhes['price_overview']['discount_percent']
                    imagem_jogo = detalhes.get('header_image', '')

                    if preco_com_desconto > 0:
                        embed = discord.Embed(title=detalhes['name'], color=discord.Color.green())
                        embed.add_field(name="Preço Original", value=preco_original, inline=False)
                        embed.add_field(name="Desconto", value=f"{preco_com_desconto}%", inline=False)
                        embed.set_image(url=imagem_jogo)  # Adiciona a imagem do jogo
                        channel=self.bot.get_channel(1296108836436049961)                 
                        print(embed)   
                        await channel.send(embed=embed)