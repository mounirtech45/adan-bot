import os
import asyncio

from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped

# ==========================
# إعدادات البوت والـ API
# ==========================
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = 1866851228          # ضع هنا الـ ID الخاص بك
GROUP_ID = -1002556293948      # ضع هنا ID الجروب الصوتي

# ==========================
# تهيئة Pyrogram و PyTgCalls
# ==========================
app = Client("radio", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call = PyTgCalls(app)

playing = False   # حالة التشغيل

# ==========================
# أمر التشغيل
# ==========================
@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("play"))
async def play(client, message):
    global playing

    if len(message.command) < 2:
        await message.reply("❌ أرسل رابط التشغيل بعد الأمر.")
        return

    link = message.command[1]

    try:
        await call.join_group_call(
            GROUP_ID,
            AudioPiped(link)
        )
        playing = True
        await message.reply("✅ تم التشغيل!")
    except Exception as e:
        await message.reply(f"❌ حدث خطأ أثناء التشغيل:\n{e}")

# ==========================
# أمر الإيقاف
# ==========================
@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("stop"))
async def stop(client, message):
    global playing

    try:
        await call.leave_group_call(GROUP_ID)
        playing = False
        await message.reply("⏹ تم الإيقاف!")
    except Exception as e:
        await message.reply(f"❌ حدث خطأ أثناء الإيقاف:\n{e}")

# ==========================
# أمر الحالة
# ==========================
@app.on_message(filters.private & filters.user(OWNER_ID) & filters.command("status"))
async def status(client, message):
    if playing:
        await message.reply("▶ الراديو يعمل الآن")
    else:
        await message.reply("⏹ الراديو متوقف")

# ==========================
# بدء البوت والـ PyTgCalls
# ==========================
app.start()
call.start()

print("✅ البوت بدأ بنجاح")

# تشغيل لوب asyncio للحفاظ على البوت يعمل
asyncio.get_event_loop().run_forever()