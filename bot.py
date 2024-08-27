from elevenlabs import play, save
from elevenlabs.client import ElevenLabs
import discord
import os
import langid
import time
import requests
from dotenv import load_dotenv
load_dotenv()

bot = discord.Bot(intents=discord.Intents.all())


def text_to_voice(text, file_name, service="google"):
    if service == "elevenlabs":
        client = ElevenLabs(
            api_key=os.getenv("API_KEY"),
        )

        audio = client.generate(
            text=text,
            voice="Rachel",
            model="eleven_turbo_v2_5"
        )
        save(audio, file_name)
    elif service=="google":
        r=requests.get(f"https://translate.google.com/translate_tts?ie=UTF-8&total=1&idx=0&textlen=320&client=tw-ob&q={text}&tl={langid.classify(text)[0]}")
        with open(file_name,"wb")as f:
            f.write(r.content)

@bot.event
async def on_ready():
    print(bot.user)


@bot.event
async def on_message(message: discord.Message):
    if message.guild.voice_client:
        if message.author.voice.channel.id == message.channel.id:
            user_name = message.author.global_name or message.author.name
            file_name = f"tmp/{message.channel.id}-{int(time.time())}.mp3"
            text = f"{user_name} 說 {message.content}"
            text_to_voice(text, file_name, os.getenv("SERVICE"))
            vc = message.guild.voice_client
            audio_source = discord.FFmpegPCMAudio(file_name)
            if not vc.is_playing():
                vc.play(audio_source, after=lambda e: os.remove(f"{file_name}"))


@bot.slash_command(name="加入", description="加入語音")
async def join(ctx: discord.ApplicationContext):
    await ctx.defer()

    if ctx.author.voice.channel is not None:
        voice_channel = ctx.author.voice.channel
        if not ctx.voice_client:
            await voice_channel.connect()
        await ctx.respond(f"已加入語音，我會開始轉達<#{ctx.author.voice.channel.id}>裡面的文字頻道!")
    else:
        await ctx.respond(f"請先加入語音")

bot.run(os.getenv("TOKEN"))
