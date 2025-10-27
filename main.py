import discord
#import yt_dlp
from discord.ui import Button, View, Modal, TextInput
from discord.ext import commands


intents = discord.Intents.all()
bot = commands.Bot(".", intents=intents)

@bot.event  # Quando o bot iniciar
async def on_ready():
    print("Bot inicializado com susssesso!")


@bot.command()  # Comando para o bot
async def ola(ctx:commands.Context):
    name = ctx.author.name
    await ctx.send(f"Olá, {name}! Tudo bem?")


@bot.command() # comando para dar cargos ex .cargo (nome do cargo) (usuario)
@commands.has_permissions(manage_roles=True)  # garante que o usuário pode dar cargos
async def cargo(ctx, nome_do_cargo: str, *, nome_do_membro: str):
    # Procura o cargo pelo nome
    cargo = discord.utils.get(ctx.guild.roles, name=nome_do_cargo)
    if cargo is None:
        await ctx.send(f"Cargo `{nome_do_cargo}` não encontrado!")
        return

    # Procura o membro pelo nome ou apelido
    membro = discord.utils.find(
        lambda m: m.name == nome_do_membro or m.display_name == nome_do_membro,
        ctx.guild.members
    )
    if membro is None:
        await ctx.send(f"Membro `{nome_do_membro}` não encontrado!")
        return

    try:
        await membro.add_roles(cargo)
        await ctx.send(f"Cargo `{cargo.name}` adicionado para {membro.mention}!")
    except discord.Forbidden:
        await ctx.send("Eu não tenho permissão para dar esse cargo.")
    except Exception as e:
        await ctx.send(f"Erro: {e}")


@bot.command() # remover todos os cargos ex: .recargoall (usuario)
@commands.has_permissions(manage_roles=True)
async def recargoall(ctx, *, nome_do_membro: str):
    membro = discord.utils.find(
        lambda m: m.name == nome_do_membro or m.display_name == nome_do_membro,
        ctx.guild.members
    )
    if membro is None:
        await ctx.send(f"⚠️ Membro `{nome_do_membro}` não encontrado!")
        return

    # Filtra todos os cargos, exceto o cargo padrão (@everyone)
    cargos_remover = [cargo for cargo in membro.roles if cargo != ctx.guild.default_role]

    if not cargos_remover:
        await ctx.send(f"ℹ️ {membro.mention} não tem cargos para remover.")
        return

    try:
        await membro.remove_roles(*cargos_remover)
        await ctx.send(f"✅ Todos os cargos foram removidos de {membro.mention}!")
    except discord.Forbidden:
        await ctx.send("❌ Eu não tenho permissão para remover os cargos.")
    except Exception as e:
        await ctx.send(f"❌ Erro: {e}")


@bot.command() # remover cargo especifico ex: .remcargo (cargo) (usuario)
@commands.has_permissions(manage_roles=True)
async def remcargo(ctx, nome_do_membro: str, *, nome_do_cargo: str):
    membro = discord.utils.find(
        lambda m: m.name == nome_do_membro or m.display_name == nome_do_membro,
        ctx.guild.members
    )
    if membro is None:
        await ctx.send(f"⚠️ Membro `{nome_do_membro}` não encontrado!")
        return

    cargo = discord.utils.get(ctx.guild.roles, name=nome_do_cargo)
    if cargo is None:
        await ctx.send(f"⚠️ Cargo `{nome_do_cargo}` não encontrado!")
        return

    try:
        await membro.remove_roles(cargo)
        await ctx.send(f"✅ Cargo `{cargo.name}` removido de {membro.mention}!")
    except discord.Forbidden:
        await ctx.send("❌ Eu não tenho permissão para remover esse cargo.")
    except Exception as e:
        await ctx.send(f"❌ Erro: {e}")

# Coloque o ID do cargo que poderá usar os comandos
STAFF_ROLE_ID = 1432368900607049738

# Verificador global para todos os comandos
@bot.check
def is_staff(ctx):
    # Se o autor tiver o cargo de staff, retorna True
    return any(role.id == STAFF_ROLE_ID for role in ctx.author.roles)


# Tratamento de erro quando o usuário não passa no verificador
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send(f"❌ {ctx.author.mention}, você não tem permissão.")
    else:
        raise error  # Mantém os outros erros normais


@bot.command()
async def callme(ctx, member: discord.Member):
    # Verifica se o autor está em um canal de voz
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        await ctx.send("❌ Você precisa estar em um canal de voz para usar este comando.")
        return

    # Verifica se o usuário mencionado está em algum canal de voz
    if member.voice is None or member.voice.channel is None:
        await ctx.send(f"❌ {member.name} não está em nenhum canal de voz.")
        return

    # Move o usuário para o canal do autor
    try:
        await member.move_to(ctx.author.voice.channel)
        await ctx.send(f"✅ {member.name} foi movido para **{ctx.author.voice.channel.name}**!")
    except discord.Forbidden:
        await ctx.send(f"❌ Não tenho permissão para mover {member.name}.")
    except discord.HTTPException:
        await ctx.send(f"❌ Não consegui mover {member.name}.")

@bot.command()
async def listacargos(ctx):
    # Pega todos os cargos do servidor
    cargos = ctx.guild.roles  # retorna uma lista de objetos Role

    # Organiza do cargo mais alto para o mais baixo (opcional)
    cargos_ordenados = sorted(cargos, key=lambda r: r.position, reverse=True)

    # Cria uma string com os nomes dos cargos
    lista = "\n".join([f"{cargo.name} (ID: {cargo.id})" for cargo in cargos_ordenados])

    # Envia a lista
    await ctx.send(f"📋 **Cargos do servidor:**\n{lista}")

# ID do canal específico onde a mensagem será enviada
CANAL_BOAS_VINDAS = 1432379875469033512  # Substitua pelo ID do canal

@bot.event
async def on_member_join(member):
    canal = bot.get_channel(CANAL_BOAS_VINDAS)
    if canal is None:
        return  # Caso o canal não seja encontrado, não faz nada

    # Criando a embed
    embed = discord.Embed(
        title="🎉 Bem-vindo(a) ao servidor!",
        description=f"Olá {member.mention}, seja muito bem-vindo(a)! Esperamos que você aproveite o servidor 😊",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.avatar.url)  # Foto do perfil do usuário
    embed.set_footer(text="Equipe do servidor")  # Mensagem de rodapé (opcional)

    await canal.send(embed=embed)  # Envia a embed no canal específico
"""
# Dicionário para armazenar os players ativos
players = {}

@bot.command() #caixa de música
async def join(ctx):
    if ctx.author.voice is None:
        await ctx.send("Você precisa estar em um canal de voz!")
        return
    canal = ctx.author.voice.channel
    await canal.connect()
    await ctx.send(f"Conectado ao canal {canal.name}!")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Desconectado do canal de voz!")

@bot.command()
async def play(ctx, url):
    if not ctx.voice_client:
        if ctx.author.voice is None:
            await ctx.send("Você precisa estar em um canal de voz!")
            return
        canal = ctx.author.voice.channel
        await canal.connect()
    
    ydl_opts = {
        'format': 'bestaudio',
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']

    source = await discord.FFmpegOpusAudio.from_probe(url2)
    ctx.voice_client.play(source)
    await ctx.send(f"🎵 Tocando: {info['title']}")
"""

# Coloque seu token aqui depois
bot.run("SEU TOKEN")
