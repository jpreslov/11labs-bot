import io
import asyncio
from datetime import datetime, timedelta
import os

import nextcord
from nextcord.ext import commands, tasks
from dotenv import load_dotenv
from elevenlabs import Voice, VoiceSettings, voices, generate, set_api_key

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ELEVENLABS_TOKEN = os.getenv("ELEVENLABS_TOKEN")

print(f"{DISCORD_TOKEN}")

set_api_key(ELEVENLABS_TOKEN)

intents = nextcord.Intents.default()
# intents.sync_commands = True
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
# bot = commands.Bot(command_prefix="!", intents=intents, permissions=2184218624)

voice_list = [v for v in voices() if v.category == "cloned"]


@tasks.loop(minutes=30.0)
async def sync_commands():
    print(f"Syncing commands - {datetime.now()}")
    # bot.tree.sync()


class ClonedVoice:
    def __init__(self, id=0, name=""):
        self.id = (id,)
        self.name = name


@bot.slash_command()
async def listvoices(ctx: nextcord.Interaction):
    name_list = []

    for v in voice_list:
        name_list.append(v.name)

    embed = nextcord.Embed(title="Voice List", description=", ".join(name_list))

    # await ctx.response.defer(ephemeral=True)
    await ctx.response.send_message(embed=embed, ephemeral=True)


@bot.slash_command(name="gen", description="Generate audio from voice models")
async def gen(ctx: nextcord.Interaction, voice_name, prompt, stability=0.5, style=0.6):
    await ctx.response.defer(ephemeral=True)
    await ctx.send("Cooking that up for you", ephemeral=True)

    selected_voice = [v for v in voice_list if v.name == voice_name]
    print(selected_voice)

    if selected_voice is None:
        return await ctx.response.send_message(
            f"Voice {voice_name} not found", ephemeral=True
        )

    voice_id = selected_voice[0].voice_id

    try:
        audio = generate(
            text=prompt,
            voice=Voice(
                voice_id=voice_id,
                settings=VoiceSettings(
                    stability=stability,
                    similarity_boost=0.7,
                    style=style,
                    use_speaker_boost=True,
                ),
            ),
            model="eleven_multilingual_v2",
        )

        in_memory_file = io.BytesIO(audio)

        author = ctx.user.mention

        await ctx.send(
            content=f"{author} used /gen: voice_name={voice_name}, prompt={prompt}",
            file=nextcord.File(in_memory_file, filename=voice_name + ".wav"),
        )
    except Exception as e:
        print(e)
        return await ctx.send(f"Error: {str(e)}", ephemeral=True)


@bot.slash_command(name="vcgen", description="Generate audio in VC")
async def vcgen(
    ctx: nextcord.Interaction, voice_name, prompt, stability=0.5, style=0.6
):
    await ctx.response.defer(ephemeral=True, with_message=True)

    if ctx.user.voice is None:
        return await ctx.send("You are not in a voice channel", ephemeral=True)
    selected_voice = [v for v in voice_list if v.name == voice_name]

    if selected_voice is None:
        return await ctx.send(f"Voice {voice_name} not found", ephemeral=True)

    voice_id = selected_voice[0].voice_id

    try:
        audio = generate(
            text=prompt,
            voice=Voice(
                voice_id=voice_id,
                settings=VoiceSettings(
                    stability=stability,
                    similarity_boost=0.7,
                    style=style,
                    use_speaker_boost=True,
                ),
            ),
            model="eleven_multilingual_v2",
        )

        # await ctx.send("Cooking that up for you", ephemeral=True)

        buffer = io.BytesIO(audio)

        audio_source = nextcord.FFmpegOpusAudio(buffer, pipe=True)

        voice_channel = ctx.user.voice.channel

        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)

        ctx.voice_client.play(audio_source)

        # ctx.voice_client.play(source=audio_source,
        #                       after=lambda _: await voice_client.disconnect())

    except Exception as e:
        print(e)
        return await ctx.send(f"Error: {str(e)}", ephemeral=True)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await sync_commands.start()
    print(f"{bot.commands}")


bot.run(DISCORD_TOKEN)
