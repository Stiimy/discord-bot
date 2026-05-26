"""
🎵 Module Musique — /play, /stop, /skip, /queue, /np, /volume
Robuste, async, pas de timeout
"""

import discord, asyncio, yt_dlp, functools
from discord.ext import commands
from discord import app_commands
from collections import deque

ytdl_opts = {
    'format': 'bestaudio/best',
    'quiet': True, 'no_warnings': True,
    'extract_flat': False, 'noplaylist': True,
    'source_address': '0.0.0.0'
}
ffmpeg_opts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -b:a 128k'
}

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.now_playing = {}

    async def _join(self, interaction):
        if not interaction.user.voice:
            await interaction.followup.send("❌ Rejoins un salon vocal d'abord !", ephemeral=True)
            return None
        ch = interaction.user.voice.channel
        vc = interaction.guild.voice_client
        if vc:
            if vc.channel != ch:
                await vc.move_to(ch)
            return vc
        else:
            try:
                vc = await ch.connect(timeout=10, reconnect=False)
            except discord.ClientException as e:
                await interaction.followup.send(f"❌ Erreur Discord : `{e}`", ephemeral=True)
                return None
            except asyncio.TimeoutError:
                await interaction.followup.send("❌ Timeout — le serveur vocal ne répond pas", ephemeral=True)
                return None
            except Exception as e:
                await interaction.followup.send(f"❌ Erreur : `{type(e).__name__}: {e}`", ephemeral=True)
                return None
            return vc
        return vc

    async def _extract(self, query):
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
            if not query.startswith('http'):
                query = f"ytsearch:{query}"
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(query, download=False))
            if 'entries' in info:
                info = info['entries'][0]
            return info['title'], info['webpage_url'], info.get('duration', 0), info['url']

    async def _play_next(self, guild_id):
        q = self.queues.get(guild_id, deque())
        if not q:
            self.now_playing.pop(guild_id, None)
            vc = self.bot.get_guild(guild_id).voice_client
            if vc: await vc.disconnect()
            return

        title, audio_url = q.popleft()
        self.now_playing[guild_id] = title

        vc = self.bot.get_guild(guild_id).voice_client
        if not vc: return

        try:
            source = await discord.FFmpegOpusAudio.from_probe(audio_url, **ffmpeg_opts)
        except:
            source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_opts)

        vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(
            self._play_next(guild_id), self.bot.loop))

    @app_commands.command(name="play", description="🎵 Joue une musique (titre ou lien)")
    async def play(self, interaction: discord.Interaction, recherche: str):
        await interaction.response.defer()
        vc = await self._join(interaction)
        if not vc: return

        try:
            title, url, duration, audio_url = await self._extract(recherche)
        except Exception as e:
            await interaction.followup.send(f"❌ Introuvable : {str(e)[:100]}", ephemeral=True)
            return

        gid = interaction.guild_id
        if gid not in self.queues:
            self.queues[gid] = deque()
        self.queues[gid].append((title, audio_url))

        m, s = divmod(duration or 0, 60)
        embed = discord.Embed(title="🎵 Ajouté à la file", description=f"[{title}]({url})", color=0x9B59B6)
        if duration: embed.add_field(name="Durée", value=f"{m}:{s:02d}", inline=True)
        embed.add_field(name="Position", value=str(len(self.queues[gid])), inline=True)
        await interaction.followup.send(embed=embed)

        if not vc.is_playing():
            await self._play_next(gid)

    @app_commands.command(name="skip", description="⏭️ Passe au titre suivant")
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("⏭️ Skippé !")
        else:
            await interaction.response.send_message("❌ Rien en cours", ephemeral=True)

    @app_commands.command(name="stop", description="⏹️ Stop la musique")
    async def stop(self, interaction: discord.Interaction):
        gid = interaction.guild_id
        self.queues.pop(gid, None)
        self.now_playing.pop(gid, None)
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
        await interaction.response.send_message("⏹️ Musique arrêtée !")

    @app_commands.command(name="queue", description="📋 File d'attente")
    async def queue(self, interaction: discord.Interaction):
        q = self.queues.get(interaction.guild_id, deque())
        if not q:
            await interaction.response.send_message("📋 File vide", ephemeral=True)
            return
        txt = f"🎶 **En cours :** {self.now_playing.get(interaction.guild_id, '?')}\n"
        for i, (t, _) in enumerate(q, 1):
            txt += f"{i}. {t}\n"
        await interaction.response.send_message(txt[:2000])

    @app_commands.command(name="np", description="🎶 Titre en cours")
    async def np(self, interaction: discord.Interaction):
        t = self.now_playing.get(interaction.guild_id)
        await interaction.response.send_message(f"🎶 **{t}**" if t else "❌ Rien en cours", ephemeral=not t)


async def setup(bot):
    await bot.add_cog(Music(bot))
