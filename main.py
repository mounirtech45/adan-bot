import os
import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped

# المتغيرات
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
OWNER_ID = int(os.getenv("OWNER_ID"))

app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

@app.on_message(filters.user(OWNER_ID) & filters.command("play"))
async def play_audio(_, message):
    if len(message.command) < 2:
        return await message.reply("❌ أرسل الرابط")
    
    link = message.command[1]
    msg = await message.reply("⏳ جاري التشغيل...")
    try:
        await call_py.join_group_call(
            GROUP_ID,
            AudioPiped(link)
        )
        await msg.edit("✅ تم التشغيل بنجاح")
    except Exception as e:
        await msg.edit(f"❌ خطأ: {e}")

@app.on_message(filters.user(OWNER_ID) & filters.command("stop"))
async def stop_audio(_, message):
    try:
        await call_py.leave_group_call(GROUP_ID)
        await message.reply("⏹ توقف")
    except:
        pass

async def main():
    await app.start()
    await call_py.start()
    print("STARTED")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
