import os
import asyncio
from flask import Flask
from threading import Thread
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream

# --- إعداد Port وهمي لإرضاء منصة Render ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is Running!"

def run_web():
    web_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# --- إعداد البوت ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
OWNER_ID = int(os.getenv("OWNER_ID"))

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("play"))
async def play_audio(_, message):
    if len(message.command) < 2:
        return await message.reply("❌ أرسل الرابط بعد الأمر.")
    
    link = message.command[1]
    msg = await message.reply("⏳ جاري محاولة التشغيل...")
    
    try:
        await call_py.play(
            GROUP_ID,
            MediaStream(link)
        )
        await msg.edit("✅ تم التشغيل في الاتصال المرئي!")
    except Exception as e:
        await msg.edit(f"❌ خطأ:\n{e}")

@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("stop"))
async def stop_audio(_, message):
    try:
        await call_py.leave_call(GROUP_ID)
        await message.reply("⏹ تم إيقاف التشغيل.")
    except Exception as e:
        await message.reply(f"❌ لا يوجد تشغيل حالي أو حدث خطأ: {e}")

async def start_bot():
    await app.start()
    await call_py.start()
    print("--- BOT STARTED SUCCESSFULLY ---")
    await asyncio.Event().wait()

if __name__ == "__main__":
    # تشغيل السيرفر الوهمي في خلفية منفصلة
    Thread(target=run_web).start()
    # تشغيل البوت
    asyncio.run(start_bot())
