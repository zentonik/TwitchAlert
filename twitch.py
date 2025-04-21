import discord
import asyncio
import aiohttp
import re

# ===CONFIG===
DISCORD_TOKEN = "TOKEN" # | change token
STREAMER_NAME = "jynxzi"  # | you can change, default streamer
CHANNEL_ID = "ID" # | change

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

is_live = False
manual_check = False

async def check_stream():
    global is_live, manual_check
    streamer_name_lower = STREAMER_NAME.lower()
    url = f"https://www.twitch.tv/{streamer_name_lower}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            html = await resp.text()

    live_check = re.search(r'"isLiveBroadcast":(true|false)', html)

    if live_check:
        currently_live = live_check.group(1) == "true"
        if currently_live and not is_live:
            is_live = True
            if not manual_check:
                await send_live_alert()
        elif not currently_live:
            is_live = False

async def send_live_alert():
    channel = client.get_channel(int(CHANNEL_ID))
    if channel:
        await channel.send(f" @here 🔴 **{STREAMER_NAME} is LIVE!**\nWatch here: https://twitch.tv/{STREAMER_NAME}")

@client.event
async def on_message(message):
    global STREAMER_NAME, is_live, manual_check
    if message.author == client.user:
        return

    if message.content.lower() == "!check":
        if is_live:
            await message.channel.send(f"@here ✅ **{STREAMER_NAME} is LIVE!**\nWatch here: https://twitch.tv/{STREAMER_NAME}")
        else:
            await message.channel.send(f"❌ **{STREAMER_NAME} is NOT live right now.**")

    elif message.content.lower().startswith("!setstreamer"):
        new_streamer = message.content.split(" ", 1)[1] if len(message.content.split(" ", 1)) > 1 else None
        if new_streamer:
            STREAMER_NAME = new_streamer
            is_live = False
            manual_check = True
            initial_message = await message.channel.send(f"Now monitoring **{STREAMER_NAME}**. Checking if they are live...")

            await check_stream()

            if is_live:
                await message.channel.send(f"✅ **{STREAMER_NAME} is LIVE!**\nWatch here: https://twitch.tv/{STREAMER_NAME}")
            else:
                await message.channel.send(f"❌ **{STREAMER_NAME} is NOT live right now.**")

            await asyncio.sleep(3)
            await initial_message.delete()

            manual_check = False
        else:
            await message.channel.send("Please provide a streamer name after `!setstreamer`.")

async def live_check_loop():
    await client.wait_until_ready()
    while not client.is_closed():
        await check_stream()
        await asyncio.sleep(5)

@client.event
async def on_ready():
    print(f'Logged in as: {client.user}')
    client.loop.create_task(live_check_loop())

client.run(DISCORD_TOKEN)
