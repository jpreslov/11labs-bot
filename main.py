import io
import os
import tempfile
import subprocess

import nextcord
from datetime import datetime
from dotenv import load_dotenv
from elevenlabs import Voice, VoiceSettings, voices, generate, set_api_key
from nextcord.ext import commands, tasks

from pydub import AudioSegment

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

set_api_key(ELEVENLABS_API_KEY)

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

    await ctx.response.send_message(embed=embed, ephemeral=True)


@bot.slash_command(name="gen", description="Generate audio from voice models")
async def gen(ctx: nextcord.Interaction, voice_name, prompt, stability=0.5, style=0.6):
    await ctx.response.defer(ephemeral=True)
    await ctx.send("Cooking that up for you", ephemeral=True, delete_after=3)

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


@bot.slash_command(name="vcgen", description="Generate audio and play it in VC")
async def vcgen(
    ctx: nextcord.Interaction, voice_name, prompt, stability=0.5, style=0.6
):
    await ctx.response.defer(ephemeral=True)

    if ctx.user.voice is None:
        return await ctx.send("You are not in a voice channel", ephemeral=True)

    selected_voice = [v for v in voice_list if v.name == voice_name]
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

        voice_channel = ctx.user.voice.channel

        if ctx.guild.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.guild.voice_client.move_to(voice_channel)

        with tempfile.NamedTemporaryFile(
            suffix=".wav", delete=False
        ) as wav_f, tempfile.NamedTemporaryFile(suffix=".opus", delete=False) as opus_f:
            wav_f.write(audio)
            wav_f.flush()
            subprocess.check_call(["ffmpeg", "-y", "-i", wav_f.name, opus_f.name])
            source = nextcord.FFmpegOpusAudio(opus_f.name)

            ctx.guild.voice_client.play(source=source)

    except Exception as e:
        print(f"{e}")
        await ctx.send(f"Error: {str(e)}", ephemeral=True)
        return await ctx.guild.voice_client.disconnect(force=True)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await sync_commands.start()
    print(f"{bot.commands}")


bot.run(DISCORD_TOKEN)
