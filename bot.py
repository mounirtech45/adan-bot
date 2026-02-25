import os
import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputAudioStream
from pytgcalls.types.input_stream import AudioPiped

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
OWNER_ID = int(os.getenv("OWNER_ID"))

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
pytgcalls = PyTgCalls(app)

playing = False

@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("play"))
async def play(_, message):
    global playing
    if len(message.command) < 2:
        await message.reply("❌ أرسل رابط التشغيل بعد الأمر.")
        return
    link = message.command[1]
    try:
        await pytgcalls.join_group_call(
            GROUP_ID,
            AudioPiped(link)
        )
        playing = True
        await message.reply("✅ تم التشغيل!")
    except Exception as e:
        await message.reply(f"❌ حدث خطأ أثناء التشغيل:\n{e}")

@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("stop"))
async def stop(_, message):
    global playing
    try:
        await pytgcalls.leave_group_call(GROUP_ID)
        playing = False
        await message.reply("⏹ تم الإيقاف!")
    except Exception as e:
        await message.reply(f"❌ حدث خطأ أثناء الإيقاف:\n{e}")

@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("status"))
async def status(_, message):
    await message.reply("▶ يعمل" if playing else "⏹ متوقف")

app.start()
pytgcalls.start()
asyncio.get_event_loop().run_forever()