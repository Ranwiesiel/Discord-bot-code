import discord
from discord.ext import commands
import logging
import logging.handlers
import os
import requests
import json
import random as rd
import re
import asyncio
import youtube_dl
from keep_alive import keep_alive

youtube_dl.utils.bug_repports_message = lambda: ''


ytdl_format_options= {
  'fromat': 'bestaudio/best',
  'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
  'restrictfilenames': True,
  'noplaylist': True,
  'nocheckercertificate': True,
  'ignoreerrors': False,
  'logostderr': False,
  'no_warnings': True,
  'default_search': 'auto',
  'source_address': '0.0.0.0'
}

ffmpeg_options= {
  'options': '-vn',
}

ytdl= youtube_dl.YoutubeDL(ytdl_format_options)


#isi youtubedl
class YTDLSource(discord.PCMVolumeTransformer):
  def __init__(self, source, *, data, volume=0.5):
    super().__init__(source, volume)
    self.data= data
    self.title= data.get('title')
    self.url= data.get('url')
    
  @classmethod
  async def from_url(cls, url, *, loop=None, stream=False):
    loop= loop or asyncio.get_event.loop()
    data= await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
    
    if 'entries' in data:
      #mengambil item/video pertama dalam playlist
      data= data['entries'][0]
      filename= data['url'] if stream else ytdl.prepare_filename(data)
      return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


#command bot youtube
class Music(commands.Cog):
  def __init__(self, bot):
    self.bot= bot
    
    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
      """Masuk ke voice channel"""
      
      if ctx.voice_client is not None:
        return await ctx.voice_client.move_to(channel)
      await channel.connect()
      
    @commands.command()
    async def play(self, ctx, *, query):
      """Memutar file dari sistem file lokal"""
      
      source= discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
      ctx.voice_client.play(source, after=lambda e: print(f'Pemutar error: {e}') if e else None)
      await ctx.send(f'Sedang diputar: {query}')
      
    @commands.command()
    async def yt(self, ctx, *, url):
      """Memutar dari url (hampir semua YouTube_dl supports)"""
      
      async with ctx.typing():
        player= await YTDLSource.from_url(url, loop=self.bot.loop)
        ctx.voice_client.play(player, after=lambda e: print(f'Pemutar error: {e}' if e else None))
      await ctx.send(f'Sekarang diputar: {player.title}')
      
    @commands.command()
    async def stream(self, ctx, *, url):
      """Streaming dari url (sama seperti yt, tapi tidak didownload)"""
      
      async with ctx.typing():
        player= await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        ctx.voice_client.play(player, after=lambda e: print(f'Pemutar error: {e}' if e else None))
      await ctx.send(f'Sekarang diputar: {player.title}')
      
    @commands.command()
    async def volume(self, ctx, volume: int):
      """Mengatur volume"""
      
      if ctx.voice_client is None:
        return await ctx.send("Tidak terhubung ke voice channel.")
      ctx.voice_client.source.volume= volume / 100
      await ctx.send(f'Volume diubah ke {volume}%')
      
    @commands.command()
    async def stop(self, ctx):
      """Berhenti dan keluar dari channel"""
      await ctx.voice_client.disconnect()
      
    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
      if ctx.voice_client is None:
        if ctx.author.voice:
          await ctx.author.voice.channel.connect()
        else:
          await ctx.send("Anda tidak dalam voice channel.")
          raise commands.commandError("Pembuat tidak dalam voice channel.")
      elif ctx.voice_client.is_playing():
        ctx.voice_client.stop()


#ambil pesan quote
def get_quote():
  response= requests.get("https://animechan.xyz/api/random")
  json_data= json.loads(response.text)
  anime, karakter, quote= json_data["anime"], json_data["character"], json_data["quote"]
  return f'''```
Anime    : {anime}
Karakter : {karakter}
Quote    : "{quote}"```'''


intents = discord.Intents.default()
intents.message_content = True
intents.members= True

bot = commands.Bot(commands.when_mentioned_or('$'), intents=intents)

guild_id = .guild.id
@bot.slash_command(name="first_slash", guild_ids=[...]) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def first_slash(ctx): 
    await ctx.respond("You executed")

#basic autoreply
my_secret = os.environ['Bot']
@bot.event
async def on_ready():
  print(f"{bot.user.name} ID: {bot.user.id} Siap digunakan!")
  await bot.add_cog(Music(bot))
  for guild in bot.guilds:
    print(guild.id)



@bot.command()
#isi_pesan= pesan.content
async def hi(ctx):
  await ctx.send("haii!")

@bot.command()
async def ping(ctx):
  await ctx.send('pong')

@bot.command()
async def quote(ctx):
  quote = get_quote()
  await ctx.send(quote)




#logger
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)



#keep_alive()
bot.run(my_secret, log_handler=None)
