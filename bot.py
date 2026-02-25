import os
import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream

# جلب المتغيرات من البيئة
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
OWNER_ID = int(os.getenv("OWNER_ID"))

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("play"))
async def play(_, message):
    if len(message.command) < 2:
        return await message.reply("❌ أرسل رابط التشغيل بعد الأمر.")
    
    link = message.command[1]
    msg = await message.reply("⏳ جاري محاولة التشغيل...")
    
    try:
        await call_py.play(
            GROUP_ID,
            MediaStream(link)
        )
        await msg.edit("✅ تم التشغيل بنجاح في المجموعة!")
    except Exception as e:
        await msg.edit(f"❌ حدث خطأ أثناء التشغيل:\n{e}")

@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("stop"))
async def stop(_, message):
    try:
        await call_py.leave_call(GROUP_ID)
        await message.reply("⏹ تم الإيقاف والمغادرة!")
    except Exception as e:
        await message.reply(f"❌ خطأ عند محاولة الإيقاف: {e}")

async def main():
    await app.start()
    await call_py.start()
    print("Bot is online and ready!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
