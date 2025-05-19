import os
import discord
import asyncio
from discord.ext import commands

# --------------------
# Configuração do Bot
# --------------------
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix='!',
    help_command=commands.MinimalHelpCommand(),
    intents=intents
)

# --------------------
# Eventos Base
# --------------------
@bot.event
async def on_ready():
    print(f'Bot {bot.user} conectado e pronto!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send(f"❌ Ocorreu um erro: `{error.original}`")
    else:
        await ctx.send(f"❌ Erro: `{error}`")

# --------------------
# Função para carregar Cogs
# --------------------
async def load_cogs():
    """Carrega todas as extensões da pasta cogs/ aguardando cada load_extension."""
    if not os.path.isdir('./cogs'):
        print("⚠️ Pasta 'cogs/' não encontrada — nenhum comando carregado.")
        return

    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename != '__init__.py':
            ext_name = f"cogs.{filename[:-3]}"
            try:
                # Agora aguardamos a coroutine load_extension
                await bot.load_extension(ext_name)  
                print(f"✅ Cog carregado: {ext_name}")
            except Exception as e:
                print(f"❌ Falha ao carregar {ext_name}: {e}")

# --------------------
# Função principal
# --------------------
async def main():
    # 1. Carrega os cogs
    await load_cogs()
    # 2. Inicia o bot (usa start em vez de run)
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        raise RuntimeError("❌ Variável de ambiente 'DISCORD_BOT_TOKEN' não definida.")
    await bot.start(token)  

# --------------------
# Ponto de entrada
# --------------------
if __name__ == "__main__":
    # Executa o main() no loop de eventos
    asyncio.run(main())
