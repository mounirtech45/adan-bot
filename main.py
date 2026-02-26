import os
import asyncio
from pyrogram import Client, filters

# استيراد مرن جداً لتجنب ImportError
try:
    from pytgcalls import PyTgCalls
    from pytgcalls.types import AudioPiped
except ImportError:
    # محاولة الاستيراد من المسار البديل في الإصدارات التجريبية
    try:
        from pytgcalls.pytgcalls import PyTgCalls
        from pytgcalls.types.input_stream import AudioPiped
    except:
        # إذا فشل كل شيء، سنحاول الوصول للكلاس مباشرة
        import pytgcalls
        PyTgCalls = pytgcalls.PyTgCalls
        AudioPiped = pytgcalls.types.AudioPiped

# إحضار البيانات
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
        return await message.reply("❌ أرسل الرابط")
    
    link = message.command[1]
    msg = await message.reply("⏳ جاري التشغيل...")
    
    try:
        await call_py.play(
            GROUP_ID,
            AudioPiped(link)
        )
        await msg.edit("✅ تم التشغيل")
    except Exception as e:
        await msg.edit(f"❌ خطأ: {e}")

@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("stop"))
async def stop(_, message):
    try:
        await call_py.leave_call(GROUP_ID)
        await message.reply("⏹ توقف")
    except:
        pass

async def main():
    await app.start()
    await call_py.start()
    print("STARTED SUCCESSFULLY")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
