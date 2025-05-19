import discord
from discord.ext import commands
import yt_dlp
import re

class Music(commands.Cog):
    """Cog com comandos de música básicos, incluindo busca e controles."""

    def __init__(self, bot):
        self.bot = bot
        self.queue = {}  # filas de música por servidor

    @commands.command(name='join')
    async def join(self, ctx):
        """Conecta o bot ao canal de voz do autor."""
        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send(f"Conectado em: **{channel.name}**")
        else:
            await ctx.send("Você precisa estar em um canal de voz primeiro!")

    @commands.command(name='play')
    async def play(self, ctx, *, query: str = None):
        """Reproduz áudio de uma URL do YouTube ou faz busca se não for URL."""
        if query is None:
            return await ctx.send("❌ Você precisa fornecer uma URL ou o nome da música para buscar.")

        is_url = bool(re.match(r'https?://', query))
        search_term = query if is_url else f"ytsearch1:{query}"

        guild_id = ctx.guild.id
        if guild_id not in self.queue:
            self.queue[guild_id] = []

        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if not voice:
            await ctx.invoke(self.join)
            voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if voice.is_playing():
            self.queue[guild_id].append(search_term)
            return await ctx.send(f"✅ Adicionado à fila: {query}")

        def play_source(source_term):
            ytdl_opts = {'format': 'bestaudio', 'noplaylist': True}
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                info = ydl.extract_info(source_term, download=False)
            if not is_url:
                entry = info['entries'][0]
                return entry['url'], entry['title']
            else:
                return info['url'], info.get('title') or info.get('id')

        def after_play(error):
            if self.queue[guild_id]:
                next_term = self.queue[guild_id].pop(0)
                next_url, next_title = play_source(next_term)
                src = discord.FFmpegPCMAudio(next_url)
                voice.play(src, after=after_play)
                self.bot.loop.create_task(ctx.send(f"▶️ Tocando agora: **{next_title}**"))

        url, title = play_source(search_term)
        source = discord.FFmpegPCMAudio(url)
        voice.play(source, after=after_play)
        await ctx.send(f"▶️ Tocando agora: **{title}**")

    @commands.command(name='skip')
    async def skip(self, ctx):
        """Pula a faixa atual e toca a próxima fila."""
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_playing():
            voice.stop()
            await ctx.send("⏭️ Música pulada!")
        else:
            await ctx.send("Nenhuma música está tocando no momento.")

    @commands.command(name='pause')
    async def pause(self, ctx):
        """Pausa a reprodução atual."""
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_playing():
            voice.pause()
            await ctx.send("⏸️ Música pausada.")
        else:
            await ctx.send("Nada tocando para pausar.")

    @commands.command(name='resume')
    async def resume(self, ctx):
        """Retoma uma reprodução pausada."""
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_paused():
            voice.resume()
            await ctx.send("▶️ Música retomada.")
        else:
            await ctx.send("Nada pausado para retomar.")

    @commands.command(name='volume')
    async def volume(self, ctx, vol: int):
        """Ajusta o volume da reprodução (0-100%)."""
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.source:
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = max(0.0, min(vol / 100, 1.0))
            await ctx.send(f"🔊 Volume ajustado para {vol}%")
        else:
            await ctx.send("Nenhuma música tocando para ajustar volume.")

async def setup(bot):
    """Registra este Cog no bot (API v2+)."""
    await bot.add_cog(Music(bot))